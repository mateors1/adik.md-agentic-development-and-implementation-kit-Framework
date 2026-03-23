# ADIK.orchestrator.md — Operational Orchestrator

> **Version:** 1.0.0
> **Role:** Specialized Orchestrator — the brain inside every adik
> **Scope:** Deployed as part of every adik into target repositories
> **Standard:** See [`ADIK.md`](ADIK.md) for the standard definition. See [`docs/specification/standard.md`](docs/specification/standard.md) for the formal specification.

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
> When this orchestrator is first invoked in a new project (i.e., this is the first run and no `adik.env.json` exists), **before taking any implementation action**, it must perform the following sequence.

### Pre-flight: Empty-Project Detection

Before presenting the startup prompt, the orchestrator **must** scan the target directory for
user-authored source files (any file with a recognised source extension or package manifest
outside ADIK-owned directories). If **no source files are found**:

> **ADIK Empty-Project Prompt:**
>
> I've deployed the ADIK framework artifacts into this directory, but I don't detect any
> project source code yet.
>
> **ADIK generates SDKs *from* existing source code** — it does not create application code
> itself. To proceed, you can either:
>
> 1. **Point me at an existing project** — provide the path to a repository that already
>    contains your API, service, or library source code and I will analyse it.
> 2. **Add source code first** — create your application code (routes, models, controllers,
>    etc.) in this directory, then invoke me again and I will generate the SDK from it.
> 3. **Scaffold a starter project** — if you'd like me to create a minimal starter project
>    structure (e.g., a basic Express/FastAPI/ASP.NET skeleton) so you have something to
>    generate an SDK from, tell me and I'll set it up.
>
> *Which would you like?*
>
> *(Respond with **1**, **2**, **3**, or describe what you need.)*

On receiving **1**: re-run the startup protocol against the provided path.  
On receiving **2**: halt and wait for the user to add code, then re-invoke.  
On receiving **3**: generate a minimal, idiomatic starter project in the target directory,
write `adik.env.json` with `startupMode: "scaffolded"`, then proceed to the normal startup
prompt below.  
On receiving a free-form response: interpret it as guided requirements and proceed accordingly.

> **Critical:** The orchestrator must **never** silently proceed to SDK generation when the
> target directory contains no source code. Doing so would produce empty or broken SDK output
> and confuse the user.

---

### Startup Prompt (requires source code present)

When source files **are** detected (or after scaffolding completes):

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

## Pipeline Execution Contract

> **⚠️ CRITICAL — READ BEFORE EXECUTING ANY STEP**
>
> Every step in this pipeline produces **real files written to disk**. The agent executing
> each step must **actually create the files** described in the step's output specification —
> not just describe them, plan them, or list them in a report.
>
> **"Invoking a skill"** means: read the skill file, follow its generation rules, and
> **write every output file to disk** using the filesystem tools available in your
> environment (`create_file`, `write_file`, `fs.writeFile`, or equivalent).
>
> **Common failure mode:** The agent populates `Registry.md`, writes `adik.env.json`,
> generates the validation report, and self-embeds context files — but stops before
> writing actual SDK source code (`.ts`, `.py`, `.cs` files) to `sdk/`. This is
> **incomplete**. The pipeline is only successful when SDK source code files exist on
> disk and are importable/compilable.

### Pipeline Completion Checklist

After the full pipeline runs, the following **must** exist on disk:

| Artifact | Location | Created by |
|---|---|---|
| Environment probe | `adik.env.json` | Step 0 |
| Symbol registry | `Registry.md` (or partitions) | Step 1 |
| Validation report | `sdk/VALIDATION_REPORT.md` | Step 2 |
| **SDK source code** | `sdk/typescript/src/*.ts` | **Step 3 — Builder** |
| **SDK source code** | `sdk/python/<pkg>/*.py` | **Step 3 — Builder** |
| **SDK source code** | `sdk/csharp/*.cs` | **Step 3 — Builder** |
| Build report | `sdk/BUILD_REPORT.md` | Step 3 |
| Context files updated | `.github/copilot-instructions.md`, `CLAUDE.md`, `agents.md` | Step 4 |

> **If `sdk/<language>/` directories are empty or missing after step 3, the pipeline has
> failed.** The orchestrator must not proceed to step 4 and must report the failure.

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
  ├─► [3] Builder Agent               → reads Registry, WRITES ACTUAL SDK SOURCE CODE
  │         (agents/builder.agent.md)
  │         │
  │         ├─► SDK Builder Skill     → WRITES .ts / .py / .cs files to sdk/<lang>/
  │         │     (skills/sdk-builder.skill.md)
  │         │     MUST create: package manifests, client code, model files, type files
  │         │
  │         ├─► SDK Builder Tier-2    → WRITES Go / Java / Kotlin files (opt-in)
  │         │     (skills/sdk-builder-tier2.skill.md)
  │         │     only invoked when tier2Languages is configured in adik.config.json
  │         │
  │         └─► SDK Consumer Skill    → WRITES example files, boilerplate, DI wiring
  │               (skills/sdk-consumer.skill.md)
  │               (uses inferred frameworkHints from adik.env.json)
  │
  │    ──► GATE: verify sdk/<language>/ directories contain source code files.
  │         If empty → FAIL. Do not proceed.
  │
  ├─► [4] Self-Embedding              → inject ADIK context into project files
  │         python3 scripts/adik-embed.py --action upsert --target .
  │         files: .github/copilot-instructions.md, CLAUDE.md, agents.md
  │
  └─► [5] MCP Server                  → exposes ADIK capabilities to external agents
            (mcp/adik_mcp_server.py — run: python mcp/adik_mcp_server.py)
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

