# adik-mcp-server

MCP server for the **ADIK** (Agentic Development and Implementation Kit) framework.

Exposes SDK generation, registry queries, codebase analysis, and project management tools via the [Model Context Protocol](https://modelcontextprotocol.io), making ADIK capabilities available to any MCP-compatible AI agent — Claude Desktop, VS Code Copilot, Cursor, Windsurf, and more.

## Installation

```bash
pip install adik-mcp-server
```

## Quick Start

### Claude Desktop / VS Code Copilot / Cursor (stdio)

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "adik": {
      "command": "adik-mcp-server"
    }
  }
}
```

### HTTP Transport

```bash
adik-mcp-server --transport http --port 3100
```

### Python module

```bash
python -m adik_mcp_server
python -m adik_mcp_server --transport http --port 3100
```

## How It Works

The server runs inside any directory containing an ADIK project (identified by `ADIK.md` or `Registry.md`). It walks up from `cwd` to find the project root automatically.

**Deterministic tools** (registry reads, validation, linting, status) execute immediately and return results. **LLM-dependent tools** (SDK generation, codebase analysis, boilerplate scaffolding) return structured instruction payloads that the calling AI agent should execute — they assemble context and point to the right agent/skill files.

## Tools

| Tool | Type | Description |
|------|------|-------------|
| `adik_get_registry` | Deterministic | Read the full symbol registry or a filtered section |
| `adik_get_symbol` | Deterministic | Look up a specific symbol by ID or name |
| `adik_get_build_report` | Deterministic | Get the latest SDK build report |
| `adik_validate_registry` | Deterministic | Run structural validation on Registry.md |
| `adik_lint` | Deterministic | Lint ADIK specification files |
| `adik_embed` | Deterministic | Manage ADIK self-embedding in project files |
| `adik_eject` | Deterministic | Remove ADIK from a project (dry-run by default) |
| `adik_status` | Deterministic | Full project state summary |
| `adik_build_sdk` | LLM-dependent | Trigger SDK generation via the Builder Agent |
| `adik_analyse_codebase` | LLM-dependent | Trigger codebase analysis via the Codebase Analyst |
| `adik_scaffold_boilerplate` | LLM-dependent | Generate framework-specific implementation boilerplate |
| `adik_vector_search` | Conditional | Semantic search (requires active vector mode) |

## Resources

| URI | Description |
|-----|-------------|
| `adik://registry` | Full Registry.md contents |
| `adik://config` | adik.config.json |
| `adik://env` | adik.env.json |
| `adik://orchestrator` | ADIK.orchestrator.md |

## What is ADIK?

ADIK replaces hand-maintained SDKs with **adiks** — self-sustaining agentic SDK bundles. An adik is a complete deliverable: cooperating AI agents that read your source code, build a symbol registry, generate publish-ready SDK packages (TypeScript, Python, C#, with optional Go/Java/Kotlin), produce framework-idiomatic boilerplate, and self-embed into your AI tools — so your SDKs stay in sync on every commit, automatically.

- [ADIK Framework Repository](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework)
- [Quickstart Guide](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/docs/getting-started/quickstart-guide.md)
- [Manifesto](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/docs/specification/manifesto.md)

## License

Apache License 2.0 — see [LICENSE](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/LICENSE) for details.
