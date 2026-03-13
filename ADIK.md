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
8. **Inferring framework hints** — automatically detects the target frameworks in use (React, NestJS, FastAPI, ASP.NET, etc.) from `architecture.md`, package manifests, and existing agent/skill files, so SDK boilerplate is framework-idiomatic without manual configuration.
9. **Preventing crosstailing** — records a development-state snapshot before each run to detect stale artifacts and config drift from prior runs.
10. **Leveraging vector capabilities** — when the target environment provides a vector database or RAG pipeline, ADIK delegates all vectorization work to `skills/vectorize.skill.md` so the orchestrator remains lean.

> **See also:** `ADIKbuilder.md` in the ADIK source repository governs the development and release of the ADIK framework itself. It is not part of this deployable bundle.

---

## Framework Hints Inference

When `frameworkHints` are not explicitly provided, ADIK instructs the Codebase Analyst Agent to infer them automatically before SDK generation begins:

| Signal Source | Examples Detected |
|---|---|
| `architecture.md` (repo root or `docs/`) | "React", "NestJS", "FastAPI", "ASP.NET" in tech-stack sections |
| `package.json` dependencies | `react`, `@nestjs/core`, `express`, `fastify`, `vue`, `@angular/core` |
| `pyproject.toml` / `requirements.txt` | `fastapi`, `flask`, `django`, `starlette` |
| `*.csproj` PackageReference | `Microsoft.AspNetCore.*`, Blazor, Hangfire |
| Existing `agents/*.md` / `skills/*.md` | `framework:` or `frameworkHints:` front-matter |

Inferred hints are recorded in `adik.env.json` under `frameworkHints` and passed to the SDK Consumer Skill. If no signal is found, the Consumer Skill generates generic, framework-neutral boilerplate.

---

## Development State and Crosstailing Prevention

Before each run, ADIK records a development-state snapshot to detect drift from previous runs:

```
COMPARE current config against previous adik.env.json:
  → Warn if sdkLanguages changed (stale SDK directories may exist)
  → Warn if includePatterns changed (registry may have orphaned entries)
  → List stale sdk/<language>/ directories in adik.env.json.staleArtifacts
  → Record runAgents, runSkills, runConfig, runTimestamp in adik.env.json
```

This prevents **crosstailing** — the accumulation of inconsistent artifacts from overlapping or divergent ADIK runs. Stale artifacts are reported but never auto-deleted; the developer decides when to clean them.

---

## Vector and RAG Support

ADIK supports vector-based Registry and codebase navigation when the deployment environment provides a vector database or RAG pipeline. All embedding, chunking, and vector-store interactions are handled exclusively by `skills/vectorize.skill.md` — keeping this orchestrator and all agent files free of vector-store specifics.

### Navigation Modes

| Mode | When Used | Description |
|---|---|---|
| **Document** (default) | Always available | Agents parse `Registry.md` as plain Markdown |
| **Vector** (preferred) | When vector DB or RAG is detected | Agents query embedded representations via the Vectorize Skill |

### Bundle Vector Status

```yaml
# Corresponds to adik.config.json → vectors.bundled
vectors.bundled: false
# Set to true if this ADIK bundle was distributed with pre-computed vector embeddings.
# When true, embedding files are located at vectors/registry.vec and vectors/codebase.vec.
```

### Environment Detection

At startup, the Codebase Analyst Agent probes for vector capabilities (VECTOR_DB_URL, OPENAI_API_KEY, Chroma, Pinecone, Weaviate, Qdrant, pgvector, Redis Stack) and writes the result to `adik.env.json`. If active, it delegates to `skills/vectorize.skill.md`. Full probe rules are in `agents/codebase-analyst.agent.md`.

### Vector Usage by Agents

When vector mode is active:

- The **Codebase Analyst Agent** delegates to `skills/vectorize.skill.md` after populating `Registry.md`.
- The **Builder Agent** queries the vectorized Registry to resolve type dependencies semantically.
- The **MCP Server** exposes an additional `adik_vector_search` tool for semantic symbol lookup.

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
  ├─► [0] Codebase Analyst Agent      → probe env, infer frameworkHints, check dev state
  │         (agents/codebase-analyst.agent.md)
  │         output: adik.env.json
  │         │
  │         └── [opt] Vectorize Skill → embed Registry + codebase (if vector env active)
  │                   (skills/vectorize.skill.md)
  │
  ├─► [1] Codebase Analyst Agent      → analyse repo, populate Registry.md
  │         (agents/codebase-analyst.agent.md)
  │
  ├─► [2] Builder Agent               → reads Registry.md, delegates to skills
  │         (agents/builder.agent.md)
  │         │
  │         ├─► SDK Builder Skill     → emits TS / Python / C# SDK packages
  │         │     (skills/sdk-builder.skill.md)
  │         │
  │         └─► SDK Consumer Skill    → emits boilerplate, classes, serializers
  │               (skills/sdk-consumer.skill.md)
  │               (uses inferred frameworkHints from adik.env.json)
  │
  └─► [3] MCP Server                  → exposes ADIK capabilities to external agents
            (mcp/adik-mcp-server.md)
