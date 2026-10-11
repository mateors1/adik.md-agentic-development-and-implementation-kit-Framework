> Historical analysis retained for context. Current behavior is specified in the
> [v2 standard](../specification/standard.md) and [migration guide](../getting-started/migration-v2.md).

# ADIK & GitHub Spec Kit — Full Specification Analysis

> **Part of:** [ADIK — Agentic Development and Implementation Kit](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework)
> **See also:** [`ADIK.md`](../../ADIK.md), [`docs/specification/standard.md`](../specification/standard.md),
> [`ADIK.orchestrator.md`](../../ADIK.orchestrator.md), [`ADIKbuilder.md`](../../ADIKbuilder.md)

This document provides a comprehensive, file-level comparison of the ADIK framework against GitHub Spec Kit
([github.com/github/spec-kit](https://github.com/github/spec-kit)) — an open-source, AI-native
**Spec-Driven Development (SDD)** standard backed by GitHub, Anthropic, and Microsoft. The analysis
draws on every ADIK component, not just top-level documentation.

---

## Part 1 — What Is GitHub Spec Kit? A Technical Summary

### Philosophy

Spec Kit inverts traditional software development: **specifications become the executable source of
truth; code is their output.** It defines a structured, AI-mediated workflow that turns a natural-language
product idea into a running application via five ordered phases.

### Core Workflow Phases

| Phase | Slash Command | Output Artifact | Purpose |
|---|---|---|---|
| Constitution | `/speckit.constitution` | `.specify/memory/constitution.md` | Governing principles — coding standards, security, governance |
| Specification | `/speckit.specify` | `.specify/specs/<feature>/spec.md` | Requirements and user stories; *what* to build, not *how* |
| Clarification | `/speckit.clarify` | Appended to `spec.md` | Structured ambiguity resolution before planning |
| Plan | `/speckit.plan` | `.specify/specs/<feature>/plan.md`, `data-model.md`, `research.md`, `contracts/api-spec.json` | Technical architecture, stack choices, API contracts |
| Tasks | `/speckit.tasks` | `.specify/specs/<feature>/tasks.md` | Granular implementation task list |
| Implementation | `/speckit.implement` | Source code | AI-driven code generation from task list |
| Analysis | `/speckit.analyze` | Report | Cross-artifact consistency and gap analysis |
| Checklist | `/speckit.checklist` | Checklist doc | Quality validation against requirements |

### Directory Structure

```
.specify/
├── memory/
│   └── constitution.md            ← Project governing principles (persists across features)
├── scripts/                       ← Shell automation helpers
├── specs/
│   └── 001-create-taskify/        ← One directory per feature/branch
│       ├── spec.md                ← Requirements and user stories
│       ├── plan.md                ← Technical plan
│       ├── data-model.md          ← Data model
│       ├── research.md            ← Stack research
│       ├── tasks.md               ← Granular task list
│       └── contracts/
│           ├── api-spec.json      ← OpenAPI/JSON API contract
│           └── signalr-spec.md    ← Protocol contracts
└── templates/
    ├── spec-template.md
    ├── plan-template.md
    └── tasks-template.md
```

### Extension and Preset System

Spec Kit has a formal, publicly documented extension ecosystem:

- **Extensions** introduce new commands and workflow phases (e.g., Jira sync, code review, V-Model
  test traceability). Published via `specify extension add <name>`.
- **Presets** override existing templates and terminology without adding commands (e.g., compliance
  formats, Agile/Kanban vocabulary, pirate-speak).
- A **community catalog** (`extensions/catalog.community.json`) lists all community extensions.
  Submission is via PR to the `github/spec-kit` repository.
- A **priority stack** governs template resolution: project-level overrides → presets → extensions → core.

### AI Agent Support

Spec Kit supports 25+ AI coding agents: GitHub Copilot, Claude Code, Gemini CLI, Cursor, Codex CLI,
Windsurf, Qwen Code, Roo Code, Amp, Kiro CLI, Jules, and more. Commands are installed as slash-command
template files (`.claude/commands/`, `.github/copilot-instructions`, etc.) or as agent skills.

### The `specify` CLI

A Python-based CLI (`specify init <project> --ai <agent>`) bootstraps a Spec Kit project. It:
- Creates the `.specify/` directory with appropriate templates
- Installs slash-command files for the chosen AI agent
- Optionally initialises a Git repository with branch-per-feature conventions

---

## Part 2 — ADIK Full Component Inventory

Before comparing, here is every ADIK component and what it does:

| File | Layer | Role |
|---|---|---|
| `ADIK.md` | Standard | Defines what ADIK is, terminology (adik/ADIK), lifecycle, reach table, and 10 standard contracts |
| `ADIK.orchestrator.md` | Deployed | Operational brain inside every adik — startup protocol, pipeline execution, headless mode, vector/RAG support |
| `ADIKbuilder.md` | Factory | Source-repo-only orchestrator that produces specialized adik bundles |
| `docs/specification/standard.md` | Spec | RFC-style formal spec with MUST/SHOULD conformance levels (Core, Extended, Full) |
| `Registry.md` | Data | Language-agnostic symbol registry template (YAML entries, section guard markers) |
| `Registry.index.md` | Data | Master index for partitioned registries (domain partition table) |
| `agents/codebase-analyst.agent.md` | Agent | Environment probe, project-type detection, framework inference, source scanning, Registry population |
| `agents/builder.agent.md` | Agent | Registry validation, SDK generation coordination, audit log, self-embedding |
| `skills/sdk-builder/SKILL.md` | Skill | Tier-1 SDK generation: TypeScript, Python, C# — full package with client, models, types, errors |
| `skills/sdk-builder-tier2/SKILL.md` | Skill | Tier-2 SDK generation (opt-in): Go, Java, Kotlin — mirrors tier-1 contract |
| `skills/sdk-consumer/SKILL.md` | Skill | Framework-idiomatic boilerplate — examples, DI wiring, retry wrappers, serialization helpers |
| `skills/registry-validator/SKILL.md` | Skill | Three-level validation gate (Structural, Type, Semantic) before every SDK generation |
| `skills/vectorize/SKILL.md` | Skill | Vector embedding and upsert — isolated from all other pipeline components |
| `scripts/adik-embed.py` | Script | Deterministic self-embedding into context files using `<!-- ADIK:START/END -->` guards |
| `scripts/adik-eject.py` | Script | Clean uninstall — removes all ADIK artifacts without touching source code |
| `scripts/adik-deploy.py` | Script | Factory-side bundle assembly and deployment (source repo only) |
| `mcp/adik-mcp-server.md` | Infra | MCP server exposing 8 tools + 5 resources + 2 prompt templates |
| `docs/specification/architecture.md` | Docs | Mermaid flow diagrams, agent-skill delegation model, data flow |
| `docs/specification/manifesto.md` | Docs | 5 core principles: single source of truth, inference over configuration, context cleanliness, graceful degradation, composability |
| `adik-lint.py` | Tooling | ADIK.md specification linter |
| `ROADMAP.md` | Planning | Versioned feature roadmap (v1.0.0 through v2.0.0) |

---

## Part 3 — The Two-Layer Model: Where Each Framework Operates

The most precise way to understand the relationship is to map both frameworks to the software lifecycle:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  LAYER 0 — INTENT: What to build and why                         SPEC KIT               │
│  Constitution → Specify → Clarify → Plan → Tasks → Implement                            │
│  Artifacts: constitution.md, spec.md, plan.md, contracts/api-spec.json, tasks.md, code  │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  LAYER 1 — CONTRACT: What the built thing exposes               ADIK BEGINS HERE        │
│  Codebase Analyst → Registry.md (symbol registry — endpoints, types, schemas)           │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  LAYER 2 — DISTRIBUTION: How others consume what was built       ADIK                   │
│  Registry → SDK Packages (TS, Python, C#, Go, Java, Kotlin)                             │
│  Registry → Boilerplate (DI wiring, retry wrappers, examples)                           │
│  Registry → AI Context (Copilot, Claude, Cursor self-embedding)                          │
│  Registry → MCP Server (programmatic API for agents)                                    │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Spec Kit's final artifact (Layer 0) is the application code. ADIK's first artifact (Layer 1) is a
structured representation of that code. The two frameworks are not competing for the same layer.

---

## Part 4 — Is ADIK a Complement? YES — Here Is the Precise Handoff

### 4.1 The Handoff Point: `contracts/api-spec.json` → `Registry.md`

When Spec Kit's `/speckit.plan` produces `contracts/api-spec.json`, it emits exactly what ADIK's
Codebase Analyst Agent is designed to read. The Codebase Analyst already has an explicit rule for
this case (from `agents/codebase-analyst.agent.md` §Symbol Discovery Strategy):

```
IF OpenAPI spec (openapi.yaml / swagger.json) exists
  OR route definitions found (Express routes, FastAPI decorators, ASP.NET controllers)
  → projectType = "api"
```

ADIK already parses OpenAPI specs as a first-class input. The only gap is the path convention:
ADIK currently looks for `openapi.yaml` / `swagger.json` at the root, while Spec Kit places the
contract at `.specify/specs/<feature>/contracts/api-spec.json`. A one-line configuration in
`adik.config.json` would bridge this:

```json
{
  "includePatterns": [
    "src/**/*",
    ".specify/specs/*/contracts/api-spec.json"
  ]
}
```

### 4.2 Phase-by-Phase Integration

| Spec Kit Phase | Spec Kit Output | ADIK Integration Point |
|---|---|---|
| **Constitution** | `constitution.md` — coding standards, stack constraints | No direct ADIK integration; constitution may constrain `sdkLanguages` or `tier2Languages` choices |
| **Specify** | `spec.md` — requirements, user stories, acceptance criteria | No direct integration; spec.md is human-readable requirements, not a symbol catalog |
| **Clarify** | Appended to `spec.md` | No direct integration |
| **Plan** | `plan.md`, `data-model.md`, **`contracts/api-spec.json`** | **Primary handoff**: `api-spec.json` is a valid input to the Codebase Analyst Agent (`projectType: "api"` path) |
| **Tasks** | `tasks.md` | No direct integration |
| **Implement** | Source code | **Primary ADIK trigger**: after implementation, ADIK's Codebase Analyst scans the source and produces `Registry.md` |
| **Analyze** | Consistency report | No direct integration |

### 4.3 What ADIK Adds After Spec Kit Finishes

Once Spec Kit's `/speckit.implement` produces working code, ADIK's pipeline takes over:

```
Spec Kit output (source code + api-spec.json)
        │
        ▼
[Step 0] Codebase Analyst → probes env, detects NestJS/FastAPI/ASP.NET via framework hints
         │                    inference from package.json / pyproject.toml / *.csproj
         │
         ▼
[Step 1] Codebase Analyst → parses source code and/or api-spec.json,
         │                    populates Registry.md with every endpoint, class, schema, enum
         │
         ▼
[Step 2] Registry Validator → three-level gate (Structural S-001–S-006, Type T-001–T-005,
         │                     Semantic P-001–P-004) before any code generation
         │
         ▼
[Step 3] Builder Agent → generates sdk/typescript/, sdk/python/, sdk/csharp/
         │                (+ Go/Java/Kotlin if tier2Languages configured)
         │
         ├─ SDK Builder Skill: package.json, tsconfig.json, client.ts, models/*.ts,
         │                      types/*.ts, errors/*.ts, pyproject.toml, *.csproj, etc.
         │
         └─ SDK Consumer Skill: examples/basic-usage.ts, boilerplate/retry-wrapper.ts,
                                  DI wiring (NestJS MyServiceModule, FastAPI Depends, IServiceCollection)
         │
         ▼
[Step 4] Self-Embedding → injects ADIK context into .github/copilot-instructions.md,
                           CLAUDE.md, agents.md (same files Spec Kit's AI agents already read)
         │
         ▼
[Step 5] MCP Server → exposes adik_build_sdk, adik_analyse_codebase, adik_get_registry,
                        adik_scaffold_boilerplate, adik_vector_search to any connected agent
```

The same AI assistant that drove Spec Kit's `/speckit.implement` step (Claude Code, GitHub Copilot,
Gemini CLI) now has ADIK's Registry and SDK context available through the same embedded context files.
No configuration change is needed on the AI side.

### 4.4 The Self-Embedding Convergence

ADIK's `scripts/adik-embed.py` writes to `.github/copilot-instructions.md`, `CLAUDE.md`, and
`agents.md`. Spec Kit's `specify init` also writes to `.github/copilot-instructions.md` (for Copilot)
and `CLAUDE.md` (via `scripts/update-claude-md.sh`). Both frameworks write to the same context files
using different sections. They can coexist as long as ADIK's guard markers (`<!-- ADIK:START/END -->`)
do not conflict with Spec Kit's content, which they do not — Spec Kit does not use ADIK-format guard
blocks. Both tools write their sections cleanly, and ADIK's embed script is idempotent by design.

---

## Part 5 — Full Compliance Assessment Against Spec Kit

Spec Kit is a methodology and tooling standard, not a machine-readable protocol schema. The assessment
below maps every ADIK component against the closest Spec Kit concept.

### 5.1 Conceptual Alignment Table

| Spec Kit Concept | ADIK Equivalent | Alignment Level | Notes |
|---|---|---|---|
| **Constitution** — project governing principles | `ADIK.md` Standard Contracts (§Standard Contracts) + `adik.config.json` defaults | ⚠️ Partial | ADIK's "constitution" is structural (what agents must do); Spec Kit's is semantic (what the *product* should be). They serve different audiences. |
| **Spec** — requirements and user stories | No direct equivalent | — | ADIK operates post-specification. It does not author requirements. |
| **Plan** → `api-spec.json` — API contract | `Registry.md` — language-agnostic symbol registry | ✅ Complementary | ADIK's Registry is a richer, more detailed form of an API contract — typed, versioned, partitionable. An OpenAPI → Registry bridge would unify them. |
| **Tasks** — granular task list | `agents/builder.agent.md` Execution Protocol (10-step numbered list) | ✅ Aligned conceptually | Both frameworks structure work as ordered, gated, numbered steps. |
| **Implement** — AI-driven code generation | `skills/sdk-builder/SKILL.md` + `skills/sdk-builder-tier2/SKILL.md` + `skills/sdk-consumer/SKILL.md` | ✅ Complementary — different output | Spec Kit generates application code; ADIK generates SDK packages and boilerplate from the application. |
| **Analyze** — cross-artifact consistency | `skills/registry-validator/SKILL.md` (3-level validation: S, T, P rules) | ✅ Aligned | Both have a cross-artifact consistency gate. ADIK's is more formal (S-001–P-004 rules). |
| **Constitution** — living document, version-controlled | `Registry.md` Changelog table + `adik.audit.log` NDJSON trail | ✅ Aligned | ADIK's audit trail is more machine-readable; Spec Kit's constitution is more human-narrative. |
| **AI agent support** — 25+ agents | Self-embedding into `.github/copilot-instructions.md`, `CLAUDE.md`, `agents.md` | ✅ Aligned | ADIK achieves multi-agent awareness via self-embedding into the same context files Spec Kit uses. |
| **Extension system** — `specify extension add` | Agent/skill architecture in `agents/` + `skills/` | ⚠️ Not interoperable | ADIK's extension model is internal (add an `.agent.md` / `.skill.md` file). It is not published to Spec Kit's community catalog. Becoming a Spec Kit extension would make ADIK discoverable there. |
| **Preset system** — override templates | `adik.config.json` `partitionStrategy`, `sdkLanguages`, `startupMode` | ⚠️ Partial | ADIK has configuration-level customization but no Spec Kit-compatible preset format. |
| **Branch-per-feature** (`001-feature-name`) | Project-wide Registry; no per-feature partitioning | ⚠️ Gap | ADIK's `Registry.<domain>.md` partitioning is namespace-based, not branch/feature-based. Aligning partition naming to Spec Kit's `001-feature-name` convention would close this gap. |
| **`/speckit.*` slash commands** | MCP tools (`adik_build_sdk`, `adik_analyse_codebase`, etc.) | ⚠️ Different mechanism | ADIK uses MCP rather than slash commands. Publishing an ADIK extension to Spec Kit would add `/speckit.adik.*` slash commands alongside the MCP interface. |

### 5.2 Gaps to Close for Structural Alignment

Three concrete changes would make ADIK structurally aligned with Spec Kit's workflow:

**Gap 1 — OpenAPI contract import path**

`agents/codebase-analyst.agent.md` (§Symbol Discovery Strategy → OpenAPI / Swagger) already handles
OpenAPI files. The gap is that it looks for them at the repo root, not at Spec Kit's path convention.
Fix: add `.specify/specs/*/contracts/api-spec.json` to the scan pattern, or document it in
`docs/getting-started/configuration.md` as an `includePatterns` entry.

**Gap 2 — Feature-branch registry partitions**

`adik.config.json` supports `partitionStrategy: "manual"` with explicit `partitionMappings`. This can
be configured to match Spec Kit's feature naming (`001-create-taskify` → Registry partition
`Registry.create-taskify.md`). This is configuration, not a code change. Document it as a
"Spec Kit integration mode" in `docs/ecosystem/`.

**Gap 3 — Spec traceability field in Registry symbols**

The `Registry.md` symbol entry schema (`docs/specification/standard.md` §5.4) includes a `tags`
field. A `specRef` convention (`tags: ["spec:001-create-taskify"]`) would provide a lightweight
traceability link back to Spec Kit's feature directory without requiring a schema change.

### 5.3 ADIK Standard vs. Spec Kit Standard — Direct Spec Comparison

| Dimension | ADIK `docs/specification/standard.md` | Spec Kit `spec-driven.md` + `github/spec-kit` README |
|---|---|---|
| **Format** | RFC-style with MUST/SHOULD/MAY conformance levels | Methodology document + CLI tool |
| **Conformance levels** | 3 levels: Core, Extended, Full (§4) | No explicit levels; tool-centric |
| **Type system** | Formal type mapping table §10.1 / §10.2 for 6 languages | No type system; spec is language-agnostic prose |
| **Symbol schema** | 12-field YAML schema with required/recommended fields (§5.4) | No symbol schema; artifacts are free-form Markdown |
| **Validation gate** | Mandatory 3-level gate before generation (§7.2 + registry-validator.skill.md) | No formal validation gate; `/speckit.analyze` is optional |
| **Versioning** | Semantic versioning with bump rules (§12): patch/minor/major | Semantic versioning of the `specify-cli` tool only |
| **Audit trail** | Append-only NDJSON `adik.audit.log` per build | No built-in audit trail |
| **Bundle specification** | Explicit required/optional/excluded file lists (§9) | No formal bundle spec |
| **Guard markers** | Formally specified: `<!-- ADIK:<SECTION>:START/END -->` (§8) | Not formally specified |
| **Configuration schema** | Full `adik.config.json` schema with all fields and defaults (§11) | `.specify/templates/` directory convention |
| **Extension contract** | Agent protocol (§6) and Skill protocol (§7) with required frontmatter | `extension.yml` manifest + template directory structure |
| **Multi-language output** | 6 languages with canonical type mappings | No code generation — produces spec artifacts only |
| **Machine-readability** | Registry is YAML-within-Markdown, parseable by agents | Spec artifacts are human-readable Markdown |

---

## Part 6 — Is ADIK a Competitor? No — With Strategic Nuance

### 6.1 Why Not a Competitor

ADIK and Spec Kit address categorically different problems:

- Spec Kit answers: *"How do we go from an idea to working application code?"*
- ADIK answers: *"How do consumers of that application call it from 6 programming languages
  without maintaining SDKs by hand?"*

There is zero feature overlap between Spec Kit's core workflow (constitution → spec → plan → tasks
→ implement) and ADIK's core pipeline (analyse → registry → validate → generate → embed).

