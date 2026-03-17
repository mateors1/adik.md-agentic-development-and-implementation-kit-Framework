# ADIKBuilderExample.md — Self-Sufficient ADIK Implementation Guide

> **Role:** Scaffolding Reference
> **Audience:** Developers who want to build their own ADIK-like framework from the ground up, without copying this repository.
> **Companion to:** [`ADIKbuilder.md`](../../ADIKbuilder.md) (framework governance) and [`README.md`](../../README.md) (manifesto and usage guide)
> **Location:** `docs/examples/ADIKBuilderExample.md`

---

## What This Document Is

This document is a **complete, self-contained walkthrough** for implementing the entire ADIK framework from scratch. It is the answer to the question: *"I understand the principles — now how do I build my own version?"*

Every decision, every file, and every contract described in this repository is reproduced here as a step-by-step construction guide. Follow it sequentially and you will arrive at a working ADIK implementation that is independent of this repository.

---

## Prerequisites

Before starting, ensure your environment has:

- A text editor or IDE with Markdown support.
- An agentic coding environment (GitHub Copilot, Claude, Cursor, or similar) that can load and execute agent definition files.
- (Optional) A vector database if you want to enable vector mode (Chroma, Qdrant, Weaviate, pgvector, or similar).
- (Optional) An embeddings-capable LLM provider (OpenAI, Anthropic, local model via Ollama) if you want semantic search.

---

## Step 1 — Create the Source Repository Structure

Start with an empty repository (or a new directory inside your existing project):

```
my-adik-framework/
├── MyADIKbuilder.md        ← your framework orchestrator (created in Step 2)
├── ADIK.md                 ← your standard definition (created in Step 3a)
├── ADIK.orchestrator.md    ← your implementation orchestrator (created in Step 3b)
├── Registry.md             ← symbol registry template (created in Step 4)
├── README.md               ← documentation (created in Step 9)
├── agents/
├── skills/
└── mcp/
```

The key principle: **factory + standard + specialized adik**. `MyADIKbuilder.md` is the factory — it stays in this source repo. `ADIK.md` is the standard definition. It produces adiks (self-sustaining agentic SDK bundles) that get deployed into every target codebase, with `ADIK.orchestrator.md` driving the operational pipeline.

---

## Step 2 — Build Your Framework Orchestrator

Create `MyADIKbuilder.md`. This file governs the development and release of your ADIK framework. It is **never deployed** to target repositories.

### Minimum Viable Content

```markdown
# MyADIKbuilder.md — Framework Orchestrator

> **Role:** Source-Repo Orchestrator
> **Scope:** This repository only — not deployed to target repos.

## Purpose

MyADIKbuilder.md governs the development, validation, and release of the
ADIK framework files in this repository.

## Deployable Bundle

The following files are copied into target repositories:

  ADIK.md
  ADIK.orchestrator.md
  Registry.md
  agents/codebase-analyst.agent.md
  agents/builder.agent.md
  skills/sdk-builder.skill.md
  skills/sdk-consumer.skill.md
  skills/vectorize.skill.md        ← only if you implement vector support
  mcp/adik-mcp-server.md           ← only if you implement MCP support

MyADIKbuilder.md itself is NEVER included.

## Framework Evolution Rules

- Adding a new agent/skill: create the file, reference it from ADIK.orchestrator.md, bump patch version.
- Changing the Registry schema: update Registry.md and all agents/skills that read/write it, bump minor version.
- Breaking change to ADIK.md or ADIK.orchestrator.md: bump major version, notify consumers.
- Releasing a new version: after tagging, prompt the user whether to create a separate GitHub repository within the same organisation for internal distribution (see Releasing and Distribution below).

## Releasing and Distribution

When releasing a new bundle version:

1. Increment the version in this file and in `ADIK.md` / `ADIK.orchestrator.md`.
2. Tag the release (`vX.Y.Z`).
3. Update `README.md` with release notes.
4. Run the factory deploy script to assemble and push the bundle:
   ```bash
   python3 scripts/adik-deploy.py --target /path/to/target-repo/
   ```
5. **Prompt the user:** *"Would you like to create a separate GitHub repository within the same organisation to distribute this bundle internally?"*
   - If **yes**: create the repo (see steps below), push only the deployable bundle files, and document the distribution URL in `README.md`.
   - If **no**: distribution is complete via this repository's tags.

### Creating an Internal Distribution Repository

```bash
# Create the repo in your organisation
gh repo create <org>/<repo-name> --description "<description>" --internal --confirm

