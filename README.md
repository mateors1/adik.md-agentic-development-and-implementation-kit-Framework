# ADIK.md — Agentic Development and Implementation Kit

**ADIK.md** is a fully agentic framework for automating the creation and maintenance of SDKs for any project — whether it is an API, a service, or a library.

---

## Manifesto

Software teams spend enormous effort writing and maintaining SDKs, client libraries, and consumption boilerplate — work that is mechanical, error-prone, and chronically behind the actual service. Every time an endpoint changes, every generated type drifts. Every time a new developer joins, they spend days unwrapping how to call the API.

**ADIK inverts this.** The source of truth is the *codebase*, not a wiki or a hand-maintained SDK. A team of specialised agents reads your code, understands its structure, and generates complete, publish-ready SDK packages in TypeScript, Python, and C#. When the codebase changes, the SDK changes. When a new developer joins, the boilerplate is already there.

ADIK is built on four principles:

1. **One source of truth.** Every type, schema, and endpoint is declared once in `Registry.md` and generated into all languages from that single definition.
2. **Inference over configuration.** Framework hints, project type, vector capabilities — ADIK discovers these automatically. You should only need to configure what ADIK cannot know.
3. **Context cleanliness.** Vectorization, framework-specific logic, and infrastructure concerns live in dedicated subagents and subskills. The orchestrator stays lean and readable in any context window.
4. **Graceful degradation.** Every feature is additive. Vector mode, MCP server, framework-specific boilerplate — all optional. The core pipeline works with zero configuration.

---

## Key Files

| File | Role | Deployed to target repos? |
|---|---|---|
| `ADIKbuilder.md` | Source-repo orchestrator — governs development and release of the ADIK framework | No |
| `ADIK.md` | Implementation orchestrator — drives SDK generation in target repositories | Yes |
| `ADIKBuilderExample.md` | Step-by-step guide to building your own ADIK implementation from scratch | No |
| `Registry.md` | DRY symbol registry template | Yes |

`ADIKbuilder.md` and `ADIKBuilderExample.md` remain in this repository only. `ADIK.md` is the file that gets copied into every target codebase.

---

## What ADIK Does

1. **Analyses your codebase** — a dedicated Codebase Analyst Agent scans your source files, detects endpoints, classes, schemas, and exported functions, and writes everything to a structured `Registry.md` file.
2. **Infers your framework** — ADIK reads `architecture.md`, package manifests, and existing agent/skill files to automatically detect which frameworks you use (React, NestJS, FastAPI, ASP.NET, etc.) so generated boilerplate is idiomatic from day one.
3. **Checks development state** — before each run, ADIK snapshots the pipeline configuration and detects stale artifacts from prior runs to prevent crosstailing.
4. **Builds the SDK** — a Builder Agent reads the Registry and delegates to language-specific skills to generate complete, idiomatic SDK packages in TypeScript, Python, and C#.
5. **Generates consumption boilerplate** — an SDK Consumer Skill produces ready-to-use examples, serialization helpers, adapter classes, and DI wiring — framework-specific when hints are available.
6. **Stays in sync** — every time new functionality is merged, ADIK detects changed symbols and regenerates only what has changed.
7. **Optionally vectorizes** — when a vector DB is available, a dedicated Vectorize Skill embeds the Registry and codebase for semantic search. The orchestrator and agents stay clean; the skill handles all embedding logic.
8. **Exposes an MCP server** — an optional Model Context Protocol server lets developers consume the SDK, query the registry, and trigger regeneration from any agentic environment.

---

## Repository Layout

```
├── ADIKbuilder.md                   ← Source-repo orchestrator (not deployed)
├── ADIK.md                          ← Implementation orchestrator (deployed to target repos)
├── ADIKBuilderExample.md            ← Guide for building your own ADIK from scratch
├── Registry.md                      ← DRY symbol registry (single source of truth)
├── agents/
│   ├── builder.agent.md             ← SDK builder agent
│   └── codebase-analyst.agent.md   ← Codebase analysis + env probe + frameworkHints inference
├── skills/
│   ├── sdk-builder.skill.md         ← SDK code-generation skill (TS / Python / C#)
│   ├── sdk-consumer.skill.md        ← Framework-idiomatic consumption boilerplate skill
│   └── vectorize.skill.md           ← Vector embedding + upsert subskill (loaded on demand)
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
| `ADIKBuilderExample.md` | Scaffolding Guide | Step-by-step guide for building your own ADIK (source repo only) |
| `ADIK.md` | Implementation Orchestrator | Drives the entire SDK generation pipeline in target repos |
| `Registry.md` | Artifact | DRY single source of truth for all symbols |
| `agents/builder.agent.md` | Agent | Generates SDK packages |
| `agents/codebase-analyst.agent.md` | Agent | Analyses source, infers frameworkHints, checks dev state |
| `skills/sdk-builder.skill.md` | Skill | Emits TS / Python / C# SDK code |
| `skills/sdk-consumer.skill.md` | Skill | Emits framework-idiomatic consumption boilerplate |
| `skills/vectorize.skill.md` | Subskill | Handles all vector embedding and upsert (loaded on demand) |
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

## Context Cleanliness

ADIK is designed so each file loads in a manageable context window:

- **Vectorization** is isolated in `skills/vectorize.skill.md` — only loaded when vector mode is active. The orchestrator and agents never contain embedding or chunking logic.
- **Framework-specific boilerplate** is handled in `skills/sdk-consumer.skill.md` — the orchestrator only passes inferred hints.
- **Development state** is persisted in `adik.env.json` — each run reads the snapshot rather than reconstructing context from scratch.

---

## Vector and RAG Support

ADIK can vectorize `Registry.md` and the target codebase when the deployment environment already uses a vector database or RAG pipeline. All vector-store interactions are handled by `skills/vectorize.skill.md`; the orchestrator and agents stay clean.

### How It Works

1. **Auto-detection** — on first run, ADIK probes for a vector DB (Chroma, Pinecone, Weaviate, Qdrant, pgvector, etc.) or an embeddings-capable provider.
2. **Delegation** — if found, the Codebase Analyst Agent invokes `skills/vectorize.skill.md` after populating `Registry.md`.
3. **Preference** — `vectors.preferVectors: true` (the default) makes agents use semantic search over document parsing when available.
4. **Bundled vectors** — bundles can ship with pre-computed embeddings in `vectors/` (NDJSON format, model-specific). Set `vectors.bundled: true` in `adik.config.json`.
5. **Graceful degradation** — no vector DB? Document mode works without any loss of functionality.

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

## Build Your Own ADIK

Want to implement the ADIK pattern from scratch, without using this repository? See **[`ADIKBuilderExample.md`](ADIKBuilderExample.md)** for a complete, self-contained, step-by-step construction guide covering:

- Building your own framework orchestrator (`MyADIKbuilder.md`)
- Building the implementation orchestrator (`ADIK.md`) with the correct structure
- Implementing the symbol registry, agents, skills, and MCP server
- Applying the vectorize-as-subskill pattern
- Applying the frameworkHints inference pattern
- Applying the dev-state / crosstailing prevention pattern
- A verification checklist before your first release

---

## Contributing

ADIK is itself an agentic project. Improvements to agent definitions, skill templates, or the registry format are welcome as pull requests. Please keep agent and skill files self-contained — each file should be independently readable and actionable by an LLM agent without needing to load the entire repository.