### 6.2 Where the Ecosystem Risk Is Real

The Spec Kit community extension catalog already contains extensions for:
- `spec-kit-docguard` — canonical-driven development enforcement with documentation validation
- `spec-kit-v-model` — V-Model paired test spec generation
- `spec-kit-review` — post-implementation code review with specialized agents
- `understanding` — requirements quality analysis against IEEE/ISO standards

These are adjacent to ADIK's concerns. None yet covers **SDK generation** or **multi-language API
client generation**. That slot is open. If a community contributor publishes a basic "generate an SDK
from this spec" extension before ADIK does, it could occupy the mindshare position that ADIK should own.

### 6.3 The Philosophical Convergence

Both frameworks share a "spec-as-source-of-truth" philosophy, but apply it at different artifact levels:

| Framework | Source of Truth | Truth About What | Output |
|---|---|---|---|
| Spec Kit | `spec.md` — natural language requirements | *Product intent* | Application code |
| ADIK | `Registry.md` — typed symbol catalog | *API contract* | SDK packages |

These are not competing philosophies — they are adjacent layers of the same principle. A Spec Kit
spec becomes ADIK's source code, which becomes ADIK's Registry, which becomes ADIK's SDKs. The chain
is: **spec → code → registry → SDK**.

---

## Part 7 — Offering ADIK as a Spec Kit Extension

