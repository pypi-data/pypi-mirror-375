import llm
from click import Group

from .cli import cli as git_commands


@llm.hookimpl
def register_commands(cli: Group):
    """
    Registers the 'git' command group with the provided Click CLI group.

    Args:
        cli (Group): The Click command group to which the 'git' commands will be added.
    """
    cli.add_command(git_commands, "git")
