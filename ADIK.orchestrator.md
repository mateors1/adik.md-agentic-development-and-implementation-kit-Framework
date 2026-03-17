# ADIK.orchestrator.md — Operational Orchestrator

> **Version:** 1.0.0
> **Role:** Specialized Orchestrator — the brain inside every adik
> **Scope:** Deployed as part of every adik into target repositories
> **Standard:** See [`ADIK.md`](ADIK.md) for the standard definition. See [`docs/standard.md`](docs/standard.md) for the formal specification.

---

## About This Project

> **[AUTO-FILLED ON FIRST RUN]** When this orchestrator runs for the first time in a target repository, this section is populated with a project-specific summary:
>
> - **Project name and description** — what the project does and who uses it
> - **Tech stack and frameworks** — detected from `architecture.md`, package manifests, and existing agent/skill files
> - **Project type** — `api` | `service` | `library` (auto-detected)
> - **SDK target languages** — as configured or defaulted to `[typescript, python, csharp]`
> - **ADIK reach** — which parts of the codebase the adik covers (included source patterns, registry scope, SDK output directories)
>
> Example:
> ```
> Project: PaymentsAPI — REST API for payment processing (Node.js / NestJS)
> Frameworks: NestJS, TypeORM, Jest
> Project type: api
> SDK languages: TypeScript, Python
> ADIK reach: src/**/* → Registry.md → sdk/typescript/, sdk/python/
> ```

---

## Implementation Mode — First Question

> **⚠️ REQUIRED STARTUP PROTOCOL**
>
> When this orchestrator is first invoked in a new project (i.e., this is the first run and no `adik.env.json` exists), **before taking any implementation action**, it must ask the following question:

---

**ADIK Startup Prompt:**

> I have analysed this repository and identified the following areas where I can help:
>
> - **SDK generation** for `[detected languages]`
> - **Registry population** from `[detected source patterns]`
> - **Consumption boilerplate** for `[detected frameworks]`
> - **Context embedding** into `.github/copilot-instructions.md`, `CLAUDE.md`, and `agents.md`
> - *(list any other applicable areas)*
>
> How would you like to proceed?
>
> **A) Blanket implementation** — I will apply ADIK across all identified areas automatically, using my best judgment for configuration and scope. Recommended for most projects. *(Faster — I'll ask clarifying questions only if I hit an ambiguity I cannot resolve.)*
>
> **B) Guided implementation** — Before I proceed, please describe any constraints, exclusions, or specific requirements I should follow. *(Better for projects with non-standard layouts, partial adoption, or specific output requirements.)*
>
> *Please respond with **A**, **B**, or describe your requirements.*

---

On receiving **A**: proceed with all identified implementation areas using auto-detected configuration. Document decisions in `adik.env.json` under `startupMode: "blanket"`.

On receiving **B**: collect requirements before proceeding. Record them in `adik.env.json` under `startupGuidance` and respect them throughout the pipeline.

On receiving neither: interpret the response as guided requirements and record them accordingly.

> **Note:** On subsequent runs (when `adik.env.json` already exists), skip this question and proceed in the mode recorded at `startupMode`. If the mode is `"guided"`, re-apply the saved `startupGuidance` unless the user explicitly overrides it.

---

## Headless / Non-Interactive Mode

When the adik runs in a CI/CD pipeline or any environment without a human at the keyboard, the
interactive startup prompt must be bypassed. The orchestrator checks the following signals **before** asking
any startup question:

| Signal | Effect |
|---|---|
| `ADIK_NON_INTERACTIVE=true` | Skip startup prompt; use `ADIK_STARTUP_MODE` or default to `blanket` |
| `ADIK_STARTUP_MODE=blanket` | Force blanket mode without prompting |
| `ADIK_STARTUP_MODE=guided` | Force guided mode; `startupGuidance` must be present in `adik.env.json` |
| `adik.env.json` already exists | Skip startup prompt; re-apply saved `startupMode` |
| No TTY detected (CI context) | Warn and default to `blanket`; write `startupMode: "blanket"` to `adik.env.json` |

**Recommended CI configuration:**

```yaml
# In your GitHub Actions workflow or CI script:
env:
  ADIK_NON_INTERACTIVE: 'true'
  ADIK_STARTUP_MODE: 'blanket'
```

**Recommended `adik.config.json` for CI environments:**

```jsonc
{
  "syncOnCommit": true,
  "nonInteractive": true,        // alternative to env var
  "startupMode": "blanket"
}
```