### 7.1 Why This Is Strategically Important

Publishing ADIK as a Spec Kit extension achieves three things simultaneously:
1. Places ADIK in the active extension catalog where Spec Kit users discover tools
2. Creates a formal integration contract between the two frameworks
3. Establishes ADIK as *the* SDK generation layer in the SDD ecosystem before the slot is filled

### 7.2 What a Spec Kit Extension Requires

Based on the Spec Kit extension development guide and `extension.yml` manifest spec:

```
spec-kit-adik/
├── extension.yml                    ← Required: manifest (id, version, name, description, author, commands, templates)
├── README.md                        ← Required: installation, usage, prerequisites
├── LICENSE                          ← Required: Apache 2.0
├── templates/
│   ├── speckit.adik.registry.md     ← Template for /speckit.adik.registry command
│   ├── speckit.adik.sdk.md          ← Template for /speckit.adik.sdk command
│   ├── speckit.adik.boilerplate.md  ← Template for /speckit.adik.boilerplate command
│   └── speckit.adik.status.md       ← Template for /speckit.adik.status command
└── commands/
    ├── claude/                      ← .claude/commands/ files for Claude Code
    ├── copilot/                     ← .github/ files for GitHub Copilot
    ├── gemini/                      ← .gemini/ files for Gemini CLI
    └── generic/                     ← For any other supported agent
```

