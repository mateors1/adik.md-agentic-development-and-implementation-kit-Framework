# ADIK.md — Agentic Development and Implementation Kit

**ADIK.md** is a fully agentic framework for automating the creation and maintenance of SDKs for any project — whether it is an API, a service, or a library. Drop the ADIK bundle into your source repository and a team of specialised agents will analyse the codebase, build publish-ready SDK packages in TypeScript, Python, and C#, and keep them in sync as the project evolves.

---

## What ADIK Does

1. **Analyses your codebase** — a dedicated Codebase Analyst Agent scans your source files, detects endpoints, classes, schemas, and exported functions, and writes everything to a structured `Registry.md` file.
2. **Builds the SDK** — a Builder Agent reads the Registry and delegates to language-specific skills to generate complete, idiomatic SDK packages in TypeScript, Python, and C#.
3. **Generates consumption boilerplate** — an SDK Consumer Skill produces ready-to-use examples, serialization helpers, adapter classes, and DI wiring for the generated SDK.
4. **Stays in sync** — every time new functionality is merged, ADIK detects changed symbols and regenerates only what has changed.
5. **Exposes an MCP server** — an optional Model Context Protocol server lets developers consume the SDK, query the registry, and trigger regeneration from any agentic environment.

---

## Repository Layout

```
├── ADIK.md                          ← Root orchestrator (start here)
├── Registry.md                      ← DRY symbol registry (single source of truth)
├── agents/
│   ├── builder.agent.md             ← SDK builder agent
│   └── codebase-analyst.agent.md   ← Codebase analysis subagent
├── skills/
│   ├── sdk-builder.skill.md         ← SDK code-generation skill (TS / Python / C#)
│   └── sdk-consumer.skill.md        ← Consumption boilerplate skill
└── mcp/
    └── adik-mcp-server.md           ← MCP server definition
```

---

## Quick Start

### 1. Add ADIK to Your Source Repository

Copy the ADIK bundle into the root of the repository whose SDK you want to generate:

```bash
cp -r adik.md-bundle/* /path/to/your/source-repo/
```

### 2. (Optional) Create `adik.config.json`

```jsonc
{
  "projectType": "auto",
  "sdkLanguages": ["typescript", "python", "csharp"],
  "outputDir": "./sdk",
  "syncOnCommit": true
}
```

If omitted, ADIK uses sensible defaults and auto-detects the project type.

### 3. Run the Codebase Analyst Agent

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
output: Registry.md
```

This populates `Registry.md` with all discovered symbols.

### 4. Run the Builder Agent

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

Generated SDKs appear in `sdk/typescript/`, `sdk/python/`, and `sdk/csharp/`.

### 5. (Optional) Start the MCP Server

```bash
npx adik-mcp-server --registry ./Registry.md
```

Add the server to your MCP client config so any connected agent can query the registry and trigger SDK rebuilds.

---

## Agentic Artifacts

| File | Kind | Role |
|---|---|---|
| `ADIK.md` | Orchestrator | Drives the entire pipeline |
| `Registry.md` | Artifact | DRY single source of truth for all symbols |
| `agents/builder.agent.md` | Agent | Generates SDK packages |
| `agents/codebase-analyst.agent.md` | Agent | Analyses source and populates Registry |
| `skills/sdk-builder.skill.md` | Skill | Emits TS / Python / C# SDK code |
| `skills/sdk-consumer.skill.md` | Skill | Emits consumption boilerplate and examples |
| `mcp/adik-mcp-server.md` | MCP Server | Exposes ADIK capabilities to external agents |

---

## Supported Languages

| Language | Package Manager | Formats |
|---|---|---|
| TypeScript | npm / pnpm / yarn | ESM + CJS + `.d.ts` declarations |
| Python | pip / poetry / uv | Wheel + sdist |
| C# | NuGet | `.nupkg` |

---

## DRYness via Registry.md

A core design principle of ADIK is that **every symbol, type, and schema is defined once** in `Registry.md` and then generated into all target languages from that single definition. This prevents drift between SDK versions and makes it easy to audit the public API surface at a glance.

The Registry uses annotated Markdown sections with `ADIK:<SECTION>:START` / `ADIK:<SECTION>:END` markers so agents can parse it reliably while keeping it human-readable.

---

## MCP Integration

The ADIK MCP server exposes the following tools to connected agents:

| Tool | Description |
|---|---|
| `adik_get_registry` | Query the symbol registry |
| `adik_build_sdk` | Trigger SDK generation |
| `adik_analyse_codebase` | Refresh the registry from source |
| `adik_scaffold_boilerplate` | Generate consumption boilerplate |
| `adik_get_symbol` | Look up a specific symbol |
| `adik_get_build_report` | Retrieve the latest build report |

See `mcp/adik-mcp-server.md` for the full tool schemas and configuration.

---

## Contributing

ADIK.md is itself an agentic project. Improvements to agent definitions, skill templates, or the registry format are welcome as pull requests. Please keep agent and skill files self-contained — each file should be independently readable and actionable by an LLM agent without needing to load the entire repository.