# Clone, copy bundle, and push
git clone https://github.com/<org>/<repo-name>.git adik-dist-repo
cd adik-dist-repo
cp -r ../ADIK.md ../ADIK.orchestrator.md ../Registry.md ../agents ../skills ../mcp .
git add .
git commit -m "chore: initialise bundle vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

Ensure `MyADIKbuilder.md` and any other source-only files are **never** included in the distribution repo.
```

### What Makes a Good Framework Orchestrator

- Documents the **bundle contents** precisely — so you never accidentally ship the wrong files.
- Defines **versioning rules** — so consumers know when to upgrade.
- Lists **internal contracts** — the cross-file dependencies between agents, skills, and ADIK.orchestrator.md.

---

## Step 3 — Build the Standard Definition and Implementation Orchestrator

Create `ADIK.md` as the standard definition (terminology, contracts, principles) and `ADIK.orchestrator.md` as the operational orchestrator. The orchestrator is the file that lands in every target repository and drives SDK generation.

### Core Sections (ADIK.orchestrator.md)

Every `ADIK.orchestrator.md` must contain:

1. **Purpose** — what the orchestrator does in the target repo.
2. **Framework Hints Inference** — how the framework infers target frameworks from `architecture.md`, package manifests, and existing agent/skill files.
3. **Development State and Crosstailing Prevention** — the dev-state snapshot mechanism.
4. **Project-Type Detection** — the heuristic table (api / service / library).
5. **Orchestration Workflow** — the numbered steps with `@agent` and `@skill` invocations.
6. **Vector and RAG Support** — brief overview, pointing to `skills/vectorize.skill.md`.
7. **File Layout** — the directory tree as deployed in the target repo.
8. **Configuration** — the `adik.config.json` schema.
9. **Constraints and Principles** — the rules the framework enforces.
10. **Related Files** — cross-reference table.

### Minimal ADIK.orchestrator.md Template

```markdown
# ADIK.orchestrator.md — [Your Framework Name]

> **Version:** 1.0.0
> **Role:** Implementation Orchestrator
> **Scope:** Deployed into target repositories

## Purpose

[Your framework name] analyses the target codebase, generates SDK packages,
and keeps them in sync. It infers framework hints automatically and prevents
crosstailing via a development-state snapshot.

## Framework Hints Inference

When frameworkHints is not provided, ADIK reads adik.env.json for hints
inferred from architecture.md, package manifests, and existing agents/skills.

## Development State and Crosstailing Prevention

Before each run, ADIK records a dev-state snapshot to detect config drift.
Stale artifacts are reported in adik.env.json.staleArtifacts.

## Project-Type Detection

| Signal                              | Detected Type |
|-------------------------------------|---------------|
| HTTP endpoints / OpenAPI spec       | api           |
| Message queue / gRPC / Dockerfile   | service       |
| Package manifest, no server entry   | library       |

## Orchestration Workflow

[0] Codebase Analyst Agent  → probe-environment (frameworkHints, dev-state, vector)
[1] Codebase Analyst Agent  → analyse-and-register → Registry.md
    └── [opt] Vectorize Skill → embed Registry + codebase
[2] Builder Agent           → build-sdk using Registry.md
[3] MCP Server              → expose capabilities (optional)

## Configuration (adik.config.json)

{
  "projectType": "auto",
  "sdkLanguages": ["typescript", "python", "csharp"],
  "outputDir": "./sdk",
  "syncOnCommit": true,
  "vectors": {
    "bundled": false,
    "autoDetect": true,
    "preferVectors": true,
    "chunkStrategy": "symbol"
  }
}
```

---

## Step 4 — Build the Symbol Registry Template

Create `Registry.md`. This is the single source of truth for all exported symbols in the target codebase.

### Required Sections

```markdown
# Registry.md — Symbol Registry

## Project Metadata

```yaml
name: ""
version: ""
projectType: ""           # "api" | "service" | "library"
sourceLanguage: ""
lastAnalysed: ""
lastAnalysedCommit: ""
sdkLanguages: [typescript, python, csharp]
vectors:
  bundled: false
  storeUri: ""
  lastVectorised: ""
  embeddingModel: ""
```

## Symbol Entry Schema

```yaml
id: string                # e.g. "fn:getUserById"
kind: function|class|interface|enum|schema|endpoint|type
name: string
namespace: string
signature: string
description: string
parameters: [{name, type, required, description}]
returns: {type, description}
deprecated: boolean
since: string
tags: [string]
```

## Endpoints
<!-- ADIK:ENDPOINTS:START -->
<!-- ADIK:ENDPOINTS:END -->