### 7.3 Proposed Extension Commands

| Command | Invocation | What It Does | ADIK Component Triggered |
|---|---|---|---|
| `/speckit.adik.registry` | After `/speckit.implement` | Scans source code + reads `.specify/specs/*/contracts/api-spec.json`; populates `Registry.md` | `agents/codebase-analyst.agent.md` |
| `/speckit.adik.sdk` | After `/speckit.adik.registry` | Validates Registry and generates SDK packages for configured languages | `agents/builder.agent.md` + `skills/sdk-builder/SKILL.md` |
| `/speckit.adik.boilerplate` | After `/speckit.adik.sdk` | Generates framework-idiomatic integration boilerplate (DI wiring, retry wrappers, examples) | `skills/sdk-consumer/SKILL.md` |
| `/speckit.adik.status` | Any time | Reports Registry freshness, SDK sync status, which symbols need regeneration | `adik_get_build_report` MCP tool |

### 7.4 Integration in the Full SDD + ADIK Workflow

```
[Spec Kit core pipeline]                   [ADIK extension — post-implement phase]
─────────────────────                      ────────────────────────────────────────
/speckit.constitution
/speckit.specify
/speckit.clarify
/speckit.plan          → contracts/api-spec.json
/speckit.tasks
/speckit.implement     → source code
                               │
                               ▼
                       /speckit.adik.registry   → Registry.md populated from source + api-spec.json
                               │
                               ▼
                       /speckit.adik.sdk         → sdk/typescript/, sdk/python/, sdk/csharp/ written
                               │
                               ▼
                       /speckit.adik.boilerplate → DI wiring, retry wrappers, usage examples
                               │
                               ▼
                       /speckit.adik.status      → sync report; re-run on next feature iteration
```

