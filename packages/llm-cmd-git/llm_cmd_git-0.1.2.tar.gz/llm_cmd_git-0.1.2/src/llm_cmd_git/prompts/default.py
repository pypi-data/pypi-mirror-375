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
<short description>

<long description>

<footer>
</template>

{SHORT_DESCRIPTION}

{LONG_DESCRIPTION}

{FOOTER}

### Full Examples

#### Simple and trivial changes example:
Add contribution guidelines

#### When user context is empty or doesn't mention specific tickets/issues:
Add social login via Google

Implement OAuth2 integration for Google authentication

#### When user context mentions specific tickets/issues:
Prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.Remove timeouts
which were used to mitigate the racing issue but are obsolete now.

Fixes #328

{OUTPUT_FORMAT}
"""
