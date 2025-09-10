from .common import (
    FOOTER,
    LONG_DESCRIPTION,
    OUTPUT_FORMAT,
    SHORT_DESCRIPTION,
    SYSTEM_INSTRUCTIONS,
)

SYSTEM_PROMPT = f"""
{SYSTEM_INSTRUCTIONS}

## Instructions
Commit message should have following structure:

<template>
<type>(<scope>): <short description>

<long description>

<footer>
</template>

### Type  (Required)
- feat: New feature addition
- fix: Bug fix that resolves an issue
- docs: Documentation-only changes
- style: Formatting, missing semi-colons, etc (no code logic change)
- refactor: Code refactoring that neither fixes nor adds features
- perf: Performance improvements
- test: Adding missing tests or correcting existing tests
- chore: Maintenance tasks (dependencies, config files)
- build: Affects build system/external dependencies
- ci: CI configuration changes
- revert: Revert previous commits

### Scope (Optional)
- Specify code section/component being modified

{SHORT_DESCRIPTION}

{LONG_DESCRIPTION}

{FOOTER}

### Breaking Changes (Optional)
- Add to footer Only if breaking changes were introduced
- Mark with "!" after type/scope, e.ge. `feat(api)!: remove deprecated endpoints`
- Include migration instructions in body/footer

### Full Examples

#### Simple and trivial changes example:
docs(readme): Add contribution guidelines

#### When user context is empty or doesn't mention specific tickets/issues:
feat(auth): Add social login via Google

Implement OAuth2 integration for Google authentication

#### When Changes introduce breaking changes:
chore!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.

#### When user context mentions specific tickets/issues:
fix(web): Prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Fixes #328

{OUTPUT_FORMAT}
"""
