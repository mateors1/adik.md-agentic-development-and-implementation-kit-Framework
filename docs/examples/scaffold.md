# ADIK Scaffold — Bootstrap the Agentic Development and Implementation Kit

> **What is this?** This is the **ADIK Scaffold** — a single, self-contained master document that
> any AI agent can read to bootstrap the complete ADIK framework into a repository from scratch.
> It contains every template, agent definition, skill definition, script, and configuration needed
> to stand up a fully functional ADIK installation with zero external dependencies.
>
> **Usage:** Give this file to your AI assistant and say:
>
> > *Read `scaffold.md` and bootstrap ADIK into this repository.*
>
> The AI will create all necessary files, configure the pipeline, and run the first analysis.

---

## 1 — Instructions for the AI Agent

Follow these steps **in order** to scaffold ADIK into the target repository.

```
STEP 1 — CREATE DIRECTORY STRUCTURE
  mkdir agents/
  mkdir skills/
  mkdir scripts/
  mkdir mcp/
  mkdir sdk/

STEP 2 — DETECT PROJECT IDENTITY
  Scan the repository to determine:
    {PROJECT_NAME}  — name from package.json / pyproject.toml / *.csproj / repo name
    {PROJECT_TYPE}  — "api" | "service" | "library" (use detection heuristics below)
    {SDK_LANGUAGES} — default: ["typescript", "python", "csharp"]
    {SOURCE_LANG}   — primary language of the source project

STEP 3 — WRITE FRAMEWORK FILES (from templates below)
  Write: ADIK.md                        (Section 3 — replace all {PLACEHOLDERS})
  Write: Registry.md                    (Section 4 — empty registry with markers)
  Write: Registry.index.md              (Section 5 — partitioned index template)
  Write: agents/codebase-analyst.agent.md  (Section 6a)
  Write: agents/builder.agent.md           (Section 6b)
  Write: skills/sdk-builder.skill.md       (Section 7a)
  Write: skills/sdk-builder-tier2.skill.md (Section 7b)
  Write: skills/sdk-consumer.skill.md      (Section 7c)
  Write: skills/registry-validator.skill.md (Section 7d)
  Write: skills/vectorize.skill.md         (Section 7e)
  Write: scripts/adik-embed.py             (Section 8a — FULL SCRIPT)
  Write: scripts/adik-eject.py             (Section 8b — FULL SCRIPT)
  Write: mcp/adik-mcp-server.md            (Section 9)

STEP 4 — CREATE adik.config.json (optional, for customisation)
  {
    "projectType": "auto",
    "sdkLanguages": {SDK_LANGUAGES},
    "tier2Languages": [],
    "outputDir": "./sdk",
    "registryPath": "./Registry.md",
    "syncOnCommit": true,
    "includePatterns": ["src/**/*"],
    "excludePatterns": ["**/*.test.*", "**/*.spec.*"]
  }

STEP 5 — RUN SELF-EMBEDDING
  python3 scripts/adik-embed.py --action upsert --target .

STEP 6 — RUN CODEBASE ANALYSIS
  @agent codebase-analyst
  task: analyse-and-register
  target: ./src
  output: Registry.md

STEP 7 — VALIDATE AND BUILD
  @agent builder
  task: build-sdk
  registry: Registry.md
  languages: {SDK_LANGUAGES}

STEP 8 — VERIFY (see Post-Scaffold Checklist, Section 10)
```

### Project-Type Detection Heuristics

```
IF OpenAPI spec (openapi.yaml / swagger.json) exists
  OR route definitions found (Express routes, FastAPI decorators, ASP.NET controllers)
  → {PROJECT_TYPE} = "api"

ELSE IF message queue consumers / gRPC service definitions / Dockerfile with CMD/ENTRYPOINT
  → {PROJECT_TYPE} = "service"

ELSE IF package manifest present AND no server entry-point detected
  → {PROJECT_TYPE} = "library"

ELSE
  → {PROJECT_TYPE} = "library"   // safe default
```

---

## 2 — ADIK.orchestrator.md Template (Operational Orchestrator)

Create `ADIK.orchestrator.md` in the repository root with the following content. Replace all `{PLACEHOLDERS}`.

````markdown
# ADIK.orchestrator.md — Agentic Development and Implementation Kit

> **Version:** 1.0.0
> **Role:** Implementation Orchestrator
> **Scope:** Drives SDK generation and codebase implementation for {PROJECT_NAME}

---

## Executive Summary

### About ADIK

**ADIK (Agentic Development and Implementation Kit)** is a framework standard for fully automated,
AI-driven SDK generation and maintenance. This file is the implementation orchestrator — it drives
the end-to-end creation of publish-ready SDK packages.

### About This Project

- **Project:** {PROJECT_NAME}
- **Project type:** {PROJECT_TYPE}
- **SDK languages:** {SDK_LANGUAGES}
- **ADIK reach:** src/**/* → Registry.md → sdk/

### Reach of ADIK

| Stage | What ADIK Does |
|---|---|
| **Analysis** | Scans source and populates `Registry.md` with every public symbol |
| **Framework inference** | Detects frameworks in use without manual configuration |
| **SDK generation** | Emits publish-ready packages in configured languages |
| **Consumption boilerplate** | Generates idiomatic usage examples, DI wiring, serialization helpers |
| **Continuous sync** | Re-runs on every commit, regenerating only what changed |
| **Vector search** | Optionally embeds the Registry for semantic symbol lookup |
| **MCP server** | Exposes all capabilities to any connected agentic environment |
| **Context embedding** | Injects itself into context files so the AI always knows ADIK is active |

---

## Implementation Mode — First Question

> **⚠️ REQUIRED STARTUP PROTOCOL**
>
> When ADIK.md is first invoked (no `adik.env.json` exists), ask:
>
> **A) Blanket implementation** — Apply ADIK across all identified areas automatically.
>
> **B) Guided implementation** — Collect constraints and requirements first.

On receiving **A**: proceed with auto-detected configuration. Record `startupMode: "blanket"`.
On receiving **B**: collect requirements. Record in `adik.env.json` under `startupGuidance`.

### Headless / Non-Interactive Mode

| Signal | Effect |
|---|---|
| `ADIK_NON_INTERACTIVE=true` | Skip startup prompt; use `ADIK_STARTUP_MODE` or default to `blanket` |
| `adik.env.json` already exists | Skip startup prompt; re-apply saved `startupMode` |

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
  ├─► [1] Codebase Analyst Agent      → analyse repo, populate Registry.md (or partitions)
  │         (agents/codebase-analyst.agent.md)
  │         output: Registry.md | Registry.index.md + Registry.<domain>.md files
  │
  ├─► [2] Registry Validator Skill    → validate Registry schema before generation
  │         (skills/registry-validator.skill.md)
  │         output: sdk/VALIDATION_REPORT.md
  │         → FAIL aborts SDK generation
  │
  ├─► [3] Builder Agent               → reads Registry, delegates to skills
  │         (agents/builder.agent.md)
  │         │
  │         ├─► SDK Builder Skill     → emits tier-1 SDK packages
  │         │     (skills/sdk-builder.skill.md)
  │         │
  │         ├─► SDK Builder Tier-2    → emits tier-2 packages (opt-in)
  │         │     (skills/sdk-builder-tier2.skill.md)
  │         │
  │         └─► SDK Consumer Skill    → emits boilerplate, classes, serializers
  │               (skills/sdk-consumer.skill.md)
  │
  ├─► [4] Self-Embedding              → inject ADIK context into project files
  │         python3 scripts/adik-embed.py --action upsert --target .
  │
  └─► [5] MCP Server                  → exposes ADIK capabilities to external agents
            (mcp/adik-mcp-server.md)
