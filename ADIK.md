# ADIK.md — Agentic Development and Implementation Kit

> **Version:** 1.0.0
> **Role:** Implementation Orchestrator
> **Scope:** Deployed into target repositories — drives SDK generation and codebase implementation

---

## Purpose

ADIK.md is the implementation orchestrator of the Agentic Development and Implementation Kit. It is copied from the ADIK source repository into the **target repository** whose SDK is being built, and drives the automated, end-to-end creation of a fully functional SDK for that project.

ADIK.md is responsible for:

1. **Analysing the source project** to determine its nature (service, API, or library).
2. **Orchestrating all agents and skills** required to produce SDK artifacts.
3. **Keeping the Registry up to date** — the single source of truth for all exported symbols.
4. **Generating SDK packages** in TypeScript, Python, and C# that stay in sync with every new feature.
5. **Producing consumption artifacts** (classes, serialization helpers, boilerplate) for downstream consumers.
6. **Exposing an MCP server** so the ADIK can be driven from any agentic environment in the target codebase.
7. **Integrating cleanly with the host repository's `agents.md`** so all context and skills persist.
8. **Leveraging vector capabilities** — when the target environment provides a vector database or RAG pipeline, ADIK uses vectorized representations of `Registry.md` and the codebase for faster, richer symbol navigation and semantic retrieval.

> **See also:** `ADIKbuilder.md` in the ADIK source repository governs the development and release of the ADIK framework itself. It is not part of this deployable bundle.

---

## Vector and RAG Support

### Overview

ADIK supports two navigation modes for `Registry.md` and the codebase:

| Mode | When Used | Description |
|---|---|---|
| **Document** (default) | Always available | Agents parse `Registry.md` as plain Markdown |
| **Vector** (preferred) | When vector DB or RAG is detected | Agents query embedded representations for semantic, cross-reference-aware retrieval |

### Bundle Vector Status

```yaml
# Corresponds to adik.config.json → vectors.bundled
vectors.bundled: false
# Set to true if this ADIK bundle was distributed with pre-computed vector embeddings
# for Registry.md and the codebase.
# When true, embedding files are located at vectors/registry.vec and
# vectors/codebase.vec relative to this file.
```

### Environment Detection

At startup, ADIK.md instructs the Codebase Analyst Agent to probe the target environment for vector capabilities:

```
IF vectors/ directory exists AND vectors.bundled = true
  → USE bundled embeddings for Registry and codebase navigation

ELSE IF environment exposes a vector DB or RAG endpoint
  (detected via: VECTOR_DB_URL env var / OPENAI_API_KEY with embeddings config /
   presence of config files for Chroma, Pinecone, Weaviate, Qdrant, pgvector, or
   Redis Stack — see agents/codebase-analyst.agent.md for the full probe rules)
  → VECTORIZE Registry.md and codebase on first run
  → STORE embeddings in vectors/ directory
  → USE vector search for all subsequent Registry lookups

ELSE
  → USE document mode (plain Markdown parsing)
```

### Vector Usage by Agents

When vector mode is active:

- The **Codebase Analyst Agent** uses semantic search to identify related symbols and detect drift across large codebases more accurately than line-by-line diffing.
- The **Builder Agent** queries the vectorized Registry to resolve type dependencies and cross-references without full-document parsing.
- The **MCP Server** exposes an additional `adik_vector_search` tool for semantic symbol lookup.

### Vectorization of Registry.md

When a vector DB is available, the Registry is vectorized incrementally on each write:

```
ON Registry.md write:
  1. Embed each symbol entry as a document chunk (id + kind + name + signature + description).
  2. Upsert the embedding into the vector store, keyed by the symbol's stable `id`.
  3. Record the vector store URI in Registry.md Project Metadata under `vectorStoreUri`.
```

### Vectorization of the Codebase

When a vector DB is available, source files are vectorized to support semantic codebase navigation:

```
ON first run OR diff-and-update:
  1. Chunk source files by logical unit (function body, class definition, module).
  2. Embed each chunk.
  3. Upsert into the vector store, keyed by file path + chunk index.
  4. Record the vector store URI in adik.config.json under vectors.storeUri.
```

---

## Project-Type Detection

Before delegating work, ADIK.md instructs the `Codebase Analyst Agent` to classify the source project using the following heuristic:

| Signal | Detected Type |
|---|---|
| HTTP endpoints / OpenAPI spec present | **API** |
| Deployed runtime, message queue, or gRPC interface | **Service** |
| Published package manifest (npm, PyPI, NuGet) with no server entry-point | **Library** |

The detected type is recorded in `Registry.md` under `## Project Metadata` and governs which SDK-generation strategy is applied.

---

## Orchestration Workflow

```
ADIK.md
  │
  ├─► [0] Environment Probe           → detect vector DB / RAG capabilities
  │         (agents/codebase-analyst.agent.md)
  │         output: adik.env.json
  │
  ├─► [1] Codebase Analyst Agent      → analyses repo, populates Registry.md
  │         (agents/codebase-analyst.agent.md)
  │         └── [opt] Vectorize Registry.md and codebase if vector env detected
  │
  ├─► [2] Builder Agent               → reads Registry.md, delegates to skills
  │         (agents/builder.agent.md)
  │         │
  │         ├─► SDK Builder Skill     → emits TS / Python / C# SDK packages
  │         │     (skills/sdk-builder.skill.md)
  │         │
  │         └─► SDK Consumer Skill    → emits boilerplate, classes, serializers
  │               (skills/sdk-consumer.skill.md)
  │
  └─► [3] MCP Server                  → exposes ADIK capabilities to external agents
            (mcp/adik-mcp-server.md)
```

### Step 0 — Environment Probe (Vector Detection)