## Classes
<!-- ADIK:CLASSES:START -->
<!-- ADIK:CLASSES:END -->

## Interfaces and Types
<!-- ADIK:INTERFACES:START -->
<!-- ADIK:INTERFACES:END -->

## Schemas
<!-- ADIK:SCHEMAS:START -->
<!-- ADIK:SCHEMAS:END -->

## Enumerations
<!-- ADIK:ENUMS:START -->
<!-- ADIK:ENUMS:END -->

## Functions and Methods
<!-- ADIK:FUNCTIONS:START -->
<!-- ADIK:FUNCTIONS:END -->

## Error Catalogue
<!-- ADIK:ERRORS:START -->
<!-- ADIK:ERRORS:END -->

## Changelog
| Date | Commit SHA | Change Summary |
|------|------------|----------------|
| —    | —          | Registry initialised |
```

### Parsing Contract

Agents and skills parse **only** the content between `ADIK:<SECTION>:START` and `ADIK:<SECTION>:END` markers. Everything outside is human documentation and must not be modified by agents.

---

## Step 5 — Build the Codebase Analyst Agent

Create `agents/codebase-analyst.agent.md`. This is the intelligence layer — it reads the source repo and populates the Registry.

### Required Capabilities

Your Codebase Analyst Agent must implement:

1. **Environment probe** — check for vector DBs, infer `frameworkHints`, record dev-state snapshot.
2. **Project type detection** — classify as api/service/library.
3. **Source language detection** — TypeScript, Python, C#, Go, Java.
4. **Symbol discovery** — extract exported symbols per language.
5. **Registry write protocol** — upsert symbols, preserve markers, append changelog.
6. **Vectorize delegation** — invoke `skills/vectorize.skill.md` when `vectorMode = "active"`.

### Framework Hints Inference Logic

```
IF architecture.md exists:
  Extract framework names from ## Tech Stack, ## Frameworks sections

ELSE scan package manifests:
  package.json → react, nestjs, express, fastify, angular, vue
  pyproject.toml → fastapi, flask, django
  *.csproj → Microsoft.AspNetCore, Blazor