> **Note:** The ADIK self-deploy workflow (`.github/workflows/adik-self-deploy.yml`) sets
> `ADIK_NON_INTERACTIVE=true` automatically. Teams running ADIK in their own CI pipelines
> should do the same.

---

After the first successful run, the orchestrator **must** embed itself into the target project's agentic
context files. This ensures that any AI assistant working in the target project is always aware
that the adik is present and active.

> **⚠️ Deterministic embedding required.** All three context files use
> `<!-- ADIK:START -->` / `<!-- ADIK:END -->` XML guard markers. Agents MUST invoke
> `python3 scripts/adik-embed.py --action upsert --target .` rather than editing these files
> directly. The script is idempotent — running it multiple times never produces duplicate blocks.

### How to Embed

```bash
# Insert or update ADIK blocks in all three context files
python3 scripts/adik-embed.py --action upsert --target .

# Verify all blocks are in place
python3 scripts/adik-embed.py --action check --target .
```

### Files Written

The script creates or updates these three files with an ADIK guard block:

1. **`.github/copilot-instructions.md`** — ADIK rules for GitHub Copilot
2. **`CLAUDE.md`** — ADIK executive summary and rules for Claude sessions
3. **`agents.md`** — ADIK agent/skill/registry registration for agentic sessions

### Embedding Rules

- **Use the script, not direct text editing.** The script guarantees idempotency.
- **Never overwrite** the entire file — only the ADIK guard block is updated.
- **Minimal footprint** — ADIK only writes its own block; all other file content is preserved.
- **Guard marker format:** `<!-- ADIK:START -->` … `<!-- ADIK:END -->` (exact strings).

---

## Framework Hints Inference

When `frameworkHints` are not explicitly provided, the orchestrator instructs the Codebase Analyst Agent to infer them automatically before SDK generation begins:

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

Before each run, the orchestrator records a development-state snapshot to detect drift from previous runs:

```
COMPARE current config against previous adik.env.json:
  → Warn if sdkLanguages changed (stale SDK directories may exist)
  → Warn if includePatterns changed (registry may have orphaned entries)
  → List stale sdk/<language>/ directories in adik.env.json.staleArtifacts
  → Record runAgents, runSkills, runConfig, runTimestamp in adik.env.json
```

This prevents **crosstailing** — the accumulation of inconsistent artifacts from overlapping or divergent runs. Stale artifacts are reported but never auto-deleted; the developer decides when to clean them.

---

## Vector and RAG Support

The adik supports vector-based Registry and codebase navigation when the deployment environment provides a vector database or RAG pipeline. All embedding, chunking, and vector-store interactions are handled exclusively by `skills/vectorize.skill.md` — keeping this orchestrator and all agent files free of vector-store specifics.

### Navigation Modes

| Mode | When Used | Description |
|---|---|---|
| **Document** (default) | Always available | Agents parse `Registry.md` as plain Markdown |
| **Vector** (preferred) | When vector DB or RAG is detected | Agents query embedded representations via the Vectorize Skill |

### Bundle Vector Status

```yaml
# Corresponds to adik.config.json → vectors.bundled
vectors.bundled: false
# Set to true if this adik was distributed with pre-computed vector embeddings.
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

Before delegating work, the orchestrator instructs the `Codebase Analyst Agent` to classify the source project using the following heuristic:

| Signal | Detected Type |
|---|---|
| HTTP endpoints / OpenAPI spec present | **API** |
| Deployed runtime, message queue, or gRPC interface | **Service** |
| Published package manifest (npm, PyPI, NuGet) with no server entry-point | **Library** |

The detected type is recorded in `Registry.md` under `## Project Metadata` and governs which SDK-generation strategy is applied.

---

## Orchestration Workflow

