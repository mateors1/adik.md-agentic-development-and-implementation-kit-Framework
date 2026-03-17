# ADIK MCP Server — `mcp/adik-mcp-server.md`

> **Role:** Model Context Protocol Server
> **Type:** MCP Server Definition
> **Invoked by:** External agentic environments in target (consuming) codebases
> **Exposes:** All ADIK capabilities as MCP tools

---

## Purpose

The ADIK MCP Server exposes the capabilities of the Agentic Development and Implementation Kit as a standard [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server. This allows developers consuming the generated SDK to drive ADIK from their own agentic environment — for example, asking their coding agent to regenerate the SDK after a breaking change, query the symbol registry, or scaffold boilerplate for a new integration.

The MCP server acts as the **remote interface** to ADIK. It is optional; teams that only use ADIK from within the source repository do not need it.

---

## Server Metadata

```json
{
  "name": "adik-mcp-server",
  "version": "1.0.0",
  "description": "MCP server exposing ADIK SDK generation, registry query, and boilerplate scaffolding capabilities",
  "protocol": "mcp",
  "transport": ["stdio", "http+sse"],
  "defaultPort": 3100
}
```

---

## Tools

### `adik_get_registry`

Returns the full contents of `Registry.md` or a filtered subset.

**Input schema:**

```json
{
  "type": "object",
  "properties": {
    "section": {
      "type": "string",
      "enum": ["all", "endpoints", "classes", "interfaces", "schemas", "enums", "functions", "errors", "metadata"],
      "default": "all",
      "description": "Which registry section to return"
    },
    "filter": {
      "type": "string",
      "description": "Optional substring filter applied to symbol names"
    }
  }
}
```

**Output:** Markdown string containing the requested registry section(s).

---

### `adik_build_sdk`

Triggers the Builder Agent to generate or regenerate the SDK for one or more languages.

**Input schema:**

```json
{
  "type": "object",
  "required": ["languages"],
  "properties": {
    "languages": {
      "type": "array",
      "items": { "type": "string", "enum": ["typescript", "python", "csharp"] },
      "minItems": 1,
      "description": "Target languages for SDK generation"
    },
    "incremental": {
      "type": "boolean",
      "default": false,
      "description": "If true, only regenerate files for symbols changed since the last build"
    },
    "outputDir": {
      "type": "string",
      "default": "./sdk",
      "description": "Override the output directory for generated SDK packages"
    }
  }
}
```

**Output:** JSON object containing the build report summary (see `sdk/BUILD_REPORT.md`).

---

### `adik_analyse_codebase`

Triggers the Codebase Analyst Agent to scan the source repository and refresh the Registry.

**Input schema:**

```json
{
  "type": "object",
  "properties": {
    "since": {
      "type": "string",
      "description": "Git commit SHA. If provided, only changes since this commit are analysed (incremental mode)"
    },
    "target": {
      "type": "string",
      "default": "./src",
      "description": "Source directory to scan"
    }
  }
}
```

**Output:** JSON object with `{ "symbolsAdded": number, "symbolsUpdated": number, "symbolsDeprecated": number, "projectType": string, "commitSha": string }`.

---

### `adik_scaffold_boilerplate`

Invokes the SDK Consumer Skill to generate consumption boilerplate for a specific language and optional framework.

**Input schema:**

```json
{
  "type": "object",
  "required": ["language"],
  "properties": {
    "language": {
      "type": "string",
      "enum": ["typescript", "python", "csharp"],
      "description": "Target language for the boilerplate"
    },
    "framework": {
      "type": "string",
      "description": "Target framework hint (e.g. 'react', 'nestjs', 'fastapi', 'aspnet', 'angular')"
    },
    "outputDir": {
      "type": "string",
      "description": "Directory where boilerplate files will be written"
    },
    "symbols": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Optional list of specific symbol IDs to generate boilerplate for. If omitted, all symbols are included."
    }
  }
}
```

**Output:** JSON array of `{ "filePath": string, "action": "created" | "updated" | "skipped" }` describing the files written.

---

### `adik_get_symbol`

Look up a specific symbol in the Registry by ID or name.

**Input schema:**

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "The unique registry ID of the symbol (e.g. 'fn:getUserById')"
    },
    "name": {
      "type": "string",
      "description": "The name of the symbol. Used if 'id' is not provided."
    }
  }
}
```

**Output:** The YAML entry for the symbol, or an error if not found.

---

### `adik_get_build_report`

Returns the most recent `sdk/BUILD_REPORT.md`.

**Input schema:**

```json
{
  "type": "object",
  "properties": {
    "language": {
      "type": "string",
      "enum": ["typescript", "python", "csharp"],
      "description": "Filter report to a single language. If omitted, all languages are included."
    }
  }
}
```

**Output:** Markdown string of the build report.

---

### `adik_vector_search`

Performs a semantic similarity search over the vectorized Registry and codebase. Only available when vector mode is active (see `ADIK.orchestrator.md` — Vector and RAG Support).

**Input schema:**

```json
{
  "type": "object",
  "required": ["query"],
  "properties": {
    "query": {
      "type": "string",
      "description": "Natural-language or code-fragment query to search for semantically similar symbols or code chunks"
    },
    "scope": {
      "type": "string",
      "enum": ["registry", "codebase", "all"],
      "default": "all",
      "description": "Whether to search the Registry embeddings, the codebase embeddings, or both"
    },
    "topK": {
      "type": "integer",
      "default": 10,
      "minimum": 1,
      "maximum": 100,
      "description": "Maximum number of results to return"
    },
    "filter": {
      "type": "object",
      "description": "Optional metadata filter (e.g. { \"kind\": \"endpoint\" } to restrict to endpoint symbols)",
      "additionalProperties": true
    }
  }
}
```

**Output:** JSON array of `{ "id": string, "kind": string, "name": string, "score": number, "excerpt": string }` ordered by descending similarity score.

**Availability:** This tool is registered only when `adik.env.json` reports an active vector store. Calling it in document mode returns a `409 Conflict` error with the message `"Vector search is not available in this environment. Ensure a vector database is configured (via VECTOR_DB_URL or adik.config.json vectors.storeUri) or that bundled vectors are present in the vectors/ directory."`

---

## Resources

The MCP server exposes the following read-only resources:

| URI | Description |
|---|---|
| `adik://registry` | Full `Registry.md` contents |
| `adik://registry/{section}` | Single registry section (e.g. `adik://registry/endpoints`) |
| `adik://sdk/build-report` | Most recent `sdk/BUILD_REPORT.md` |
| `adik://config` | Current `adik.config.json` contents |
| `adik://env` | Current `adik.env.json` contents (detected environment capabilities, including vector status) |