```

---

## Configuration

ADIK reads from optional `adik.config.json`:

```jsonc
{
  "projectType": "auto",
  "sdkLanguages": ["typescript", "python", "csharp"],
  "tier2Languages": [],
  "tier2Options": {
    "go":     { "modulePath": "", "goVersion": "1.21" },
    "java":   { "groupId": "", "artifactId": "", "javaVersion": "17", "buildTool": "maven" },
    "kotlin": { "groupId": "", "artifactId": "", "javaVersion": "17", "buildTool": "gradle" }
  },
  "outputDir": "./sdk",
  "registryPath": "./Registry.md",
  "registryMode": "auto",
  "partitionThresholdSymbols": 500,
  "partitionThresholdBytes": 204800,
  "vectorizationAdvisoryDismissed": false,
  "mcpPort": 3100,
  "syncOnCommit": true,
  "nonInteractive": false,
  "includePatterns": ["src/**/*"],
  "excludePatterns": ["**/*.test.*", "**/*.spec.*"],
  "vectors": {
    "bundled": false,
    "autoDetect": true,
    "preferVectors": true,
    "storeUri": "",
    "embeddingModel": "auto",
    "chunkStrategy": "symbol"
  }
}
```

---

## Constraints and Principles

- **DRYness via Registry** — no SDK artifact may define a type not first declared in `Registry.md`.
- **ADIK.md never modifies source code** — only generates SDK output and agentic artifacts.
- **Self-embedding is deterministic** — `scripts/adik-embed.py` manages guard blocks idempotently.
- **Registry validation is mandatory** — must pass before SDK generation proceeds.
- **Tier-2 languages are opt-in** — require `tier2Languages` in `adik.config.json`.
- **Vector mode degrades gracefully** — falls back to document mode when no vector DB is available.
- **Crosstailing is prevented** — dev-state snapshots detect stale artifacts across runs.
- **Framework hints are inferred** — no manual configuration needed for boilerplate generation.

---

## Eject Protocol

```bash
# Preview what would be removed
python3 scripts/adik-eject.py --target . --dry-run

# Eject ADIK (keep generated sdk/)
python3 scripts/adik-eject.py --target . --confirm

# Eject everything including sdk/
python3 scripts/adik-eject.py --target . --confirm --remove-sdk
```

---

## Related Files

| File | Role |
|---|---|
| `Registry.md` | Single source of truth for all exported symbols |
| `Registry.index.md` | Master index for partitioned registries |
| `adik.config.json` | Configuration |
| `adik.env.json` | Auto-generated env capabilities and dev state |
| `agents/codebase-analyst.agent.md` | Codebase analysis and registry population |
| `agents/builder.agent.md` | SDK generation orchestration |
| `skills/sdk-builder.skill.md` | Tier-1 SDK generation (TS, Python, C#) |
| `skills/sdk-builder-tier2.skill.md` | Tier-2 SDK generation (Go, Java, Kotlin) |
| `skills/sdk-consumer.skill.md` | Consumption boilerplate generation |
| `skills/registry-validator.skill.md` | Registry schema validation |
| `skills/vectorize.skill.md` | Vector embedding and upsert |
| `scripts/adik-embed.py` | Deterministic self-embedding |
| `scripts/adik-eject.py` | Clean uninstall |
| `mcp/adik-mcp-server.md` | MCP server definition |
````

---

## 3 — Registry.md Template

Create `Registry.md` in the repository root:

````markdown
# Registry.md — ADIK Symbol Registry

> **Maintained by:** Codebase Analyst Agent (`agents/codebase-analyst.agent.md`)
> **Consumed by:** Builder Agent (`agents/builder.agent.md`), SDK Builder Skill, SDK Consumer Skill
> **Principle:** Every exported symbol, endpoint, schema, and type used by any ADIK-generated artifact MUST be declared here first. This is the single source of truth that ensures DRYness across all SDK languages and consumption artifacts.

---

## Project Metadata

```yaml
name: "{PROJECT_NAME}"
version: ""
projectType: "{PROJECT_TYPE}"
sourceLanguage: ""
lastAnalysed: ""
lastAnalysedCommit: ""
sdkLanguages:
  - typescript
  - python
  - csharp
vectors:
  bundled: false
  storeUri: ""
  lastVectorised: ""
  embeddingModel: ""
```

---

## Registry Format

Each section below follows a consistent schema so agents can parse and consume entries programmatically.

### Symbol Entry Schema

```yaml
id: string                  # unique stable identifier (e.g. "fn:getUserById")
kind: function | class | interface | enum | schema | endpoint | type
name: string                # canonical name as it appears in the source
namespace: string           # module / package / namespace path
signature: string           # full type signature (language-agnostic description)
description: string         # one-sentence description
parameters:
  - name: string
    type: string
    required: boolean
    description: string
returns:
  type: string
  description: string
deprecated: boolean
since: string               # version or commit when this symbol was introduced
tags: [string]
```

---

## Endpoints

> Populated when `projectType: api` or `projectType: service`.

<!-- ADIK:ENDPOINTS:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
<!-- ADIK:ENDPOINTS:END -->

---

## Classes

> Populated for all project types.

<!-- ADIK:CLASSES:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
<!-- ADIK:CLASSES:END -->

---

## Interfaces and Types

> Abstract contracts and type aliases used across the SDK.

<!-- ADIK:INTERFACES:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
<!-- ADIK:INTERFACES:END -->

---

## Schemas

> JSON Schema / OpenAPI / Protobuf definitions for request and response bodies.

<!-- ADIK:SCHEMAS:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
<!-- ADIK:SCHEMAS:END -->

---

## Enumerations

> Named sets of constant values.

<!-- ADIK:ENUMS:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
<!-- ADIK:ENUMS:END -->

---

## Functions and Methods

> Standalone exported functions and notable class methods.

<!-- ADIK:FUNCTIONS:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
<!-- ADIK:FUNCTIONS:END -->

---

## Error Catalogue

> All named error / exception types that the SDK must surface to consumers.

<!-- ADIK:ERRORS:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
<!-- ADIK:ERRORS:END -->

---

## Changelog

> A running log of registry mutations. Append-only.

| Date | Commit SHA | Change Summary |
|---|---|---|
| — | — | Registry initialised |

---

## Usage by Agents and Skills

### Reading the Registry

Agents and skills MUST parse only the content between `ADIK:<SECTION>:START` and `ADIK:<SECTION>:END` markers. Content outside these markers is human documentation and MUST NOT be modified by agents.

### Writing to the Registry

Only the **Codebase Analyst Agent** may write to the auto-generated sections. All writes must:

1. Preserve all existing markers.
2. Append to the Changelog with the current timestamp and commit SHA.
3. Mark deprecated symbols with `deprecated: true` rather than deleting them.

### Consuming the Registry

The **SDK Builder Skill** reads the registry to determine what classes, methods, and types to generate. The **SDK Consumer Skill** reads it to produce idiomatic consumption boilerplate for each target language.
````

---

## 4 — Registry.index.md Template

Create `Registry.index.md` in the repository root:

````markdown
# Registry.index.md — ADIK Partitioned Registry Index

> **Maintained by:** Codebase Analyst Agent (`agents/codebase-analyst.agent.md`)
> **Consumed by:** Builder Agent (`agents/builder.agent.md`), SDK Builder Skill, SDK Consumer Skill
> **Principle:** For large codebases the monolithic `Registry.md` is split into domain-scoped child
> registries. This index is the single entry-point that all agents load first.

---

## Partition Strategy

Registry partitioning is triggered automatically when `Registry.md` exceeds the configured size
threshold (default: **500 symbols** or **200 KB**, whichever is reached first). The Codebase
Analyst Agent detects this during analysis and:

1. Rewrites the monolithic `Registry.md` as `Registry.<domain>.md` files (one per namespace/domain).
2. Creates or updates this file (`Registry.index.md`) as the master index.
3. Prompts the user to enable vectorization if the total symbol count is high.

Agents MUST load `Registry.index.md` first and select only the partitions they need.

---

## Project Metadata

```yaml
name: "{PROJECT_NAME}"
version: ""
projectType: "{PROJECT_TYPE}"
sourceLanguage: ""
lastAnalysed: ""
lastAnalysedCommit: ""
sdkLanguages:
  - typescript
  - python
  - csharp