ELSE scan agents/*.md, skills/*.md for "framework:" front-matter

WRITE frameworkHints to adik.env.json
```

### Development State Check Protocol

```
READ previous adik.env.json (if present)
COMPARE current adik.config.json vs previous runConfig:
  sdkLanguages changed? → warn: stale SDK directories
  includePatterns changed? → warn: orphaned registry entries
DETECT sdk/<language>/ dirs not matching sdkLanguages → staleArtifacts
WRITE { runAgents, runSkills, runConfig, runTimestamp, staleArtifacts } to adik.env.json
```

### Execution Protocol

```
1. READ adik.config.json
2. PROBE environment → WRITE adik.env.json
3. PERFORM dev-state check
4. DETECT projectType + sourceLanguage
5. INFER frameworkHints
6. SCAN source files
7. EXTRACT symbols
8. MERGE into Registry.md
9. UPDATE Registry.md metadata
10. IF vectorMode = "active": INVOKE skills/vectorize.skill.md
11. APPEND Registry.md changelog
12. REPORT to ADIK.orchestrator.md
```

---

## Step 6 — Build the Builder Agent

Create `agents/builder.agent.md`. This agent reads the populated Registry and delegates to skills.

### Required Capabilities

1. **Registry validation** — assert `projectType`, `lastAnalysedCommit`, and at least one non-empty section.
2. **frameworkHints propagation** — read from `adik.env.json`, pass to sdk-consumer.skill.
3. **Skill invocation** — invoke `sdk-builder.skill.md` and `sdk-consumer.skill.md` per language.
4. **Build report** — emit `sdk/BUILD_REPORT.md` with timestamps, commit SHA, vectorMode, and any warnings.
5. **agents.md upsert** — append or update the ADIK integration block.

### Execution Protocol

```
1. LOAD Registry.md → assert non-empty
2. READ adik.env.json → frameworkHints, vectorMode
3. FOR EACH language IN sdkLanguages:
     INVOKE sdk-builder.skill { registry, language, projectType, outputDir }
     INVOKE sdk-consumer.skill { registry, language, projectType, outputDir, frameworkHints }
4. WRITE sdk/BUILD_REPORT.md
5. UPSERT agents.md
```

---

## Step 7 — Build the Skills

### 7a — SDK Builder Skill

Create `skills/sdk-builder.skill.md`. This skill generates the actual SDK packages.

**Minimum Implementation:**

```markdown
# SDK Builder Skill

Inputs: registry, language, projectType, outputDir
Outputs: sdk/<language>/ package

For each language:
  1. Read ADIK:CLASSES, ADIK:INTERFACES, ADIK:ENUMS, ADIK:SCHEMAS, ADIK:ENDPOINTS
  2. Apply naming conventions (PascalCase classes, camelCase methods for TS, snake_case for Python)
  3. Map registry types to language types (string→str/string, number→float/number/double)
  4. Generate model files, client file, error files, barrel/init exports
  5. Emit package manifest (package.json / pyproject.toml / .csproj)
  6. Deprecated symbols → @deprecated / warnings.deprecated / [Obsolete]
```

**Type Mapping Table** (required in your skill):

| Registry | TypeScript | Python | C# |
|----------|------------|--------|----|
| string | string | str | string |
| number | number | float | double |
| integer | number | int | int |
| boolean | boolean | bool | bool |
| date | Date | datetime | DateTimeOffset |
| array\<T\> | T[] | list[T] | List\<T\> |
| map\<K,V\> | Record\<K,V\> | dict[K,V] | Dictionary\<K,V\> |
| optional\<T\> | T\|undefined | T\|None | T? |

### 7b — SDK Consumer Skill

Create `skills/sdk-consumer.skill.md`. This skill generates framework-idiomatic consumption boilerplate.

**Minimum Implementation:**

```markdown
# SDK Consumer Skill

Inputs: registry, language, projectType, outputDir, frameworkHints (auto-inferred if absent)

frameworkHints resolution:
  1. Explicit parameter
  2. adik.env.json.frameworkHints (inferred by codebase-analyst)
  3. [] → generic boilerplate

For each endpoint/function in Registry:
  Generate: basic usage example, error handling example, retry wrapper

For each frameworkHint:
  react     → useMyServiceClient hook
  nestjs    → MyServiceModule + MyServiceProvider
  fastapi   → Depends(get_client) dependency
  aspnet    → IServiceCollection.AddMyServiceClient() extension
  angular   → MyServiceClientModule + MyServiceClientService
```

### 7c — Vectorize Skill

Create `skills/vectorize.skill.md`. This skill handles all vector store interactions and is **only invoked when vectorMode = "active"**. Keeping it separate prevents vector-store details from polluting the orchestrator and agents.

**Minimum Implementation:**

```markdown
# Vectorize Skill

Invoked by: agents/codebase-analyst.agent.md (only when vectorMode = "active")
Inputs: Registry.md, source files, adik.env.json
Outputs: vector store upserts, Registry.md metadata update

Execution:
  1. ASSERT adik.env.json.vectorMode = "active"
  2. Embed each Registry symbol (id + kind + name + signature + description)
  3. Upsert embeddings keyed by symbol.id
  4. Chunk source files per adik.config.json.vectors.chunkStrategy
  5. Embed and upsert each chunk keyed by filePath#index
  6. UPDATE Registry.md vectors.storeUri + vectors.lastVectorised
```

---

## Step 8 — Build the MCP Server (Optional)

Create `mcp/adik-mcp-server.md`. This is the remote interface to your ADIK framework, exposing all capabilities as MCP tools.

### Required Tools

| Tool | Description |
|---|---|
| `adik_get_registry` | Return Registry.md contents or a filtered section |
| `adik_build_sdk` | Trigger Builder Agent |
| `adik_analyse_codebase` | Trigger Codebase Analyst Agent |
| `adik_scaffold_boilerplate` | Invoke SDK Consumer Skill |
| `adik_get_symbol` | Look up a symbol by id or name |
| `adik_get_build_report` | Return sdk/BUILD_REPORT.md |
| `adik_vector_search` | Semantic search (only when vectorMode = "active") |

### Required Resources

| URI | Description |
|---|---|
| `adik://registry` | Full Registry.md |
| `adik://registry/{section}` | Single registry section |
| `adik://sdk/build-report` | Latest BUILD_REPORT.md |
| `adik://config` | adik.config.json |
| `adik://env` | adik.env.json |

### Security Model

- Read-only by default; writes require `--allow-writes` flag.
- HTTP mode requires `ADIK_AUTH_TOKEN` for all requests.
- Never expose raw source code — only Registry data and generated artifacts.

---

## Step 9 — Build the README

Your `README.md` should serve two audiences:

### Audience 1: Users of Your Framework

- **What it does** — brief, clear.
- **Quick Start** — 4 steps: copy bundle → (optional) config → run analyst → run builder.
- **Key files table** — MyADIKbuilder.md vs ADIK.md vs ADIK.orchestrator.md vs Registry.md.
- **Vector support summary** — one paragraph, no implementation details.

### Audience 2: Developers Building Their Own Framework

- Link to this document (`ADIKBuilderExample.md`).
- Explain the principle: two orchestrators, one deployable.
- Explain the vectorize-as-subskill pattern.
- Explain the frameworkHints inference pattern.
- Explain the dev-state / crosstailing prevention pattern.

---

## Step 10 — Wire Everything Together

### adik.config.json (default, ship this in your bundle)

```jsonc
{
  "projectType": "auto",
  "sdkLanguages": ["typescript", "python", "csharp"],
  "outputDir": "./sdk",
  "registryPath": "./Registry.md",
  "mcpPort": 3100,
  "syncOnCommit": true,
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

### agents.md Integration Block

After the first successful run, your Builder Agent should upsert this block:

```markdown
## ADIK — SDK Orchestrator

Loaded agents:
- agents/builder.agent.md
- agents/codebase-analyst.agent.md

Loaded skills:
- skills/sdk-builder.skill.md
- skills/sdk-consumer.skill.md
- skills/vectorize.skill.md

Registry: Registry.md
MCP server: mcp/adik-mcp-server.md
Vector store: <vectorStoreUri or "none">
Framework hints: <inferred list or "none">
```

### Verification Checklist

Before calling your framework complete, verify:

- [ ] `MyADIKbuilder.md` is NOT in the deployable bundle list.
- [ ] `ADIK.orchestrator.md` references all agents, skills, and the MCP server in its Related Files table.
- [ ] `Registry.md` has all `ADIK:<SECTION>:START/END` markers.
- [ ] `codebase-analyst.agent.md` infers `frameworkHints` and writes `adik.env.json`.
- [ ] `codebase-analyst.agent.md` delegates vectorization to `vectorize.skill.md`.
- [ ] `sdk-consumer.skill.md` reads `frameworkHints` from `adik.env.json` if not explicitly provided.
- [ ] `vectorize.skill.md` starts with `ASSERT vectorMode = "active"` and exits immediately if not.
- [ ] `ADIK.orchestrator.md` does not contain any embedding or vector-store implementation details.
- [ ] Your framework has a version number in both `MyADIKbuilder.md` and `ADIK.md` / `ADIK.orchestrator.md`.
- [ ] Your `MyADIKbuilder.md` release workflow prompts the user to optionally create a separate GitHub repository within the same organisation for internal distribution.

---

## Core Design Decisions (and Why)

### Why Two Orchestrators?

`ADIKbuilder.md` governs the framework source repository. `ADIK.md` defines the standard. `ADIK.orchestrator.md` governs target codebases. Keeping them separate prevents the framework's own development machinery from leaking into consumer projects. Every file in the deployable bundle should be something a consumer codebase actually needs.

### Why Is Vectorization a Subskill?

Vector-store interactions involve connection management, retry logic, chunking strategies, and embedding APIs. Embedding that logic in the orchestrator or the analyst agent would inflate their context window and couple them to a specific infrastructure stack. As a subskill, `vectorize.skill.md` is loaded only when needed and can be swapped out or extended without touching the orchestrator.

### Why Infer frameworkHints?

Asking developers to manually specify `frameworkHints` creates friction and leads to stale config. The `architecture.md` file (if present) is already the authoritative source of framework choices; package manifests confirm them. Automatic inference means the SDK boilerplate is framework-idiomatic on day one, without any extra configuration.

### Why Track Development State?

Agentic pipelines can be interrupted, reconfigured, or run in parallel. Without a state snapshot, a second run with a different `sdkLanguages` list can produce a mix of artifacts from two different configurations — "crosstailing." The `adik.env.json` dev-state snapshot gives every run a consistent starting point and surfaces inconsistencies before they become bugs.

---

## Related Files in the Reference Implementation

| File | Role |
|---|---|
| `ADIKbuilder.md` | Framework orchestrator for the reference implementation |
| `ADIK.md` | Standard definition of the reference implementation |
| `ADIK.orchestrator.md` | Operational orchestrator of the reference implementation |
| `README.md` | Manifesto + dual guide (use this repo / build your own) |
| `Registry.md` | Symbol registry template |
| `agents/codebase-analyst.agent.md` | Reference implementation of the analysis agent |
| `agents/builder.agent.md` | Reference implementation of the builder agent |
| `skills/sdk-builder.skill.md` | Reference SDK builder skill |
| `skills/sdk-consumer.skill.md` | Reference SDK consumer skill |
| `skills/vectorize.skill.md` | Reference vectorize subskill |
| `mcp/adik-mcp-server.md` | Reference MCP server definition |
