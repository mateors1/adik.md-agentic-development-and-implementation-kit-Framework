# ADIK.md — Agentic Development and Implementation Kit

**ADIK.md** is a fully agentic framework for automating the creation and maintenance of SDKs for any project — whether it is an API, a service, or a library. Drop the ADIK bundle into your source repository and a team of specialised agents will analyse the codebase, build publish-ready SDK packages in TypeScript, Python, and C#, and keep them in sync as the project evolves.

---

## Key Files

| File | Role | Deployed to target repos? |
|---|---|---|
| `ADIKbuilder.md` | Source-repo orchestrator — governs the development and release of the ADIK framework itself | No |
| `ADIK.md` | Implementation orchestrator — drives SDK generation in target repositories | Yes |
| `Registry.md` | DRY symbol registry template | Yes |

`ADIKbuilder.md` remains in this repository only. `ADIK.md` is the file that gets copied into every target codebase.

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
├── ADIKbuilder.md                   ← Source-repo orchestrator (not deployed)
├── ADIK.md                          ← Implementation orchestrator (start here for target repos)
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

The bundle includes `ADIK.md` (implementation orchestrator), `Registry.md`, agents, skills, and the MCP server. `ADIKbuilder.md` is **not** included in the bundle.

### 2. (Optional) Create `adik.config.json`

```jsonc
{
  "projectType": "auto",
  "sdkLanguages": ["typescript", "python", "csharp"],
  "outputDir": "./sdk",
  "syncOnCommit": true,
  "vectors": {
    "bundled": false,
    "autoDetect": true,
    "preferVectors": true
  }
}
```

If omitted, ADIK uses sensible defaults and auto-detects the project type and vector capabilities.

### 3. Run the Codebase Analyst Agent

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
output: Registry.md
```

This populates `Registry.md` with all discovered symbols. If a vector DB is detected in the environment, the registry and codebase are also vectorized automatically.

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
| `ADIKbuilder.md` | Framework Orchestrator | Governs ADIK development and releases (source repo only) |
| `ADIK.md` | Implementation Orchestrator | Drives the entire SDK generation pipeline in target repos |
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

## Vector and RAG Support

ADIK can vectorize `Registry.md` and the target codebase when the deployment environment already uses a vector database or RAG pipeline. This enables semantic symbol lookup, richer cross-reference resolution, and faster incremental analysis on large codebases.

### How It Works

1. **Auto-detection** — on first run, ADIK probes the environment for a vector DB (Chroma, Pinecone, Weaviate, Qdrant, pgvector, etc.) or an embeddings-capable LLM provider.
2. **Vectorization** — if a vector DB is found, every Registry symbol entry and source file chunk is embedded and stored.
3. **Preference** — when `vectors.preferVectors: true` (the default), agents use semantic vector search over plain Markdown parsing whenever possible.
4. **Bundled vectors** — ADIK bundles can optionally ship with pre-computed embeddings (`vectors/registry.vec`, `vectors/codebase.vec`). Set `vectors.bundled: true` in `adik.config.json` to use them. Bundled vector files are serialized in [NDJSON](https://ndjson.org/) format where each line is `{"id": "<symbol-id>", "model": "<embedding-model>", "vector": [<float>, ...]}`. Bundled vectors are model-specific and not portable across different embedding models.
5. **Graceful degradation** — if no vector DB is available and no bundled vectors are present, ADIK falls back to document mode with no loss of functionality.

See `ADIK.md` for the full vector detection logic and configuration options.

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
| `adik_vector_search` | Semantic symbol search (available when vector mode is active) |

See `mcp/adik-mcp-server.md` for the full tool schemas and configuration.

---

## Contributing

ADIK.md is itself an agentic project. Improvements to agent definitions, skill templates, or the registry format are welcome as pull requests. Please keep agent and skill files self-contained — each file should be independently readable and actionable by an LLM agent without needing to load the entire repository.