```
ADIK.orchestrator.md
  │
  ├─► [0] Codebase Analyst Agent      → probe env, infer frameworkHints, check dev state
  │         (agents/codebase-analyst.agent.md)
  │         output: adik.env.json
  │         │
  │         └── [opt] Vectorize Skill → embed Registry + codebase (if vector env active)
  │                   (skills/vectorize.skill.md)
  │
  ├─► [1] Codebase Analyst Agent      → analyse repo, populate Registry.md (or partitions)
  │         (agents/codebase-analyst.agent.md)
  │         output: Registry.md | Registry.index.md + Registry.<domain>.md files
  │         → surfaces vectorization advisory if total symbols ≥ 500
  │
  ├─► [2] Registry Validator Skill    → validate Registry schema before generation
  │         (skills/registry-validator.skill.md)
  │         output: sdk/VALIDATION_REPORT.md
  │         → FAIL aborts SDK generation
  │
  ├─► [3] Builder Agent               → reads Registry, delegates to skills
  │         (agents/builder.agent.md)
  │         │
  │         ├─► SDK Builder Skill     → emits TS / Python / C# SDK packages (tier-1)
  │         │     (skills/sdk-builder.skill.md)
  │         │
  │         ├─► SDK Builder Tier-2    → emits Go / Java / Kotlin packages (opt-in)
  │         │     (skills/sdk-builder-tier2.skill.md)
  │         │     only invoked when tier2Languages is configured in adik.config.json
  │         │
  │         └─► SDK Consumer Skill    → emits boilerplate, classes, serializers
  │               (skills/sdk-consumer.skill.md)
  │               (uses inferred frameworkHints from adik.env.json)
  │
  ├─► [4] Self-Embedding              → inject ADIK context into project files
  │         python3 scripts/adik-embed.py --action upsert --target .
  │         files: .github/copilot-instructions.md, CLAUDE.md, agents.md
  │
  └─► [5] MCP Server                  → exposes ADIK capabilities to external agents
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

### Step 1 — Codebase Analysis and Registry Population

Invoke the **Codebase Analyst Agent**:

```
@agent codebase-analyst
task: analyse-and-register
target: <path-to-source-repo>
output: Registry.md          # or Registry.index.md for large codebases
```

The agent scans all source files, identifies every public symbol, and writes them to the
registry. For large codebases (≥ 500 symbols or ≥ 200 KB), it writes domain-partitioned
`Registry.<domain>.md` files and a master `Registry.index.md`, then surfaces the vectorization
advisory if vector mode is not active.

The `partitionStrategy` option in `adik.config.json` controls how symbols are assigned to domains:
- **`"auto"`** (default) — infer from the first namespace segment; falls back to `"file"` if all
  symbols land in one partition.
- **`"manual"`** — use explicit `partitionMappings` to assign namespace globs to domain names.
- **`"file"`** — one partition per top-level source directory.

### Step 2 — Registry Validation

Before SDK generation, the Builder Agent invokes the **Registry Validator Skill**:

```
@skill registry-validator
registry: Registry.md    # or Registry.index.md
outputDir: ./sdk
```

Validation must report `PASS` or `WARN` before proceeding. A `FAIL` result aborts SDK
generation and instructs the developer to fix the registry or re-run the analyst.

### Step 3 — SDK Generation

Invoke the **Builder Agent** once validation passes:

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]      # tier-1
tier2Languages: [go, java]                   # opt-in; omit if not needed
```

The builder reads `adik.env.json.frameworkHints` and passes them to `sdk-consumer.skill.md`.
When `tier2Languages` is configured, it invokes `skills/sdk-builder-tier2.skill.md` for each
tier-2 language after completing tier-1 generation.

### Step 4 — Self-Embedding

After a successful build, the orchestrator deterministically updates the three context files:

```bash
python3 scripts/adik-embed.py --action upsert --target .
```

### Step 5 — Continuous Sync

Every time new functionality is merged into the source repo, the orchestrator triggers a re-run of
steps 0–3 (and 4 if context files have changed):

```
@agent codebase-analyst
task: diff-and-update
since: <last-registry-commit-sha>
output: Registry.md
```

Only changed symbols trigger incremental SDK regeneration. Changed embeddings are upserted
incrementally via the Vectorize Skill.

---

## Integration with `agents.md`, `CLAUDE.md`, and Copilot Instructions

After the first successful run, the orchestrator follows the **Self-Embedding Protocol** above to inject its presence into the three context files via `scripts/adik-embed.py`. The Builder Agent is responsible for triggering the script; the script itself handles all three files atomically.

The full ADIK integration block written to `agents.md` is managed by `scripts/adik-embed.py`.
The script renders the block from the current `adik.config.json` and `adik.env.json` values and
inserts it between `<!-- ADIK:START -->` and `<!-- ADIK:END -->` markers — idempotently, on every
successful build.

---

## File Layout