### 7.5 What the Extension `extension.yml` Manifest Looks Like

```yaml
id: adik-sdk-generator
version: 1.0.0
name: ADIK SDK Generator
description: >
  Generates multi-language, self-maintaining SDK packages from your Spec Kit
  implementation using the ADIK (Agentic Development and Implementation Kit) framework.
  After /speckit.implement, run /speckit.adik.registry → /speckit.adik.sdk →
  /speckit.adik.boilerplate to produce publish-ready TypeScript, Python, and C# SDKs.
author: mateors1
license: Apache-2.0
homepage: https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework
category: code
effect: Read+Write
prerequisites:
  - name: ADIK deployed in repository
    check: ADIK.orchestrator.md exists
    required: true
  - name: Python 3.11+
    check: python3 --version
    required: true
commands:
  - speckit.adik.registry
  - speckit.adik.sdk
  - speckit.adik.boilerplate
  - speckit.adik.status
```

### 7.6 Three-Milestone Delivery Plan

**Milestone 1 — Minimum Viable Extension**

| Deliverable | Description |
|---|---|
| `extension.yml` | Manifest with ID, version, author, commands list |
| `/speckit.adik.registry` template | Invoke Codebase Analyst; point it at source + `.specify/specs/*/contracts/api-spec.json` |
| `/speckit.adik.sdk` template | Invoke Builder Agent for TypeScript + Python; report output |
| `README.md` | Prerequisites (ADIK deployed), installation, quick start |
| Integration test | End-to-end test using Spec Kit's Taskify demo project |