registryMode: "monolithic"
partitionThresholdSymbols: 500
partitionThresholdBytes: 204800
vectors:
  bundled: false
  storeUri: ""
  lastVectorised: ""
  embeddingModel: ""
```

---

## Partition Table

<!-- ADIK:PARTITIONS:START -->
<!-- Entries are auto-generated by the Codebase Analyst Agent. Do not edit manually. -->
| Domain | File | Symbols | Last Updated |
|---|---|---|---|
| *(monolithic)* | `Registry.md` | — | — |
<!-- ADIK:PARTITIONS:END -->

---

## Partition Naming Convention

```
Registry.md                  ← monolithic (default / small projects)
Registry.index.md            ← master index (present only when partitioned)
Registry.<domain>.md         ← domain partition, e.g.:
  Registry.users.md
  Registry.payments.md
  Registry.shared.md         ← cross-domain types and utilities
```

---

## Reading Rules for Agents

1. **Always load `Registry.index.md` first** to discover partitions and symbol counts.
2. **Load only the partitions relevant to the current task.**
3. **Never load all partitions simultaneously** unless performing a full rebuild.
4. **Resolve cross-partition type references** by querying this index for the owning partition.
5. **When vector mode is active**, prefer semantic queries over partition loading.

---

## Writing Rules for the Codebase Analyst Agent

1. **Partition assignment** is based on the `namespace` field of each symbol entry.
2. **Shared types** (used by more than one domain) go in `Registry.shared.md`.
3. **After writing each partition**, update the Partition Table above.
4. **Trigger vectorization advisory** when conditions are met (see Vectorization Advisory below).
5. **Changelog entries** are written to each child registry's own `## Changelog` section.

---

## Vectorization Advisory

When total symbols ≥ 500 and vector mode is not active:

> ⚠️ Your registry contains **{totalSymbols}** symbols. Loading the full registry on every run
> will become costly. **Recommended:** Enable vectorization via `VECTOR_DB_URL` or `OPENAI_API_KEY`.
> To dismiss permanently, set `"vectorizationAdvisoryDismissed": true` in `adik.config.json`.
````

---

## 5 — Agent Definitions

### 5a — `agents/codebase-analyst.agent.md`

````markdown
# Codebase Analyst Agent — `agents/codebase-analyst.agent.md`

> **Role:** Codebase Analysis Subagent
> **Type:** Analysis Agent
> **Invoked by:** `ADIK.orchestrator.md`
> **Writes to:** `Registry.md` (monolithic) or `Registry.index.md` + `Registry.<domain>.md`
> (partitioned), `adik.env.json`

---

## Purpose

The Codebase Analyst Agent is the intelligence layer of the ADIK framework. It reads the source
repository and produces a structured, language-agnostic representation of every public symbol,
endpoint, type, and schema in `Registry.md`. It is always the first agent to run.

This agent does not generate any SDK code. Its responsibilities are accurate, complete, and
up-to-date population of the Registry, plus environment probing for vector and RAG capabilities.

---

## Inputs

| Input | Source | Required |
|---|---|---|
| Source file tree | Repository (per `includePatterns`) | Yes |
| `adik.config.json` | Repository root | No (defaults apply) |
| Existing `Registry.md` | Repository root | No (absent on first run) |

---

## Outputs

| Output | Description |
|---|---|
| Updated `Registry.md` | All symbols in canonical format (monolithic mode) |
| Updated `Registry.index.md` + partitions | Domain-partitioned files (auto-triggered by size) |
| `adik.env.json` | Env capabilities, frameworkHints, dev-state snapshot |

---

## Execution Protocol

```
1. READ adik.config.json (apply defaults if absent)
2. PROBE environment for vector capabilities → WRITE adik.env.json
3. PERFORM development state check → WRITE state fields to adik.env.json
4. DETECT projectType using heuristics:
     OpenAPI / route definitions → "api"
     Message queues / gRPC / Dockerfile → "service"
     Package manifest, no server → "library"
5. DETECT sourceLanguage
6. INFER frameworkHints from architecture.md, package manifests, existing agents/skills
     → WRITE to adik.env.json
7. SCAN source files matching includePatterns, excluding excludePatterns
8. EXTRACT symbols per language strategy:
     TypeScript: parse exports, JSDoc, route definitions
     Python: parse __all__, docstrings, route decorators
     C#: parse public declarations, XML docs, controller actions
     OpenAPI: parse paths + schemas directly
9. COUNT total symbols
10. DETERMINE registryMode:
      IF totalSymbols >= 500 OR fileSize >= 200KB → "partitioned"
      ELSE → "monolithic"
11. MERGE/WRITE symbols into Registry (monolithic or partitioned)
12. CHECK and emit vectorization advisory if conditions met
13. IF vectorMode = "active": INVOKE skills/vectorize.skill.md
14. REPORT summary
```

---

## Error Handling

| Condition | Action |
|---|---|
| No source files found | Warn and exit; do not modify Registry |
| Source language cannot be detected | Default to `unknown`; warn user |
| Registry parse error | Abort write; preserve existing Registry |
| Symbol with conflicting `id` | Log conflict; keep most recent version |
| Vector DB probe fails | Set vectorMode = "inactive"; continue in document mode |
| Development state mismatch | Log warnings; do not abort |
````

### 5b — `agents/builder.agent.md`

````markdown
# Builder Agent — `agents/builder.agent.md`

> **Role:** SDK Builder
> **Type:** Orchestrator Agent
> **Invoked by:** `ADIK.orchestrator.md`
> **Delegates to:** `skills/registry-validator.skill.md`, `skills/sdk-builder.skill.md`,
> `skills/sdk-builder-tier2.skill.md` (opt-in), `skills/sdk-consumer.skill.md`

---

## Purpose

The Builder Agent reads the fully populated Registry, validates it via the Registry Validator
Skill, then coordinates the SDK Builder and SDK Consumer skills to produce complete, publish-ready
SDK packages in every configured target language.

---

## Inputs

| Input | Source | Required |
|---|---|---|
| `Registry.md` or `Registry.index.md` | Repository root | Yes |
| `adik.config.json` | Repository root | No |
| `adik.env.json` | Repository root | No |
| `projectType` | Registry metadata | Yes |
| `sdkLanguages` | Config or Registry | Yes |
| `tier2Languages` | Config | No (default: empty) |

---

## Outputs

