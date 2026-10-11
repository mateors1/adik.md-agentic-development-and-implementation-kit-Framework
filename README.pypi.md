# ADIK MCP server

Optional MCP access to ADIK, a producer skill suite for generating **SDK code plus
matching implementation skills, contracts, examples and context** as one adik.
The developer's coding agent executes generation. A consumer's agent uses the
finished bundle to integrate that SDK into application code.

Install `adik-mcp-server` and run it from the producer repository or consumer
application root. Producer workflows require the deployed ADIK toolkit. The wheel
contains the MCP server and shared contracts module; it does not contain the
producer skills or a generated SDK.

```sh
adik-mcp-server --transport stdio
```

Tools query and validate the registry, report status, and return generation or
implementation instructions. `adik_implement` accepts a relative path to a completed
bundle, such as `.adik/hello`, validates it, and returns its implementation
skill paths. The calling agent performs code edits and tests. Vector search remains
an optional, unimplemented extension.

For producer bootstrap, bundle generation, consumer registration and the runnable
reference, see the [repository documentation](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework).