If no source files are found for the configured include patterns, the run must stop after issuing
an explicit warning. In this case, the orchestrator must not proceed to SDK generation and must
ask the user to either:

1. Point ADIK at the correct project/repository that contains source code, or
2. Add source code first, then re-run analysis and generation.

Deploying ADIK into an empty folder installs only ADIK artifacts. SDK code is generated only
after successful analysis of a real codebase.

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

### Step 3 — SDK Generation (writes actual source code)

> **⚠️ This is the step that produces the actual SDK.** If this step completes but `sdk/`
> directories are empty, the pipeline has failed.

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

**What "invoke the SDK Builder Skill" means concretely:**

For each configured language, the agent must:

1. Read every symbol from `Registry.md` (classes, interfaces, enums, endpoints, errors).
2. **Create real source code files** on disk — one file per model/class, a client file,
   barrel exports, type definitions, error classes.
3. **Create a package manifest** (`package.json`, `pyproject.toml`, `.csproj`).
4. **Create a README** with a quick-start usage example.

Example: for a registry with 3 endpoints, 5 models, and 2 enums in TypeScript mode, step 3
must produce at minimum:

```
sdk/typescript/
├── package.json                  ← real file with name, version, dependencies
├── tsconfig.json                 ← real file with compiler options
├── README.md                     ← real file with usage example
└── src/
    ├── index.ts                  ← barrel export (real code)
    ├── client.ts                 ← HTTP client with 3 typed methods (real code)
    ├── models/
    │   ├── Model1.ts             ← actual TypeScript interface/class (real code)
    │   ├── Model2.ts             ← ...
    │   ├── Model3.ts
    │   ├── Model4.ts
    │   ├── Model5.ts
    │   └── index.ts
    ├── types/
    │   ├── Enum1.ts              ← actual TypeScript enum (real code)
    │   ├── Enum2.ts
    │   └── index.ts
    └── errors/
        └── index.ts
```

**If none of these files exist after this step, the pipeline has not completed.**

### Post-Step-3 Verification Gate

After the Builder Agent finishes, the orchestrator **must** verify:

```
FOR EACH language IN sdkLanguages + tier2Languages:
  CHECK: sdk/<language>/ directory exists
  CHECK: sdk/<language>/ contains at least one source code file (.ts, .py, .cs, .go, .java, .kt)
  CHECK: sdk/<language>/ contains a package manifest
  IF any check fails → REPORT FAILURE and re-invoke the Builder Agent for that language
```

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

> See [`README.md`](README.md) for the full repository structure and [`docs/getting-started/quickstart-guide.md`](docs/getting-started/quickstart-guide.md) for a walkthrough.

Key paths the orchestrator writes to:

| Path | Created by |
|---|---|
| `Registry.md` / `Registry.<domain>.md` | Codebase Analyst (step 1) |
| `adik.env.json` | Codebase Analyst (step 0) |
| `adik.audit.log` | Builder Agent (step 3) |
| `sdk/<language>/` | Builder Agent (step 3) |
| `.github/copilot-instructions.md`, `CLAUDE.md`, `agents.md` | Self-Embedding (step 4) |

---

## Configuration

The orchestrator reads `adik.config.json` from the repository root. If absent, all defaults apply.

> **Full schema and field reference:** [`docs/getting-started/configuration.md`](docs/getting-started/configuration.md)

Key defaults: tier-1 languages `[typescript, python, csharp]`, output to `./sdk`, auto project-type detection, auto registry partitioning above 500 symbols.

---

## Eject

One command removes the entire adik without touching source code:

```bash
python3 scripts/adik-eject.py --target . --dry-run    # preview
python3 scripts/adik-eject.py --target . --confirm     # eject (keeps sdk/)
python3 scripts/adik-eject.py --target . --confirm --remove-sdk  # eject all
```

> **Details:** See `scripts/adik-eject.py --help` or [`docs/getting-started/quickstart-guide.md`](docs/getting-started/quickstart-guide.md#step-7--eject-if-needed).

---

## Operational Constraints

> Standard contracts are in [`ADIK.md` — Standard Contracts](ADIK.md#standard-contracts). Additional operational rules:

- Each SDK package is self-contained (own README, types, serialization helpers).
- MCP server is optional. Vector mode degrades gracefully. Vectors are never required.
- `frameworkHints` are inferred automatically; explicit config is optional.
- Dev-state tracking in `adik.env.json` prevents crosstailing (stale artifact accumulation).
- Startup mode is recorded and re-applied on subsequent runs.
- Registry partitioning is automatic and transparent to downstream agents.
- Every build appends an audit entry to `adik.audit.log` (NDJSON).

---

> **Related files:** All agent, skill, script, and registry files are listed in [`ADIK.md`](ADIK.md) and [`docs/getting-started/configuration.md`](docs/getting-started/configuration.md). For the full file tree, see [`README.md`](README.md#repository-structure).