**Milestone 2 — Full Integration**

| Deliverable | Description |
|---|---|
| `includePatterns` Spec Kit path support | Document and test `.specify/specs/*/contracts/api-spec.json` as an `includePatterns` entry |
| Per-feature Registry partitions | Configuration guide for `partitionStrategy: "manual"` aligned to Spec Kit's `001-feature-name` branch names |
| `/speckit.adik.boilerplate` template | NestJS / FastAPI / ASP.NET DI wiring + retry wrappers |
| `/speckit.adik.status` template | Diff Registry against last build; show stale symbols |
| `specRef` tagging convention | Document use of `tags: ["spec:001-feature"]` in Registry symbols for traceability |

**Milestone 3 — Community Catalog Submission**

| Deliverable | Description |
|---|---|
| Published GitHub release | `spec-kit-adik` v1.0.0 with zip artifact |
| PR to `github/spec-kit` | Add entry to `extensions/catalog.community.json`; update `extensions/README.md` |
| Community walkthrough | A Spec Kit-style walkthrough repo (like `mnriem/spec-kit-dotnet-cli-demo`) demonstrating the full Spec Kit + ADIK end-to-end flow |
| Community walkthrough PR | Submit walkthrough to Spec Kit's community walkthroughs section in the main README |

---

## Part 8 — What ADIK Uniquely Offers That Spec Kit Does Not