```
<target-repo>/
├── ADIK.md                          ← standard definition (reference)
├── ADIK.orchestrator.md             ← this file (operational orchestrator)
├── Registry.md                      ← DRY symbol registry (monolithic for small projects)
├── Registry.index.md                ← (auto-created) master index when registry is partitioned
├── Registry.<domain>.md             ← (auto-created) domain-scoped registry partitions
├── adik.config.json                 ← (optional) configuration
├── adik.env.json                    ← (auto-generated) env capabilities, frameworkHints, dev state
├── adik.audit.log                   ← (auto-generated) append-only NDJSON audit trail
├── CLAUDE.md                        ← (created/updated) ADIK context for Claude sessions
├── agents.md                        ← (created/updated) agent/skill registry for agentic sessions
├── .github/
│   ├── copilot-instructions.md      ← (created/updated) ADIK context for GitHub Copilot
│   └── workflows/
│       └── adik-self-deploy.yml     ← (optional) CI/CD self-deploy workflow
├── vectors/                         ← (optional) bundled or generated vector embeddings
│   ├── registry.vec                 ← Registry embeddings (NDJSON; see vectorize.skill.md)
│   └── codebase.vec                 ← Codebase embeddings (NDJSON; see vectorize.skill.md)
├── agents/
│   ├── builder.agent.md             ← SDK builder agent
│   └── codebase-analyst.agent.md   ← codebase analysis + env probe + framework inference
├── skills/
│   ├── sdk-builder.skill.md         ← SDK code-generation skill (TypeScript, Python, C#)
│   ├── sdk-builder-tier2.skill.md   ← Tier-2 SDK skill (Go, Java, Kotlin — opt-in)
│   ├── sdk-consumer.skill.md        ← consumption boilerplate skill
│   ├── registry-validator.skill.md  ← Registry schema validation (runs before every build)
│   └── vectorize.skill.md           ← vector embedding + upsert subskill (loaded on demand)
├── scripts/
│   ├── adik-embed.py                ← deterministic self-embedding script
│   └── adik-eject.py                ← clean uninstall / eject script
└── mcp/
    └── adik-mcp-server.md           ← MCP server definition
```

---

## Configuration

The orchestrator reads configuration from the optional `adik.config.json` file in the repository root. If the file is absent, all defaults apply.

```jsonc
{
  "projectType": "auto",            // "auto" | "api" | "service" | "library"
  "sdkLanguages": ["typescript", "python", "csharp"],   // tier-1 (always available)
  "tier2Languages": [],             // opt-in: [] | ["go"] | ["java"] | ["kotlin"] | any combination
  "tier2Options": {
    "go": {
      "modulePath": "",             // e.g. "github.com/acme/myapi-sdk-go"
      "goVersion": "1.21"
    },
    "java": {
      "groupId": "",                // e.g. "com.acme"
      "artifactId": "",             // e.g. "myapi-sdk"
      "javaVersion": "17",
      "buildTool": "maven"          // "maven" | "gradle"
    },
    "kotlin": {
      "groupId": "",
      "artifactId": "",
      "javaVersion": "17",
      "buildTool": "gradle"
    }
  },
  "outputDir": "./sdk",
  "registryPath": "./Registry.md",
  "registryMode": "auto",           // "auto" | "monolithic" | "partitioned"
  "partitionStrategy": "auto",      // "auto" | "manual" | "file" (controls domain assignment)
  "partitionMappings": {},           // used when partitionStrategy = "manual"; maps domain → glob patterns
  "partitionThresholdSymbols": 500, // trigger partitioned mode above this symbol count
  "partitionThresholdBytes": 204800, // or above this file size (200 KB)
  "vectorizationAdvisoryDismissed": false,  // set true to suppress advisory
  "mcpPort": 3100,
  "syncOnCommit": true,             // re-run analysis on every commit
  "nonInteractive": false,          // true = headless mode (no startup prompt)
  "startupMode": "blanket",         // "blanket" | "guided" (used in non-interactive mode)
  "includePatterns": ["src/**/*"],
  "excludePatterns": ["**/*.test.*", "**/*.spec.*"],
  "vectors": {
    "bundled": false,               // true if embeddings are distributed with this adik
    "autoDetect": true,             // probe environment for vector DB / RAG capabilities
    "preferVectors": true,          // use vector search over document parsing when available
    "storeUri": "",                 // explicit vector store URI (overrides auto-detection)
    "embeddingModel": "auto",       // "auto" | explicit model name
    "chunkStrategy": "symbol"       // "symbol" | "file" | "sliding-window"
  }
}
```

---

## Operational Constraints