| Output | Path | Description |
|---|---|---|
| Validation report | `sdk/VALIDATION_REPORT.md` | Registry validation result |
| TypeScript SDK | `sdk/typescript/` | Full TS package |
| Python SDK | `sdk/python/` | Python package |
| C# SDK | `sdk/csharp/` | .NET package |
| Go / Java / Kotlin | `sdk/<lang>/` | Tier-2 (opt-in) |
| Build report | `sdk/BUILD_REPORT.md` | Summary of all generated artifacts |

---

## Execution Protocol

```
1. RESOLVE registry
     IF Registry.index.md exists → partitioned mode
     ELSE → Registry.md (monolithic)

2. ASSERT registry exists
     IF missing → ABORT; prompt user to run codebase-analyst first

3. INVOKE skills/registry-validator.skill.md
     IF FAIL → ABORT; log path to VALIDATION_REPORT.md
     IF WARN → continue; note in BUILD_REPORT.md

4. READ adik.env.json for vectorMode and frameworkHints

5. FOR EACH language IN sdkLanguages (tier-1):
     INVOKE sdk-builder.skill → sdk/<language>/
     INVOKE sdk-consumer.skill → sdk/<language>/examples/, boilerplate/

6. IF tier2Languages is non-empty:
     FOR EACH language IN tier2Languages:
       INVOKE sdk-builder-tier2.skill → sdk/<language>/

7. WRITE sdk/BUILD_REPORT.md

8. POST-GENERATION TYPE CHECK (advisory):
     TypeScript → tsc --noEmit
     Python → mypy (if available)
     C# → dotnet build (if available)
     Go → go build ./...
     Java / Kotlin → gradle/maven build

9. RUN self-embedding:
     python3 scripts/adik-embed.py --action upsert --target .
```

---

## Error Handling

| Condition | Action |
|---|---|
| Registry empty or missing | Abort; prompt to run codebase-analyst |
| Registry validator FAIL | Abort; do not generate SDK files |
| Tier-1 skill fails | Log error; continue with remaining languages |
| Tier-2 skill fails | Log error; do not abort tier-1 |
| Unknown tier-2 language | Log warning; skip |
| Output dir exists | Merge: overwrite generated, preserve manual files |
| `adik-embed.py` not found | Log warning; skip self-embedding |
| Type-check fails | Log to BUILD_REPORT.md (advisory unless ADIK_STRICT_TYPECHECK=true) |
````

---

## 6 — Skill Definitions

### 6a — `skills/sdk-builder.skill.md`

````markdown
# SDK Builder Skill — `skills/sdk-builder.skill.md`

> **Role:** SDK Code Generation (Tier-1)
> **Invoked by:** `agents/builder.agent.md`
> **Reads from:** `Registry.md`

---

## Purpose