### 8.1 Capability Comparison Table

| Capability | Spec Kit | ADIK | ADIK Component |
|---|---|---|---|
| **Multi-language SDK code generation** | ❌ Not in scope | ✅ TS, Python, C#, Go, Java, Kotlin | `skills/sdk-builder/SKILL.md` + `skills/sdk-builder-tier2/SKILL.md` |
| **Language-agnostic symbol registry** | ❌ `api-spec.json` is per-feature, JSON only | ✅ `Registry.md` — YAML-in-Markdown, typed, partitionable, versioned | `Registry.md`, `Registry.index.md` |
| **Self-maintaining CI pipeline** | ❌ Manual re-run required | ✅ `syncOnCommit: true` → every commit triggers re-analysis + regeneration | `ADIK.orchestrator.md` headless mode |
| **Framework-idiomatic boilerplate** | ❌ Left to the developer | ✅ NestJS DI module, FastAPI `Depends`, ASP.NET `IServiceCollection`, React hook, Angular module | `skills/sdk-consumer/SKILL.md` |
| **Deterministic self-embedding** | Spec Kit writes commands at install time | ✅ `adik-embed.py` writes/updates context files with idempotent guard markers | `scripts/adik-embed.py` |
| **Registry validation gate** | `/speckit.analyze` is optional consistency check | ✅ Mandatory 3-level gate (14 validation rules S-001–P-004); `FAIL` aborts generation | `skills/registry-validator/SKILL.md` |
| **Append-only audit trail** | ❌ None | ✅ `adik.audit.log` NDJSON — one structured record per build (compliance, debugging, drift detection) | `agents/builder.agent.md` §Audit Log |
| **MCP server** | ❌ No MCP interface | ✅ 8 tools, 5 resources, 2 prompt templates via stdio or HTTP+SSE | `mcp/adik-mcp-server.md` |
| **Vector/RAG semantic search** | ❌ Not in scope | ✅ `adik_vector_search` tool; 3 chunking strategies (symbol / file / sliding-window) | `skills/vectorize/SKILL.md` |
| **Formal conformance levels** | ❌ No conformance levels | ✅ Core (L1), Extended (L2), Full (L3) with MUST/SHOULD/MAY compliance checklist | `docs/specification/standard.md` §4 |
| **Post-generation type-checking** | ❌ None | ✅ tsc, mypy, dotnet build after generation (advisory or strict via `ADIK_STRICT_TYPECHECK`) | `agents/builder.agent.md` §Post-generation |
| **Clean eject** | Manual file deletion | ✅ `adik-eject.py` — removes all ADIK artifacts, respects guard markers, preserves source | `scripts/adik-eject.py` |
| **Incremental build** | ❌ Full regeneration on every run | ✅ Diff-and-update mode; only re-generates symbols that changed since last analysed commit | `agents/builder.agent.md` §Incremental Build |
| **Application code generation** | ✅ Full application from spec | ❌ Not in scope | — |
| **Requirements management** | ✅ spec.md with user stories, acceptance criteria | ❌ Not in scope | — |
| **Multi-agent support (25+)** | ✅ Native slash-command install for 25+ agents | ✅ Via self-embedding into shared context files | Both |

### 8.2 The Unique Architectural Advantage: Incremental, Self-Maintaining SDKs

The feature Spec Kit cannot replicate is ADIK's **self-maintaining** character: the adik bundle
carries its own agents, so every commit to the source code triggers automatic re-analysis, re-validation,
and re-generation. This is not a UI feature — it is the fundamental architecture of an adik
(an **adik** carries its own maintenance pipeline; a Spec Kit project does not).

This means:

- Spec Kit + ADIK together provide the full lifecycle: *intent → spec → implementation → SDK →
  maintained SDK*