```

### Step 0 — Environment Probe, Framework Inference, and Dev-State Check

Before any analysis begins, the Codebase Analyst Agent probes the environment, infers framework hints, and validates the development state:

```
@agent codebase-analyst
task: probe-environment
checks: [vector-db, rag-pipeline, embeddings-config, framework-hints, dev-state]
output: adik.env.json
```

The result is written to `adik.env.json` and referenced throughout the pipeline:
- **`vectorMode`** — whether to activate the Vectorize Skill after analysis.
- **`frameworkHints`** — inferred target frameworks for the SDK Consumer Skill.
- **`staleArtifacts`** — any SDK directories or registry entries that conflict with the current config.

### Step 1 — Codebase Analysis

Invoke the **Codebase Analyst Agent**:

```
@agent codebase-analyst
task: analyse-and-register
target: <path-to-source-repo>
output: Registry.md
```

The agent scans all source files, identifies every public symbol (functions, classes, interfaces, schemas, enumerations, endpoints), and writes them to `Registry.md` in the canonical format. When `adik.env.json.vectorMode = "active"`, it invokes `skills/vectorize.skill.md` to embed and store all entries.

### Step 2 — SDK Generation

Invoke the **Builder Agent** once the registry is populated:

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

The builder reads `adik.env.json.frameworkHints` and passes them to `sdk-consumer.skill.md`. Explicit `frameworkHints` in the invocation always override inferred values.

### Step 3 — Continuous Sync

Every time new functionality is merged into the source repo, ADIK.md triggers a re-run of steps 0–2:

```
@agent codebase-analyst
task: diff-and-update
since: <last-registry-commit-sha>
output: Registry.md
```

Only changed symbols trigger incremental SDK regeneration. Changed embeddings are upserted incrementally via the Vectorize Skill.

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
├── adik.env.json                    ← (auto-generated) env capabilities, frameworkHints, dev state
├── vectors/                         ← (optional) bundled or generated vector embeddings
│   ├── registry.vec                 ← Registry embeddings (NDJSON; see vectorize.skill.md)
│   └── codebase.vec                 ← Codebase embeddings (NDJSON; see vectorize.skill.md)
├── agents/
│   ├── builder.agent.md             ← SDK builder agent
│   └── codebase-analyst.agent.md   ← codebase analysis + env probe + framework inference
├── skills/
│   ├── sdk-builder.skill.md         ← SDK code-generation skill
│   ├── sdk-consumer.skill.md        ← consumption boilerplate skill
│   └── vectorize.skill.md           ← vector embedding + upsert subskill (loaded on demand)
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
- **Vectorization is a subskill.** All vector-store interactions are isolated in `skills/vectorize.skill.md`. The orchestrator and agents never contain embedding or chunking logic directly.
- **frameworkHints are inferred, not required.** If the caller does not supply hints, the Codebase Analyst Agent infers them from `architecture.md`, package manifests, and existing agent/skill files.
- **Crosstailing is prevented by state tracking.** Each run records a dev-state snapshot in `adik.env.json` so the next run can detect and report stale artifacts before writing anything.

---

## Related Files

| File | Role |
|---|---|
| `Registry.md` | Single source of truth for all exported symbols |
| `adik.config.json` | Configuration including vector options |
| `adik.env.json` | Auto-generated: env capabilities, inferred frameworkHints, dev-state snapshot |
| `vectors/` | Bundled or generated vector embeddings (optional; managed by vectorize.skill.md) |
| `agents/codebase-analyst.agent.md` | Env probe, framework inference, dev-state check, symbol analysis |
| `agents/builder.agent.md` | Orchestrates SDK generation across languages |
| `skills/sdk-builder.skill.md` | Generates SDK packages per language |
| `skills/sdk-consumer.skill.md` | Generates framework-idiomatic consumption boilerplate |
| `skills/vectorize.skill.md` | Handles all vector embedding and upsert operations |
| `mcp/adik-mcp-server.md` | MCP server for external agent integration |
