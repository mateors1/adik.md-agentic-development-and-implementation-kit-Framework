# Greeting capability

| Need | Symbol | Recipe |
|---|---|---|
| Greet a user | `fn:greet` / `hello_sdk.greet` | Pass a string; render the returned greeting |
| Handle blank input | `fn:greet` | Catch `ValueError`; use the application's validation response |

`greet(" Ada ")` returns `"Hello, Ada!"`. Unicode names are preserved. Empty and
whitespace-only strings raise `ValueError`; non-string values raise `TypeError`.
No environment variables or credentials are required. Supported consumers: Python
3.10+. Web-framework response mappings belong to the consumer application.
