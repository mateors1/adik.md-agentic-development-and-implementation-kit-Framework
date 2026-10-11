---
name: implement-hello
description: Implement the bundled Hello SDK in a Python application to greet users. Use for greeting integration, input validation, and handling blank or invalid names.
metadata:
  sdk-version: 1.0.0
---

# Implement Hello

This skill and the SDK in `../../sdk/python/` are one release, version 1.0.0.
Read [capabilities](references/capabilities.md) for `fn:greet` and
[the example](assets/example.py) before selecting the integration point.
The canonical producer contract is `../../contracts/registry.json`.

1. Confirm the application uses Python 3.10 or newer. Inspect its dependency
   manifest and the function, route, or command where the user requested greetings.
2. Copy `<bundle-root>/sdk/python/` into a temporary build directory outside the
   sealed bundle. Install that copy using the application's package manager, for
   example `python -m pip install <temporary-sdk-copy>`. This installs actual SDK
   code while keeping package-manager artifacts out of the sealed bundle.
3. Import `greet` from `hello_sdk` at the selected integration point and call it
   with the application's user name. Reuse the application's error-handling conventions.
4. Map `ValueError` for blank input and `TypeError` for non-string input as appropriate.
   This SDK has no authentication, network I/O, persistent state, retries, or cleanup.
5. Run the example and the application's relevant checks. Verify whitespace trimming,
   Unicode names, and blank-input handling. Report actual commands and outcomes.

Application edits are authorized by the user's implementation request. Preserve
unrelated application code and the bundled producer contract. The producer source
repository is not needed to implement this adik.