> **Standard contracts** are defined in [`ADIK.md` — Standard Contracts](ADIK.md#standard-contracts). The items below are additional operational rules for the running orchestrator.

- **Language-specific output is self-contained.** Each generated SDK package includes its own `README`, type definitions, and serialization helpers so it can be published independently.
- **The MCP server is optional.** Teams that do not need remote orchestration can omit the MCP component entirely.
- **Vector mode degrades gracefully.** When no vector DB is available, the adik falls back to document mode without loss of functionality.
- **Vectors are never required.** All core functionality works in document mode. Vector mode is an optimisation for large codebases and environments that already invest in RAG infrastructure.
- **frameworkHints are inferred, not required.** If the caller does not supply hints, the Codebase Analyst Agent infers them from `architecture.md`, package manifests, and existing agent/skill files.
- **Crosstailing is prevented by state tracking.** Each run records a dev-state snapshot in `adik.env.json` so the next run can detect and report stale artifacts before writing anything.
- **Implementation mode is recorded.** The startup mode (`blanket` or `guided`) and any guidance provided is saved in `adik.env.json` and re-applied on subsequent runs.
- **Registry partitioning is automatic.** For large projects, the Codebase Analyst Agent automatically switches from a monolithic `Registry.md` to a partitioned `Registry.index.md` + domain files model. The `partitionStrategy` option (`auto` / `manual` / `file`) controls domain assignment. This is transparent to downstream agents and skills.
- **Every build is auditable.** The Builder Agent appends a structured NDJSON entry to `adik.audit.log` after each build, recording the commit, registry hash, validation status, and exit status for full traceability.

---

## Eject Protocol

To remove the adik cleanly from a target repository:

```bash
# Preview what would be removed (no changes made)
python3 scripts/adik-eject.py --target . --dry-run

# Eject ADIK framework files (preserves generated sdk/)
python3 scripts/adik-eject.py --target . --confirm

# Eject everything including generated SDKs
python3 scripts/adik-eject.py --target . --confirm --remove-sdk
```

**Non-interactive / CI eject:**

```bash
ADIK_EJECT=true python3 scripts/adik-eject.py --target .
ADIK_EJECT=true ADIK_EJECT_SDK=true python3 scripts/adik-eject.py --target .
```

What the eject script removes:
- ADIK framework files: `ADIK.md`, `ADIK.orchestrator.md`, `Registry.md`, `Registry.index.md`, `Registry.*.md`, `adik.env.json`, `adik.config.json`, `adik.audit.log`
- ADIK directories: `agents/`, `skills/`, `mcp/`, `vectors/`, `scripts/`
- ADIK context blocks from: `.github/copilot-instructions.md`, `CLAUDE.md`, `agents.md` (blocks only — file content outside the guard markers is preserved)
- Generated `sdk/` directory (only with `--remove-sdk`)

What the eject script **never** touches:
- Source code files
- Any file content outside an ADIK guard block
- Repository-level configuration (`.git/`, CI workflows unrelated to ADIK)

---

## Related Files

| File | Role |
|---|---|
| `ADIK.md` | Standard definition — what ADIK is, what an adik is, contracts |
| `Registry.md` | Single source of truth for all exported symbols (monolithic) |
| `Registry.index.md` | Master index for partitioned registries (auto-created for large projects) |
| `Registry.<domain>.md` | Domain-scoped registry partition (auto-created) |
| `adik.config.json` | Configuration including vector options, tier-2 languages, registry mode |
| `adik.env.json` | Auto-generated: env capabilities, inferred frameworkHints, dev-state snapshot, startupMode |
| `adik.audit.log` | Auto-generated: append-only NDJSON build audit trail (one entry per build) |
| `CLAUDE.md` | Created/updated: ADIK context for Claude-based sessions |
| `agents.md` | Created/updated: agent and skill registry for agentic sessions |
| `.github/copilot-instructions.md` | Created/updated: ADIK context for GitHub Copilot |
| `.github/workflows/adik-self-deploy.yml` | CI/CD self-deployment workflow (optional) |
| `vectors/` | Bundled or generated vector embeddings (optional; managed by vectorize.skill.md) |
| `agents/codebase-analyst.agent.md` | Env probe, framework inference, dev-state check, symbol analysis |
| `agents/builder.agent.md` | Orchestrates SDK generation across languages |
| `skills/sdk-builder.skill.md` | Generates tier-1 SDK packages (TypeScript, Python, C#) |
| `skills/sdk-builder-tier2.skill.md` | Generates tier-2 SDK packages (Go, Java, Kotlin — opt-in) |
| `skills/sdk-consumer.skill.md` | Generates framework-idiomatic consumption boilerplate |
| `skills/registry-validator.skill.md` | Validates Registry schema before every SDK generation run |
| `skills/vectorize.skill.md` | Handles all vector embedding and upsert operations |
| `scripts/adik-embed.py` | Deterministic self-embedding script (manages ADIK guard blocks) |
| `scripts/adik-eject.py` | Clean uninstall / eject script |
| `mcp/adik-mcp-server.md` | MCP server for external agent integration |