Generates publish-ready SDK packages for a given tier-1 target language (TypeScript, Python, C#)
from the symbols declared in `Registry.md`. Invoked once per language.

---

## Inputs

| Input | Type | Description |
|---|---|---|
| `registry` | path | Path to `Registry.md` |
| `language` | enum | `typescript` \| `python` \| `csharp` |
| `projectType` | enum | `api` \| `service` \| `library` |
| `outputDir` | path | Root output path (default: `./sdk`) |

---

## Output File Structures

**TypeScript:** `sdk/typescript/` — `package.json`, `tsconfig.json`, `src/index.ts`, `src/client.ts`, `src/models/`, `src/types/`, `src/errors/`, `README.md`

**Python:** `sdk/python/` — `pyproject.toml`, `<pkg>/__init__.py`, `<pkg>/client.py`, `<pkg>/models/`, `<pkg>/types.py`, `<pkg>/errors.py`, `README.md`

**C#:** `sdk/csharp/` — `<Pkg>.csproj`, `<Pkg>.sln`, `Client/<Pkg>Client.cs`, `Models/`, `Enums/`, `Exceptions/`, `README.md`

---

## Type Mapping

| Registry Type | TypeScript | Python | C# |
|---|---|---|---|
| `string` | `string` | `str` | `string` |
| `number` | `number` | `float` | `double` |
| `integer` | `number` | `int` | `int` |
| `boolean` | `boolean` | `bool` | `bool` |
| `date` | `Date` | `datetime` | `DateTimeOffset` |
| `array<T>` | `T[]` | `list[T]` | `List<T>` |
| `map<K,V>` | `Record<K,V>` | `dict[K, V]` | `Dictionary<K,V>` |
| `optional<T>` | `T \| undefined` | `T \| None` | `T?` |
| `any` | `unknown` | `Any` | `object` |

---

## SDK Template Selection

```
IF projectType == "api":     → typed HTTP client, one method per endpoint
IF projectType == "service": → typed event/RPC client
IF projectType == "library": → re-export types, thin facade wrapper
```

---

## Execution Protocol

```
1. Read all ADIK:<SECTION>:START/END sections from Registry
2. FOR EACH symbol: map types, apply naming conventions, generate files
3. Generate client (HTTP for api, RPC for service, facade for library)
4. Generate barrel exports and package manifests
5. Write README with quick-start example
```

---

## Error Handling

Unsupported type → map to `any`/`Any`/`object` + warning. Output dir conflict → merge strategy.
````

### 6b — `skills/sdk-builder-tier2.skill.md`

````markdown
# SDK Builder Tier-2 Skill — `skills/sdk-builder-tier2.skill.md`

> **Role:** Tier-2 SDK Code Generation (Go, Java, Kotlin)
> **Invoked by:** `agents/builder.agent.md`
> **Reads from:** `Registry.md` or `Registry.index.md`
> **Opt-in:** Only invoked when language is in `adik.config.json` → `tier2Languages`

---

## Purpose

Generates publish-ready Go modules and Java/Kotlin packages from the ADIK Registry.
Mirrors the contract of `skills/sdk-builder.skill.md` for tier-1 languages.

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `registry` | path | Yes | `Registry.md` or `Registry.index.md` |
| `language` | string | Yes | `go` \| `java` \| `kotlin` |
| `projectType` | string | Yes | `api` \| `service` \| `library` |
| `outputDir` | path | No | Default `./sdk` |
| `options` | object | No | Language-specific from `tier2Options` |

---

## Type Mapping

| Registry Type | Go | Java | Kotlin |
|---|---|---|---|
| `string` | `string` | `String` | `String` |
| `number` | `float64` | `double` | `Double` |
| `integer` | `int` | `int` | `Int` |
| `boolean` | `bool` | `boolean` | `Boolean` |
| `any` | `interface{}` | `Object` | `Any` |
| `array<T>` | `[]T` | `List<T>` | `List<T>` |
| `map<K,V>` | `map[K]V` | `Map<K,V>` | `Map<K,V>` |
| `Date` | `time.Time` | `java.time.Instant` | `java.time.Instant` |
| `Promise<T>` | `(T, error)` | `CompletableFuture<T>` | `Deferred<T>` |

---

## Execution Protocol

```
1. ASSERT language ∈ {go, java, kotlin}
2. READ registry (honor partitioned index)
3. VALIDATE via registry-validator.skill.md → ABORT on FAIL
4. RESOLVE tier2Options for language
5. FOR EACH symbol: map types, apply naming, generate files
6. WRITE output to sdk/<language>/
7. WRITE README with install + quick-start
8. APPEND result to BUILD_REPORT.md
```

---

## Error Handling

| Condition | Action |
|---|---|
| `tier2Languages` not configured | Skill not invoked |
| Unsupported type | Emit `any`/`Object`/`Any` + warning |
| Validation FAIL | Abort output for this language |
````

### 6c — `skills/sdk-consumer.skill.md`

````markdown
# SDK Consumer Skill — `skills/sdk-consumer.skill.md`

> **Role:** SDK Consumption Boilerplate Generation
> **Invoked by:** `agents/builder.agent.md`
> **Reads from:** `Registry.md`, generated SDK packages

---

## Purpose

Generates ready-to-use integration boilerplate: examples, service stubs, adapter classes,
serialization helpers, and DI wiring — everything a developer needs to drop the SDK into an
existing project with zero friction.

---

## Inputs

| Input | Type | Required | Description |
|---|---|---|---|
| `registry` | path | Yes | `Registry.md` |
| `language` | enum | Yes | `typescript` \| `python` \| `csharp` |
| `projectType` | enum | Yes | `api` \| `service` \| `library` |
| `outputDir` | path | Yes | Root output path |
| `frameworkHints` | string[] | No | Auto-inferred from `adik.env.json` if not provided |

---

## Outputs

Per-language `examples/` and `boilerplate/` directories containing:
- `basic-usage` — minimal end-to-end example
- `error-handling` — error handling patterns
- `dependency-injection` — framework-specific DI wiring
- `client-factory` — configured client instance factory
- `retry-wrapper` — retry + exponential backoff
- `serialization-helpers` — JSON serialization utilities

---

## Framework Adapter Generation

| Framework Hint | Generated Artifact |
|---|---|
| `react` | `useMyServiceClient` React hook |
| `nestjs` | `MyServiceModule` and `MyServiceProvider` |
| `fastapi` | `Depends(get_client)` dependency |
| `aspnet` | `IServiceCollection.AddMyServiceClient()` extension |
| `angular` | `MyServiceClientModule` and `MyServiceClientService` |

---

## Error Handling

All examples must compile against the generated SDK. All serialization helpers must round-trip
without data loss. Framework adapter generation is best-effort; unknown hints produce generic
boilerplate.
````

### 6d — `skills/registry-validator.skill.md`

````markdown
# Registry Validator Skill — `skills/registry-validator.skill.md`

> **Role:** Registry Schema Validator
> **Invoked by:** `agents/builder.agent.md` (before every SDK generation run)
> **Reads from:** `Registry.md` or `Registry.index.md`
> **Writes to:** `sdk/VALIDATION_REPORT.md`
> **Purpose:** Validates structural integrity and semantic correctness of all Registry entries
> before SDK generation. Catches hallucinated or malformed type mappings.

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `registry` | path | Yes | `Registry.md` or `Registry.index.md` |
| `strict` | boolean | No | Default `false`. When `true`, warnings become errors |
| `outputDir` | path | No | Default `./sdk` |

---

## Outputs

- `sdk/VALIDATION_REPORT.md` — all violations and warnings
- Exit status: `PASS` | `WARN` | `FAIL`

---

## Validation Rules

### Level 1 — Structural Integrity (blocking)

```
S-001: Matching ADIK:<SECTION>:START and END markers present
S-002: Required metadata fields non-empty (name, version, projectType, sourceLanguage, lastAnalysed, lastAnalysedCommit)
S-003: Symbol required fields present (id, kind, name, namespace, signature)
S-004: Unique symbol IDs (no duplicates)
S-005: Valid kind values (function | class | interface | enum | schema | endpoint | type)
S-006: Valid projectType (api | service | library)
```

### Level 2 — Type Consistency (blocking)

```
T-001: All parameter/return types are known primitives or valid Registry symbol references
T-002: No raw "dict" or "Object" without type parameters
T-003: Cross-partition references resolve to existing symbols (partitioned mode)
T-004: Endpoint symbols have valid HTTP method tags
T-005: Warning if non-deprecated symbol references a deprecated symbol
```

### Level 3 — Semantic Plausibility (warnings)

```
P-001: Warning for empty or single-word descriptions
P-002: Warning for void/void functions without explanatory description
P-003: Warning for inconsistent namespace assignment
P-004: Warning if lastAnalysed > 30 days old
```

---

## Execution Protocol

```
1. LOAD registry (monolithic or all partitions)
2. RUN Level 1 rules → collect violations
3. RUN Level 2 rules → collect violations/warnings
4. RUN Level 3 rules → collect warnings
5. WRITE sdk/VALIDATION_REPORT.md
6. RETURN exitStatus: PASS | WARN | FAIL
```

---

## Error Handling

| Condition | Action |
|---|---|
| Registry file not found | FAIL |
| Partition listed but missing on disk | FAIL |
| YAML parse error | FAIL with line number |
| Output dir not writable | Print report to stdout |
````

### 6e — `skills/vectorize.skill.md`

````markdown
# Vectorize Skill — `skills/vectorize.skill.md`

> **Role:** Registry and Codebase Vectorization
> **Invoked by:** `agents/codebase-analyst.agent.md`
> **Reads from:** `Registry.md`, source files, `adik.env.json`
> **Writes to:** Vector store, `Registry.md` (metadata only)

---

## Purpose

Handles all embedding and vector-store interactions. Isolated from analysis and build pipelines
so teams without a vector DB can safely ignore this file.

Only invoked when `adik.env.json` reports `vectorMode = "active"`.

---

## Inputs

| Input | Source | Required |
|---|---|---|
| `adik.env.json` | Repository root | Recommended |
| `Registry.md` | Repository root | Yes |
| Source file tree | Repository | Yes |

---

## Outputs

| Output | Description |
|---|---|
| Vector store upserts | One embedding per symbol + one per source chunk |
| `Registry.md` metadata | Updates `vectors.storeUri`, `lastVectorised`, `embeddingModel` |

---

## Execution Protocol

```
1. READ adik.env.json → storeUri, embeddingModel, vectorMode
   ASSERT vectorMode = "active"

2. READ Registry.md → extract all symbol entries

3. EMBED REGISTRY SYMBOLS
   FOR EACH symbol:
     Build document: "<id> <kind> <name> <signature> <description>"
     Embed and UPSERT into vector store

4. EMBED CODEBASE (per chunkStrategy: "symbol" | "file" | "sliding-window")
   FOR EACH source file in includePatterns:
     Chunk according to strategy → embed → UPSERT

5. UPDATE Registry.md vectors metadata
```

---

## Error Handling

| Condition | Action |
|---|---|
| `vectorMode != "active"` | Exit immediately with log message |
| Vector store connection fails | Log error; do not update Registry metadata |
| Embedding API fails for a symbol | Skip symbol; continue with rest |
| Rate limited | Retry with exponential backoff (max 5 retries) |
````

---

## 7 — Scripts (Complete Python Source)

### 7a — `scripts/adik-embed.py`

Create this file with executable permissions:

````python
#!/usr/bin/env python3
"""
adik-embed.py — Deterministic ADIK Self-Embedding Script

Manages the ADIK context blocks in:
  - .github/copilot-instructions.md
  - CLAUDE.md
  - agents.md

Uses <!-- ADIK:START --> / <!-- ADIK:END --> guard markers to ensure idempotent,
non-duplicating writes. Safe to run multiple times and across different LLM models.

Usage:
    python3 scripts/adik-embed.py --action upsert --target <path-to-repo>
    python3 scripts/adik-embed.py --action remove --target <path-to-repo>
    python3 scripts/adik-embed.py --action check  --target <path-to-repo>
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ADIK_START_MARKER = "<!-- ADIK:START -->"
ADIK_END_MARKER = "<!-- ADIK:END -->"

# Templates for each target file.  {vars} are filled at runtime.
COPILOT_BLOCK = """\
<!-- ADIK:START -->
## ADIK — Agentic Development and Implementation Kit

This project uses **ADIK** for automated SDK generation and maintenance.

- **Orchestrator:** `ADIK.orchestrator.md` (operational orchestrator)
- **Standard:** `ADIK.md` (standard definition)
- **Registry:** `{registry_path}` (single source of truth for all public symbols)
- **Agents:** `agents/builder.agent.md`, `agents/codebase-analyst.agent.md`
- **Skills:** `skills/sdk-builder.skill.md`, `skills/sdk-consumer.skill.md`,
  `skills/vectorize.skill.md`, `skills/registry-validator.skill.md`
- **Tier-2 Skills:** `skills/sdk-builder-tier2.skill.md` (Go / Java / Kotlin — opt-in)
- **MCP server:** `mcp/adik-mcp-server.md`
- **Build output:** `sdk/` ({sdk_languages})

**Key rules for Copilot:**
- Never define a type in the SDK that is not first declared in `{registry_path}`.
- SDK files in `sdk/` are generated — do not edit them directly; update the source and re-run ADIK.
- To trigger SDK regeneration: `@agent builder task: build-sdk registry: {registry_path}`
- To refresh the registry: `@agent codebase-analyst task: analyse-and-register`
- To eject ADIK: run `python3 scripts/adik-eject.py --target .` or set `ADIK_EJECT=true`
<!-- ADIK:END -->
"""

CLAUDE_BLOCK = """\
<!-- ADIK:START -->
## ADIK — Agentic Development and Implementation Kit

**Executive Summary:** {project_summary}

**Orchestrator:** `ADIK.orchestrator.md`
**Standard:** `ADIK.md`
**Registry:** `{registry_path}`
**SDK output:** `sdk/` ({sdk_languages})
**ADIK reach:** {adik_reach}

**Key rules:**
- `{registry_path}` is the single source of truth. All public symbols must be declared there.
- Files in `sdk/` are generated. Do not edit them manually.
- Run `@agent codebase-analyst task: analyse-and-register` to refresh the registry.
- Run `@agent builder task: build-sdk` to regenerate the SDK after registry changes.
- To eject ADIK cleanly: `python3 scripts/adik-eject.py --target .`
<!-- ADIK:END -->
"""

AGENTS_BLOCK = """\
<!-- ADIK:START -->
## ADIK — SDK Orchestrator

Loaded agents:
- agents/builder.agent.md
- agents/codebase-analyst.agent.md

Loaded skills:
- skills/sdk-builder.skill.md
- skills/sdk-consumer.skill.md
- skills/registry-validator.skill.md
- skills/vectorize.skill.md (loaded on demand when vectorMode is active)
- skills/sdk-builder-tier2.skill.md (loaded on demand when tier2Languages is configured)

Registry: {registry_path}
MCP server: mcp/adik-mcp-server.md
Vector store: {vector_store}
SDK output: sdk/ ({sdk_languages})
<!-- ADIK:END -->
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    """Read file content, returning empty string if file does not exist."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _write(path: Path, content: str) -> None:
    """Write content to file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [written] {path}")


def _upsert_block(existing: str, new_block: str) -> str:
    """
    Insert or replace the ADIK block in `existing`.

    - If no markers are present: append the block.
    - If markers are present: replace the content between them (inclusive).
    - Never duplicates the block.
    """
    start = existing.find(ADIK_START_MARKER)
    end = existing.find(ADIK_END_MARKER)

    if start == -1 and end == -1:
        # No existing block — append with a leading newline separator.
        separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
        return existing + separator + new_block.rstrip() + "\n"

    if start != -1 and end != -1:
        # Replace existing block (inclusive of markers).
        before = existing[:start]
        after = existing[end + len(ADIK_END_MARKER):]
        return before + new_block.rstrip() + "\n" + after.lstrip("\n")

    # Mismatched markers — append safely and warn.
    print(
        "  [warn] Mismatched ADIK markers detected. Appending new block. "
        "Please manually remove stale markers.",
        file=sys.stderr,
    )
    return existing + "\n\n" + new_block.rstrip() + "\n"


def _remove_block(existing: str) -> str:
    """Remove the ADIK block from `existing`, including surrounding blank lines."""
    start = existing.find(ADIK_START_MARKER)
    end = existing.find(ADIK_END_MARKER)

    if start == -1 or end == -1:
        return existing  # Nothing to remove.

    before = existing[:start].rstrip("\n")
    after = existing[end + len(ADIK_END_MARKER):].lstrip("\n")
    return (before + "\n" + after).rstrip() + "\n"


def _has_block(content: str) -> bool:
    return ADIK_START_MARKER in content and ADIK_END_MARKER in content


# ---------------------------------------------------------------------------
# Context gathering
# ---------------------------------------------------------------------------


def _gather_context(target: Path) -> dict:
    """Collect runtime values used in template rendering."""
    import json

    registry_path = "Registry.md"
    sdk_languages = "typescript, python, csharp"
    vector_store = "none"
    project_summary = "[auto-filled on deployment]"
    adik_reach = "src/**/* → Registry.md → sdk/"

    def _safe(value: str) -> str:
        """Sanitize user-supplied strings for safe use in str.format() templates.
        Escapes curly braces to prevent format-string injection."""
        return str(value).replace("{", "{{").replace("}", "}}")

    # Read adik.env.json if present.
    env_file = target / "adik.env.json"
    if env_file.exists():
        try:
            env = json.loads(env_file.read_text(encoding="utf-8"))
            if env.get("vectors", {}).get("storeUri"):
                vector_store = _safe(env["vectors"]["storeUri"])
        except (json.JSONDecodeError, KeyError):
            pass

    # Read adik.config.json if present.
    config_file = target / "adik.config.json"
    if config_file.exists():
        try:
            cfg = json.loads(config_file.read_text(encoding="utf-8"))
            languages = list(cfg.get("sdkLanguages", ["typescript", "python", "csharp"]))
            tier2 = cfg.get("tier2Languages", [])
            if tier2:
                languages += [f"{_safe(l)} (tier-2)" for l in tier2]
            sdk_languages = ", ".join(_safe(l) for l in languages)
            if cfg.get("registryPath"):
                registry_path = _safe(cfg["registryPath"])
            if cfg.get("includePatterns"):
                adik_reach = (
                    ", ".join(_safe(p) for p in cfg["includePatterns"])
                    + f" → {registry_path} → sdk/"
                )
        except (json.JSONDecodeError, KeyError):
            pass

    # Use partitioned index if present.
    if (target / "Registry.index.md").exists():
        registry_path = "Registry.index.md"

    return {
        "registry_path": registry_path,
        "sdk_languages": sdk_languages,
        "vector_store": vector_store,
        "project_summary": project_summary,
        "adik_reach": adik_reach,
    }


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


def action_upsert(target: Path) -> None:
    """Insert or update the ADIK block in all three context files."""
    ctx = _gather_context(target)
    # Values from _gather_context are already brace-escaped via _safe().
    # Do NOT double-escape here.

    files = {
        target / ".github" / "copilot-instructions.md": COPILOT_BLOCK.format(**ctx),
        target / "CLAUDE.md": CLAUDE_BLOCK.format(**ctx),
        target / "agents.md": AGENTS_BLOCK.format(**ctx),
    }

    for path, block in files.items():
        existing = _read(path)
        updated = _upsert_block(existing, block)
        if updated != existing:
            _write(path, updated)
        else:
            print(f"  [up-to-date] {path}")


def action_remove(target: Path) -> None:
    """Remove the ADIK block from all three context files."""
    paths = [
        target / ".github" / "copilot-instructions.md",
        target / "CLAUDE.md",
        target / "agents.md",
    ]
    for path in paths:
        if not path.exists():
            continue
        existing = _read(path)
        updated = _remove_block(existing)
        if updated != existing:
            _write(path, updated)
        else:
            print(f"  [no block found] {path}")


def action_check(target: Path) -> None:
    """Check whether the ADIK block is present in all three context files."""
    paths = {
        ".github/copilot-instructions.md": target / ".github" / "copilot-instructions.md",
        "CLAUDE.md": target / "CLAUDE.md",
        "agents.md": target / "agents.md",
    }
    all_ok = True
    for label, path in paths.items():
        content = _read(path)
        if _has_block(content):
            print(f"  [OK]      {label}")
        else:
            print(f"  [MISSING] {label}")
            all_ok = False
    sys.exit(0 if all_ok else 1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministically manage ADIK self-embedding blocks."
    )
    parser.add_argument(
        "--action",
        choices=["upsert", "remove", "check"],
        required=True,
        help="upsert: insert/update block; remove: strip block; check: verify block present",
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Root directory of the target repository (default: current directory)",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"Error: target directory '{target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"ADIK embed — action={args.action}, target={target}")

    if args.action == "upsert":
        action_upsert(target)
    elif args.action == "remove":
        action_remove(target)
    elif args.action == "check":
        action_check(target)


if __name__ == "__main__":
    main()
````

### 7b — `scripts/adik-eject.py`

Create this file with executable permissions:

````python
#!/usr/bin/env python3
"""
adik-eject.py — ADIK Clean Uninstall / Eject Script

Removes all ADIK-generated and ADIK-owned artifacts from a target repository
so the team can stop using ADIK without leaving stale files behind.

Eject is SAFE by default:
  - Dry-run mode shows what would be deleted without touching anything.
  - Destructive operations require --confirm.
  - Source code is NEVER deleted.
  - Generated SDK directories are removed only when --remove-sdk is supplied.

Usage:
    # Preview what would be ejected
    python3 scripts/adik-eject.py --target <path-to-repo> --dry-run

    # Eject ADIK framework files (keep generated sdk/)
    python3 scripts/adik-eject.py --target <path-to-repo> --confirm

    # Eject everything including generated SDKs
    python3 scripts/adik-eject.py --target <path-to-repo> --confirm --remove-sdk

Environment variables:
    ADIK_EJECT=true   Equivalent to --confirm (enables non-interactive eject in CI)
    ADIK_EJECT_SDK=true  Also remove sdk/ directory (equivalent to --remove-sdk)
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# What gets removed
# ---------------------------------------------------------------------------

# Files that are always candidates for removal (ADIK framework files)
ADIK_FRAMEWORK_FILES = [
    "ADIK.md",
    "Registry.md",
    "Registry.index.md",
    "adik.env.json",
    "adik.config.json",
    # ADIK-owned helper scripts in the scripts/ directory
    "scripts/adik-embed.py",
    "scripts/adik-eject.py",
]

# Glob patterns for domain registry partitions
ADIK_REGISTRY_PATTERNS = ["Registry.*.md"]

# Directories that are always candidates for removal
# NOTE: We intentionally do NOT include the top-level "scripts" directory here
# to avoid deleting non-ADIK scripts owned by the target repository.
ADIK_FRAMEWORK_DIRS = [
    "agents",
    "skills",
    "mcp",
    "vectors",
]

# Generated SDK directory (only removed with --remove-sdk)
ADIK_SDK_DIR = "sdk"

# Context file handling: remove the ADIK block, NOT the entire file
ADIK_CONTEXT_FILES = [
    ".github/copilot-instructions.md",
    "CLAUDE.md",
    "agents.md",
]

ADIK_START_MARKER = "<!-- ADIK:START -->"
ADIK_END_MARKER = "<!-- ADIK:END -->"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _remove_adik_block(content: str) -> Tuple[str, bool]:
    """Remove the ADIK block from file content. Returns (updated_content, was_modified)."""
    start = content.find(ADIK_START_MARKER)
    end = content.find(ADIK_END_MARKER)

    if start == -1 or end == -1:
        return content, False

    before = content[:start].rstrip("\n")
    after = content[end + len(ADIK_END_MARKER):].lstrip("\n")
    updated = (before + "\n" + after).rstrip() + "\n"
    return updated, True


def _collect_removals(target: Path, remove_sdk: bool, keep_scripts: bool = False) -> List[Tuple[str, Path, str]]:
    """
    Collect all paths that would be removed.
    Returns list of (action, path, reason) tuples.
    action: "delete_file" | "delete_dir" | "strip_block"
    """
    actions = []

    # Framework files
    for fname in ADIK_FRAMEWORK_FILES:
        p = target / fname
        if p.exists():
            actions.append(("delete_file", p, "ADIK framework file"))

    # Registry partition files (exclude files already added from ADIK_FRAMEWORK_FILES)
    already_collected = {p for _, p, _ in actions}
    for pattern in ADIK_REGISTRY_PATTERNS:
        for p in sorted(target.glob(pattern)):
            if p not in already_collected:
                actions.append(("delete_file", p, "ADIK registry partition"))
                already_collected.add(p)

    # Framework directories
    for dname in ADIK_FRAMEWORK_DIRS:
        if keep_scripts and dname == "scripts":
            continue
        p = target / dname
        if p.exists() and p.is_dir():
            actions.append(("delete_dir", p, "ADIK framework directory"))

    # SDK directory (optional)
    if remove_sdk:
        sdk_path = target / ADIK_SDK_DIR
        if sdk_path.exists() and sdk_path.is_dir():
            actions.append(("delete_dir", sdk_path, "ADIK generated SDK (--remove-sdk)"))

    # Context files: strip block only
    for cfile in ADIK_CONTEXT_FILES:
        p = target / cfile
        if p.exists():
            content = p.read_text(encoding="utf-8")
            if ADIK_START_MARKER in content:
                actions.append(("strip_block", p, "ADIK context block"))

    return actions


def _print_plan(actions: List[Tuple[str, Path, str]]) -> None:
    print("\nEject plan:")
    print("-" * 60)
    for action, path, reason in actions:
        verb = {
            "delete_file": "DELETE FILE",
            "delete_dir": "DELETE DIR ",
            "strip_block": "STRIP BLOCK",
        }[action]
        print(f"  {verb}  {path}  ({reason})")
    print("-" * 60)
    print(f"  {len(actions)} operation(s) total.\n")


def _execute_plan(
    actions: List[Tuple[str, Path, str]], dry_run: bool
) -> None:
    for action, path, reason in actions:
        if dry_run:
            print(f"  [dry-run] would {action} → {path}")
            continue

        try:
            if action == "delete_file":
                path.unlink()
                print(f"  [deleted]  {path}")
            elif action == "delete_dir":
                shutil.rmtree(path)
                print(f"  [deleted]  {path}/")
            elif action == "strip_block":
                content = path.read_text(encoding="utf-8")
                updated, changed = _remove_adik_block(content)
                if changed:
                    path.write_text(updated, encoding="utf-8")
                    print(f"  [stripped] {path}")
                else:
                    print(f"  [skipped]  {path} (no block found)")
        except OSError as exc:
            print(f"  [error]    {path}: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cleanly eject ADIK from a repository."
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Root directory of the target repository (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without making any changes",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required to execute destructive operations (or set ADIK_EJECT=true)",
    )
    parser.add_argument(
        "--remove-sdk",
        action="store_true",
        help="Also remove the generated sdk/ directory (or set ADIK_EJECT_SDK=true)",
    )
    parser.add_argument(
        "--keep-scripts",
        action="store_true",
        help=(
            "Preserve the scripts/ directory during eject. "
            "Recommended when you want to verify the eject or re-run the script afterwards."
        ),
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"Error: target directory '{target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Honour environment variables for non-interactive / CI usage.
    confirmed = args.confirm or os.environ.get("ADIK_EJECT", "").lower() == "true"
    remove_sdk = args.remove_sdk or os.environ.get("ADIK_EJECT_SDK", "").lower() == "true"
    keep_scripts = args.keep_scripts or os.environ.get("ADIK_EJECT_KEEP_SCRIPTS", "").lower() == "true"
    dry_run = args.dry_run

    print(f"ADIK Eject — target={target}")
    print(f"  dry-run={dry_run}, confirmed={confirmed}, remove-sdk={remove_sdk}, keep-scripts={keep_scripts}\n")

    actions = _collect_removals(target, remove_sdk, keep_scripts)

    if not actions:
        print("Nothing to eject — no ADIK artefacts found.")
        sys.exit(0)

    _print_plan(actions)

    if dry_run:
        print("Dry-run complete. No files were modified.")
        print("Re-run with --confirm to execute.")
        sys.exit(0)

    if not confirmed:
        print(
            "Eject requires --confirm (or ADIK_EJECT=true) to execute.\n"
            "Run with --dry-run first to preview what would be removed.",
        )
        sys.exit(1)

    print("Executing eject...")
    _execute_plan(actions, dry_run=False)
    print("\nADIK has been ejected. Source code was not modified.")
    if keep_scripts:
        print("Note: scripts/ directory was preserved (--keep-scripts).")
    if not remove_sdk:
        print(
            "Note: generated sdk/ directory was preserved. "
            "Re-run with --remove-sdk to delete it."
        )


if __name__ == "__main__":
    main()
````

---

## 8 — MCP Server Definition

Create `mcp/adik-mcp-server.md`:

````markdown
# ADIK MCP Server — `mcp/adik-mcp-server.md`

> **Role:** Model Context Protocol Server
> **Type:** MCP Server Definition
> **Invoked by:** External agentic environments in target codebases
> **Exposes:** All ADIK capabilities as MCP tools

---

## Purpose

Exposes ADIK capabilities as a standard MCP server so developers can drive ADIK from their own
agentic environment — regenerate SDKs, query the registry, scaffold boilerplate remotely.

---

## Server Metadata

```json
{
  "name": "adik-mcp-server",
  "version": "1.0.0",
  "description": "MCP server exposing ADIK SDK generation, registry query, and scaffolding",
  "protocol": "mcp",
  "transport": ["stdio", "http+sse"],
  "defaultPort": 3100
}
```

---

## Tools

### `adik_get_registry`

Returns full or filtered `Registry.md` contents.

**Input:** `{ "section": "all"|"endpoints"|"classes"|..., "filter": "<substring>" }`
**Output:** Markdown string of requested section(s).

### `adik_build_sdk`

Triggers SDK generation for specified languages.

**Input:** `{ "languages": ["typescript", ...], "incremental": false, "outputDir": "./sdk" }`
**Output:** JSON build report summary.

### `adik_analyse_codebase`

Triggers codebase analysis and Registry refresh.

**Input:** `{ "since": "<commit-sha>", "target": "./src" }`
**Output:** `{ "symbolsAdded": N, "symbolsUpdated": N, "symbolsDeprecated": N, "projectType": "...", "commitSha": "..." }`

### `adik_scaffold_boilerplate`

Generates consumption boilerplate for a language/framework.

**Input:** `{ "language": "typescript"|"python"|"csharp", "framework": "react"|..., "outputDir": "...", "symbols": [...] }`
**Output:** JSON array of file actions.

### `adik_get_symbol`

Look up a specific symbol by ID or name.

**Input:** `{ "id": "fn:getUserById" }` or `{ "name": "getUserById" }`
**Output:** YAML symbol entry.

### `adik_get_build_report`

Returns the most recent `sdk/BUILD_REPORT.md`.

**Input:** `{ "language": "typescript" }` (optional filter)
**Output:** Markdown build report.

### `adik_vector_search`

Semantic similarity search (only when vector mode is active).

**Input:** `{ "query": "...", "scope": "registry"|"codebase"|"all", "topK": 10, "filter": {...} }`
**Output:** JSON array of `{ id, kind, name, score, excerpt }`.

---

## Resources

| URI | Description |
|---|---|
| `adik://registry` | Full `Registry.md` contents |
| `adik://registry/{section}` | Single registry section |
| `adik://sdk/build-report` | Most recent build report |
| `adik://config` | Current `adik.config.json` |
| `adik://env` | Current `adik.env.json` |

---

## Prompts

### `adik_sdk_overview`
Returns SDK overview: project type, languages, symbol counts, build report link.

### `adik_onboard_consumer`
Step-by-step onboarding for a developer using the SDK: install, init, first call.

---

## Running the Server

**stdio (default):**
```json
{
  "mcpServers": {
    "adik": {
      "command": "npx",
      "args": ["adik-mcp-server", "--registry", "./Registry.md"],
      "env": { "ADIK_OUTPUT_DIR": "./sdk" }
    }
  }
}
```

**HTTP + SSE:**
```bash
npx adik-mcp-server --transport http --port 3100 --registry ./Registry.md
```

---

## Security

- Read-only by default. Write ops require `--allow-writes` or `ADIK_ALLOW_WRITES=true`.
- HTTP mode: authenticate via `ADIK_AUTH_TOKEN` (Bearer token).
- Never exposes source code — only structured Registry data and SDK artifacts.
````

---

## 9 — Post-Scaffold Checklist

After scaffolding is complete, verify:

```
[ ] ADIK.md exists in repository root with correct {PROJECT_NAME} and {PROJECT_TYPE}
[ ] Registry.md exists with all 8 section markers:
      ADIK:ENDPOINTS:START/END
      ADIK:CLASSES:START/END
      ADIK:INTERFACES:START/END
      ADIK:SCHEMAS:START/END
      ADIK:ENUMS:START/END
      ADIK:FUNCTIONS:START/END
      ADIK:ERRORS:START/END
[ ] Registry.index.md exists with ADIK:PARTITIONS:START/END markers
[ ] agents/codebase-analyst.agent.md exists and is readable
[ ] agents/builder.agent.md exists and is readable
[ ] skills/sdk-builder.skill.md exists
[ ] skills/sdk-builder-tier2.skill.md exists
[ ] skills/sdk-consumer.skill.md exists
[ ] skills/registry-validator.skill.md exists
[ ] skills/vectorize.skill.md exists
[ ] scripts/adik-embed.py exists and runs: python3 scripts/adik-embed.py --action check --target .
[ ] scripts/adik-eject.py exists and runs: python3 scripts/adik-eject.py --target . --dry-run
[ ] mcp/adik-mcp-server.md exists
[ ] .github/copilot-instructions.md contains ADIK:START/END block
[ ] CLAUDE.md contains ADIK:START/END block
[ ] agents.md contains ADIK:START/END block
[ ] sdk/ directory exists (empty until first build)
[ ] adik.config.json exists (optional but recommended)
[ ] No placeholder text remains (all {PROJECT_NAME} etc. replaced)
```

---

*ADIK Scaffold v1.0.0 — Agentic Development and Implementation Kit*