Before any analysis begins, probe the environment for vector capabilities:

```
@agent codebase-analyst
task: probe-environment
checks: [vector-db, rag-pipeline, embeddings-config]
output: adik.env.json
```

The result is written to `adik.env.json` and referenced throughout the pipeline. If a vector DB or RAG endpoint is detected, all subsequent steps prefer vector-based retrieval over plain-document parsing.

### Step 1 — Codebase Analysis

Invoke the **Codebase Analyst Agent**:

```
@agent codebase-analyst
task: analyse-and-register
target: <path-to-source-repo>
output: Registry.md
vectorize: <from adik.env.json>
```

The agent scans all source files, identifies every public symbol (functions, classes, interfaces, schemas, enumerations, endpoints), and writes them to `Registry.md` in the canonical format. When vector mode is active, it also upserts embeddings for each symbol entry and each source file chunk.

### Step 2 — SDK Generation

Invoke the **Builder Agent** once the registry is populated:

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
useVectors: <from adik.env.json>
```

The builder delegates to `sdk-builder.skill.md` per language and `sdk-consumer.skill.md` for boilerplate. When vector mode is active, type resolution uses semantic vector search rather than full-document parsing.

### Step 3 — Continuous Sync

Every time new functionality is merged into the source repo, ADIK.md triggers a re-run of steps 0–2:

```
@agent codebase-analyst
task: diff-and-update
since: <last-registry-commit-sha>
output: Registry.md
vectorize: <from adik.env.json>
```

Only changed symbols trigger incremental SDK regeneration, keeping build times short. Changed embeddings are upserted incrementally.

---

## Integration with `agents.md`

After the first successful run, ADIK.md appends the following snippet to the repository's root `agents.md` (or creates one if absent):

```markdown
## ADIK — SDK Orchestrator

Loaded agents:
- agents/builder.agent.md
- agents/codebase-analyst.agent.md

Loaded skills:
- skills/sdk-builder.skill.md
- skills/sdk-consumer.skill.md

Registry: Registry.md
MCP server: mcp/adik-mcp-server.md
Vector store: <vectorStoreUri or "none">
```

This ensures all ADIK agents and skills are available in any agentic session that loads the repository.

---

## File Layout

```
<target-repo>/
├── ADIK.md                          ← this file (implementation orchestrator)
├── Registry.md                      ← DRY symbol registry
├── adik.config.json                 ← (optional) configuration
├── adik.env.json                    ← (auto-generated) detected environment capabilities
├── vectors/                         ← (optional) bundled or generated vector embeddings
│   ├── registry.vec                 ← Registry embeddings (if vectorsBundled or generated)
│   └── codebase.vec                 ← Codebase embeddings (if vectorsBundled or generated)
├── agents/
│   ├── builder.agent.md             ← SDK builder agent
│   └── codebase-analyst.agent.md   ← codebase analysis subagent
├── skills/
│   ├── sdk-builder.skill.md         ← SDK code-generation skill
│   └── sdk-consumer.skill.md        ← consumption boilerplate skill
└── mcp/
    └── adik-mcp-server.md           ← MCP server definition
```

---

## Configuration

ADIK.md reads configuration from the optional `adik.config.json` file in the repository root. If the file is absent, all defaults apply.

```jsonc
{
  "projectType": "auto",            // "auto" | "api" | "service" | "library"
  "sdkLanguages": ["typescript", "python", "csharp"],
  "outputDir": "./sdk",
  "registryPath": "./Registry.md",
  "mcpPort": 3100,
  "syncOnCommit": true,             // re-run analysis on every commit
  "includePatterns": ["src/**/*"],
  "excludePatterns": ["**/*.test.*", "**/*.spec.*"],
  "vectors": {
    "bundled": false,               // true if embeddings are distributed with this bundle
    "autoDetect": true,             // probe environment for vector DB / RAG capabilities
    "preferVectors": true,          // use vector search over document parsing when available
    "storeUri": "",                 // explicit vector store URI (overrides auto-detection)
    "embeddingModel": "auto",       // embedding model; "auto" selects the first available:
                                    //   1. model named in VECTOR_EMBEDDING_MODEL env var
                                    //   2. provider default (e.g. text-embedding-3-small for OpenAI)
                                    //   3. local model if no remote provider is detected
    "chunkStrategy": "symbol"       // "symbol" | "file" | "sliding-window"
  }
}
```

---

## Constraints and Principles

- **DRYness is enforced through the Registry.** No SDK artifact may define a type or schema that is not first declared in `Registry.md`.
- **ADIK.md never modifies source code.** It only generates SDK output directories and agentic artifact files.
- **Language-specific output is self-contained.** Each generated SDK package includes its own `README`, type definitions, and serialization helpers so it can be published independently.
- **The MCP server is optional.** Teams that do not need remote orchestration can omit the MCP component entirely.
- **Vector mode degrades gracefully.** When no vector DB is available, ADIK falls back to document mode without loss of functionality.
- **Vectors are never required.** All core ADIK functionality works in document mode. Vector mode is an optimisation for large codebases and environments that already invest in RAG infrastructure.

---

## Related Files

| File | Role |
|---|---|
| `Registry.md` | Single source of truth for all exported symbols |
| `adik.config.json` | Configuration including vector options |
| `adik.env.json` | Auto-generated environment capability report |
| `vectors/` | Bundled or generated vector embeddings (optional) |
| `agents/builder.agent.md` | Orchestrates SDK generation across languages |
| `agents/codebase-analyst.agent.md` | Analyses source code and populates Registry |
| `skills/sdk-builder.skill.md` | Generates SDK packages per language |
| `skills/sdk-consumer.skill.md` | Generates consumption boilerplate |
| `mcp/adik-mcp-server.md` | MCP server for external agent integration |
