# Optional ADIK MCP interface

Version 2.0.0 (proposed). Run from the producer repository or consumer app root:

```sh
python3 mcp/adik_mcp_server.py --transport stdio
```

The installed `adik-mcp-server` entry point exposes the same interface. The wheel
includes shared contract code; generation skills come from producer deployment.

| Tool | Behavior |
|---|---|
| `adik_get_registry` | Read canonical JSON or normalized legacy Markdown, with optional section/filter. |
| `adik_get_symbol` | Look up a stable ID or exact name. |
| `adik_validate_registry` | Shared structural validation; FAIL blocks build instructions. |
| `adik_build_sdk` | Return instructions to generate SDK code and matching agentic elements as one adik. |
| `adik_scaffold_boilerplate` | Compatibility name for producer implementation-kit generation instructions. |
| `adik_analyse_codebase` | Return producer analysis instructions. |
| `adik_implement` | Validate a completed bundle and return implementation skill paths for the consumer agent. |
| `adik_get_build_report` | Read existing producer reports. |
| `adik_status` | Report registry status, completed bundle presence and installed registrations. |
| `adik_lint` | Run the deployed framework document linter. |
| `adik_embed` | Run producer context registration. Consumer bundles use `adik-bundle.py install`. |
| `adik_eject` | Run receipt-based producer toolkit removal. |
| `adik_vector_search` | Return extension status; a vector backend is not implemented here. |

Resources: `adik://registry`, `adik://config`, `adik://env`, `adik://orchestrator`.

READY means that the host agent has a handoff to execute. It does not mean code
was generated, integrated, tested or published. No model runner is required.
Keep HTTP transport private to your trusted development environment; stdio is the
default. Consumer installation and package dependency installation are separate steps.