---

## Prompts

The MCP server registers the following prompt templates for use by connected agents:

### `adik_sdk_overview`

Returns a concise overview of the generated SDK: project type, available languages, number of endpoints/classes/functions, and a link to the build report.

**Input schema:**

```json
{
  "type": "object",
  "properties": {
    "languages": {
      "type": "array",
      "items": { "type": "string", "enum": ["typescript", "python", "csharp"] },
      "description": "Filter the overview to specific languages. If omitted, all configured languages are included."
    }
  }
}
```

### `adik_onboard_consumer`

Given a `language` parameter, returns step-by-step onboarding instructions for a developer who wants to use the generated SDK in a new project, including installation commands, client initialisation, and a first API call example.

**Input schema:**

```json
{
  "type": "object",
  "required": ["language"],
  "properties": {
    "language": {
      "type": "string",
      "enum": ["typescript", "python", "csharp"],
      "description": "The target language for the onboarding guide"
    },
    "framework": {
      "type": "string",
      "description": "Optional framework hint (e.g. 'react', 'nestjs', 'fastapi', 'aspnet') to tailor the onboarding instructions"
    }
  }
}
```

---

## Running the Server

### stdio transport (default — for use with Claude Desktop, VS Code Copilot, etc.)

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "adik": {
      "command": "npx",
      "args": ["adik-mcp-server", "--registry", "./Registry.md"],
      "env": {
        "ADIK_OUTPUT_DIR": "./sdk"
      }
    }
  }
}
```

### HTTP + SSE transport (for remote or multi-user environments)

```bash
npx adik-mcp-server --transport http --port 3100 --registry ./Registry.md
```

---

## Security

- The MCP server operates with **read-only access by default**. Write operations (`adik_build_sdk`, `adik_analyse_codebase`, `adik_scaffold_boilerplate`) must be explicitly enabled via `--allow-writes` flag or `ADIK_ALLOW_WRITES=true` environment variable.
- When running in HTTP mode, configure authentication via `ADIK_AUTH_TOKEN` environment variable. All requests must include `Authorization: Bearer <token>`.
- The server never exposes source code directly — only the structured Registry data and generated SDK artifacts.

---

## Related Files

| File | Role |
|---|---|
| `ADIK.orchestrator.md` | Root orchestrator; defines vector detection and configuration |
| `Registry.md` | Primary data source for the MCP server |
| `adik.env.json` | Detected environment capabilities (governs `adik_vector_search` availability) |
| `agents/builder.agent.md` | Agent triggered by `adik_build_sdk` tool |
| `agents/codebase-analyst.agent.md` | Agent triggered by `adik_analyse_codebase` tool |
| `skills/sdk-consumer.skill.md` | Skill triggered by `adik_scaffold_boilerplate` tool |
