import inspect
import re
from typing import Any, Callable, Literal

import llm
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from . import git
from .prompts import common, conventional, default, odoo

# Module-level detection of repository-local toml files. Keep these outside the
# Pydantic settings classes so they are not treated as model fields.
_git_dir = git.get_git_dir()
_GIT_CONFIGS = (
    [_git_dir / ".llm-git.toml", _git_dir / "llm-git.toml"] if _git_dir else []
)


class CommonSettings(BaseSettings):
    """
    CommonSettings manages configuration for LLM (Large Language Model) integration.

    Attributes:
        model (str | None): Name of the LLM model to use.
        key (str | None): API key for accessing the LLM model.
        options (dict): Additional options for the LLM model.

    Methods:
        get_llm_model() -> llm.Model:
            Returns an instance of the configured LLM model, setting the API key if required.
    """

    model: str | None = Field(default=None, description="Model name")
    key: str | None = Field(default=None, description="Model API Key")
    options: dict = Field(default={}, description="Model options")

    def get_llm_model(self) -> llm.Model:
        """
        Retrieve and configure the LLM model instance.

        Returns:
            llm.Model: An instance of the LLM model specified by self.model.

        Raises:
            llm.ModelNotFoundError: If the specified model cannot be found.
            llm.KeyError: If a required API key is missing or invalid.
        """
        model = llm.get_model(self.model)
        if model.needs_key:
            model.key = llm.get_key(self.key, model.needs_key, model.key_env_var)
        return model

    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_prefix="llm_git_",
        pyproject_toml_table_header=("tool", "llm-git"),
        toml_file=[
            ".llm-git.toml",
            "llm-git.toml",
            *_GIT_CONFIGS,
            llm.user_dir() / "llm-git.toml",
        ],
        nested_model_default_partial_update=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            PyprojectTomlConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls),
        )


class CommitSettings(CommonSettings):
    """
    CommitSettings manages configuration for generating commit messages using
    different presets and custom prompts.

    Attributes:
        preset (Literal["default", "conventional", "odoo"]):
            Commit message style preset. Determines which system prompt template
            to use.
        system_prompt_custom (str | None):
            Custom system prompt string. If set, overrides the preset system
            prompt.
        user_prompt_template (str | None):
            Custom user prompt template. If set, overrides the default user
            prompt.
        extra_context (str | None):
            Additional context to be included in the prompt.
        edit (bool):
            Whether to open an editor for manual editing of the generated commit
            message.

    Properties:
        system_prompt (str):
            Returns the system prompt string based on the current settings. Uses
            the custom prompt if provided, otherwise selects a preset prompt.
        user_prompt (str):
            Returns the user prompt template, falling back to the default if not
            set.

    Methods:
        generate_commit_message(
            diff: str,
            stream_callback: Callable[[str], Any] | None = None
        ) -> str:
            Generates a commit message based on the provided diff and current
            settings. Supports streaming output via callback.
        finalize(message: str) -> str:
            Extracts and returns the commit message from the model's response,
            using <message> tags as delimiters.
    """

    preset: Literal["default", "conventional", "odoo"] = Field(
        default="default", description="Commit message style preset"
    )
    system_prompt_custom: str | None = Field(
        default=None,
        description="Custom prompt to overrides preset system prompt",
    )
    user_prompt_template: str | None = Field(
        default=None,
        description="Custom user prompt",
    )
    extra_context: str | None = Field(
        default=None, description="Extra context added to the prompt"
    )
    edit: bool = Field(
        default=True,
        description="Open editor to edit the generated commit message",
    )

    @property
    def system_prompt(self):
        """
        Returns the system prompt string based on the current settings.

        If a custom system prompt is set (`self.system_prompt_custom`), it is returned.
        Otherwise, selects a preset system prompt based on the value of `self.preset`:
        - "conventional": returns the conventional system prompt.
        - "odoo": returns the odoo system prompt.
        - Any other value: returns the default system prompt.

        Returns:
            str: The selected system prompt string.
        """
        if self.system_prompt_custom:
            return self.system_prompt_custom

        match self.preset:
            case "conventional":
                return conventional.SYSTEM_PROMPT
            case "odoo":
                return odoo.SYSTEM_PROMPT
            case _:
                return default.SYSTEM_PROMPT

    @property
    def user_prompt(self):
        """
        Returns the user prompt string.

        If a custom user prompt template is set, it returns that template.
        Otherwise, it returns the default user prompt from the common module.

        Returns:
            str: The user prompt string.
        """
        return self.user_prompt_template or common.USER_PROMPT

    def generate_commit_message(
        self,
        diff: str,
        stream_callback: Callable[[str], Any] | None = None,
    ) -> str:
        """Generate a commit message from the provided diff.

        Args:
            diff: The diff string representing code changes.
            stream_callback: Optional callback to receive streamed chunks.

        Returns:
            The finalized commit message generated by the LLM model.
        """
        model_obj = self.get_llm_model()
        is_stream = bool(stream_callback)
        context = self.extra_context or "None"
        system_prompt = self.system_prompt
        user_prompt = self.user_prompt.format(diff=diff, context=context)

        response = model_obj.prompt(
            inspect.cleandoc(user_prompt),
            system=inspect.cleandoc(system_prompt),
            stream=is_stream,
            **self.options,
        )

        if is_stream:
            for chunk in response:
                stream_callback(chunk)

        return self.finalize(response.text())

    def finalize(self, message: str) -> str:
        """
        Extracts and returns the content of the last <message>...</message> tag.

        Args:
            message (str): Input string with <message> tags.

        Returns:
            str: Content of the last <message> tag, or empty string if not found.
        """
        matches = re.findall(r"<message>(.+?)</message>", message, re.DOTALL)
        return str(matches[-1]).strip() if matches else ""