- Without ADIK, Spec Kit's output (the implemented application) requires ongoing manual SDK maintenance
- Without Spec Kit, ADIK works on any existing codebase — but lacks the structured specification
  and planning phase

---

## Part 9 — Recommended Next Steps

### Immediate (this sprint)

1. **Open a GitHub Discussion in `github/spec-kit`** to signal intent before building. This prevents
   duplication, invites early collaboration, and is good community etiquette given how active the
   Spec Kit maintainers are.

2. **Test the existing integration** with zero code changes: deploy ADIK into a Spec Kit project
   (e.g., the Taskify demo), add `.specify/specs/*/contracts/api-spec.json` to `includePatterns` in
   `adik.config.json`, and run the ADIK pipeline. Document whether the Registry populates correctly
   from the api-spec.json. This validates the integration claim and produces concrete evidence.

### Short-Term (v1.1.0 scope — already on ADIK's roadmap)

3. **OpenAPI 3.1 bidirectional sync** is already on `ROADMAP.md` (v1.2.0). Consider pulling it
   forward to v1.1.0 given the strategic importance of Spec Kit alignment. This one feature makes
   ADIK compatible with any OpenAPI-aware toolchain, not just Spec Kit.

4. **Document a "Spec Kit integration mode"** in `docs/ecosystem/` (this file) with a concrete
   `adik.config.json` snippet showing how to point ADIK at Spec Kit's contract artifacts.

### Medium-Term (extension MVP)

5. **Build `spec-kit-adik` extension** following the Spec Kit Extension Development Guide. The MVP
   needs only two working commands (`/speckit.adik.registry` and `/speckit.adik.sdk`) and a `README.md`.

6. **Adopt Spec Kit for ADIK's own development.** Use `/speckit.*` commands to drive ADIK's own
   feature development. This produces a `specs/` directory in the ADIK repository, making every
   framework change traceable to a formal specification. ADIK would then use itself (deploy an adik)
   to generate its own MCP server SDK and agent SDKs. The two frameworks feeding each other is a
   powerful and honest demonstration of value.

### Strategic Investigations

7. **Monitor the extension catalog for SDK generation entries.** The catalog is growing rapidly
   (~20 extensions in the first months). SDK generation is currently absent. The window to publish
   first is open but not indefinitely.

8. **Consider a `speckit.adik` preset** that reshapes Spec Kit's plan and task templates to embed
   ADIK-compatible type annotations directly in `spec.md` — making the Codebase Analyst Agent's
   job easier by pre-structuring what will become Registry entries.

9. **Explore formal SDD + ADIK methodology documentation** — a joint white paper or blog post
   (GitHub Blog, LogRocket, Microsoft Dev Blog) explaining how SDD + ADIK form a complete spec-to-SDK
   pipeline. All three surfaces already cover Spec Kit extensively; an ADIK integration story would
   be novel content with a receptive audience.

---

## Part 10 — Further Reading

| Resource | Link |
|---|---|
| GitHub Spec Kit repository | [github.com/github/spec-kit](https://github.com/github/spec-kit) |
| Spec Kit documentation | [github.github.io/spec-kit](https://github.github.io/spec-kit/) |
| Spec-Driven Development methodology | [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) |
| Spec Kit extension development guide | [extensions/EXTENSION-DEVELOPMENT-GUIDE.md](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-DEVELOPMENT-GUIDE.md) |
| Spec Kit community extension catalog | [extensions/catalog.community.json](https://github.com/github/spec-kit/blob/main/extensions/catalog.community.json) |
| ADIK Standard Specification | [docs/specification/standard.md](../specification/standard.md) |
| ADIK Architecture | [docs/specification/architecture.md](../specification/architecture.md) |
| ADIK Manifesto | [docs/specification/manifesto.md](../specification/manifesto.md) |
| ADIK Roadmap | [ROADMAP.md](../../ROADMAP.md) |
| ADIK Configuration Reference | [docs/getting-started/configuration.md](../getting-started/configuration.md) |
| Builder Agent spec | [agents/builder.agent.md](../../agents/builder.agent.md) |
| Codebase Analyst spec | [agents/codebase-analyst.agent.md](../../agents/codebase-analyst.agent.md) |
| Registry Validator spec | [skills/registry-validator/SKILL.md](../../skills/registry-validator/SKILL.md) |
| MCP Server spec | [mcp/adik-mcp-server.md](../../mcp/adik-mcp-server.md) |
