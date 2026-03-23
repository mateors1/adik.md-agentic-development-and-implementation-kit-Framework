# ADIK & GitHub Spec Kit — Ecosystem Analysis

> **Part of:** [ADIK — Agentic Development and Implementation Kit](../../README.md)
> **See also:** [`ADIK.md`](../../ADIK.md) (standard definition), [`docs/specification/manifesto.md`](../specification/manifesto.md) (ADIK philosophy), [`docs/community/launch-posts.md`](../community/launch-posts.md)

---

## Summary: What is GitHub Spec Kit?

**GitHub Spec Kit** ([github.com/github/spec-kit](https://github.com/github/spec-kit)) is an open-source
toolkit for **Spec-Driven Development (SDD)** — a methodology that inverts the traditional relationship
between specifications and code. Where traditional development treats specs as throwaway scaffolding, SDD
makes specifications the primary, executable artifact: code becomes the output of a living, versioned spec,
not the other way around.

Spec Kit was developed in collaboration with engineers from GitHub, Microsoft, and Anthropic, and is
designed to work with virtually every major AI coding agent — Claude Code, GitHub Copilot, Gemini CLI,
Cursor, Codex CLI, Windsurf, and 20+ others.

### Core Concepts

| Concept | Description |
|---|---|
| **Constitution** | Governing principles for a project — coding standards, security guidelines, governance rules. Created via `/speckit.constitution`. |
| **Specification** | Formal requirements and user stories focused on *what* to build, not *how*. Created via `/speckit.specify`. |
| **Clarification** | Structured ambiguity resolution before technical planning. `/speckit.clarify`. |
| **Plan** | Technical architecture and implementation breakdown for a chosen stack. `/speckit.plan`. |
| **Tasks** | Granular, executable task list generated from the plan. `/speckit.tasks`. |
| **Implementation** | AI-driven code generation from the task list. `/speckit.implement`. |
| **Analysis** | Cross-artifact consistency and coverage checks. `/speckit.analyze`. |

### Directory Structure Produced by Spec Kit

```
.specify/
├── memory/
│   └── constitution.md          ← Project governing principles
├── scripts/                     ← Automation helpers
├── specs/
│   └── 001-create-taskify/
│       ├── spec.md              ← Requirements & user stories
│       ├── plan.md              ← Technical implementation plan
│       ├── data-model.md        ← Data model
│       ├── research.md          ← Stack research notes
│       ├── tasks.md             ← Granular task list
│       └── contracts/
│           ├── api-spec.json    ← API contract (OpenAPI/JSON)
│           └── signalr-spec.md  ← Protocol contracts
└── templates/                   ← Customizable spec/plan/task templates
```

### Extension and Preset System

Spec Kit ships with a formal extension and preset system:

- **Extensions** add new commands and workflows (`specify extension add <name>`). They expand *what Spec Kit can do* — Jira integration, post-implementation code review, V-Model test traceability, etc.
- **Presets** override templates and terminology without adding commands. They customize *how Spec Kit works* — compliance formats, domain-specific vocabulary, organizational standards.
- A **community catalog** (`extensions/catalog.community.json`) accepts community-submitted extensions via PR to the main spec-kit repository.

### Philosophy in One Sentence

> *Specifications are the source of truth. Code is their expression. AI is the transformation engine.*

---

## The Two-Layer Model: Why ADIK and Spec Kit Complement Each Other

Before comparing the frameworks, it helps to map them to the software development lifecycle:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FULL DEVELOPMENT PIPELINE                    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1 — What to Build (Spec Kit)                             │
│  Constitution → Specify → Clarify → Plan → Tasks → Implement   │
│  Output: spec.md, plan.md, tasks.md, contracts/api-spec.json   │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2 — How Others Consume What Was Built (ADIK)             │
│  Analyse → Registry → SDK Generation → Boilerplate → Embed     │
│  Output: TypeScript/Python/C#/Go/Java/Kotlin SDK packages      │
└─────────────────────────────────────────────────────────────────┘
```

**Spec Kit operates at the application layer**: it answers "what does this software do and why?" It
produces the specification, plan, and implementation of a feature or application.

**ADIK operates at the SDK/API contract layer**: it answers "how do other developers consume what was
built?" It produces publish-ready, self-maintaining SDK packages, framework-idiomatic boilerplate, and
AI-context embeddings for the generated API.

These layers are adjacent and complementary, not competing. A team could use Spec Kit to specify, plan,
and implement a payments API — and then deploy ADIK to generate the TypeScript, Python, and C# SDKs that
external developers use to call it. Both tools serve the same codebase, at different phases of its
lifecycle.

---

## Is ADIK a Complement? YES

ADIK and Spec Kit are **natural complements** that together cover the full lifecycle from specification to
self-maintaining multi-language SDK.

### How They Fit Together

#### Phase 1 — Spec Kit's Output Feeds ADIK's Input

Spec Kit's `/speckit.plan` produces API contract artifacts like `contracts/api-spec.json` (OpenAPI/JSON).
ADIK's Codebase Analyst agent reads the codebase to build `Registry.md`. These are different representations
of the same thing: the API contract. A bridge between them is natural and achievable:

```
Spec Kit produces:  contracts/api-spec.json  ──┐
                                                ├──▶  ADIK Registry.md  ──▶  SDKs
ADIK reads:         source code, endpoints    ──┘
```

#### Phase 2 — ADIK Generates What Spec Kit's `/speckit.implement` Would Hand-Code

After Spec Kit builds the application, ADIK generates:
- Publish-ready SDK packages in TypeScript, Python, C#, Go, Java, and Kotlin
- Framework-idiomatic integration boilerplate (NestJS DI wiring, FastAPI dependency injection, ASP.NET middleware)
- Retry wrappers, serialization helpers, and authentication adapters

This is work that Spec Kit's implementation phase would otherwise leave to the developer manually.

#### Phase 3 — ADIK's AI Self-Embedding Enriches Spec Kit Workflows

ADIK embeds SDK context into `.github/copilot-instructions.md`, `CLAUDE.md`, and `agents.md`. Any
AI agent (including the same Claude Code or Copilot that Spec Kit uses) automatically understands the
API surface, generated SDK structure, and integration patterns — with zero extra configuration.

#### Phase 4 — ADIK's Self-Maintenance Keeps SDKs in Sync Across Spec Iterations

When Spec Kit drives a new feature iteration and the implementation changes, ADIK's CI pipeline
re-analyses, re-validates, and re-generates all SDKs automatically. The spec-to-SDK chain becomes
continuous.

---

## Are We Compliant with Spec Kit's Standard?

Spec Kit is a **methodology and tooling standard**, not a strict protocol with a machine-readable
compliance schema. It does not publish a JSON schema or contract file that other tools must satisfy.
Compliance is conceptual and behavioural.

### Current Alignment Assessment

| Spec Kit Principle | ADIK Alignment | Status |
|---|---|---|
| Specifications as the source of truth | ADIK has its own source of truth (`Registry.md`) derived from code, not from specs | ✅ Complementary — different layers |
| Version-controlled spec artifacts | `Registry.md` is version-controlled; ADIK appends to `adik.audit.log` for traceability | ✅ Aligned |
| AI-native workflows | ADIK is built entirely for AI agents; all artifacts are optimized for LLM context windows | ✅ Aligned |
| Extensibility | ADIK's agent/skill architecture is extension-first by design | ✅ Aligned |
| Multi-agent support | ADIK supports Copilot, Claude, Cursor, and any AI agent via self-embedding | ✅ Aligned |
| Contract artifacts as planning output | ADIK currently reads source code; does not yet consume `api-spec.json` directly | ⚠️ Gap — see below |
| Branch-per-feature workflow | ADIK operates project-wide; does not track Spec Kit feature branches | ⚠️ Gap — see below |

### Gaps to Close for Full Alignment

1. **API contract import**: ADIK's Codebase Analyst should optionally ingest `contracts/api-spec.json`
   (OpenAPI format) produced by Spec Kit's `/speckit.plan` phase as a Registry bootstrap input. This
   would make the Spec Kit → ADIK handoff seamless.

2. **Feature-branch awareness**: ADIK currently generates a project-wide registry. Adding support for
   per-feature registry partitions (aligned with Spec Kit's `001-feature-name` branch structure) would
   enable incremental SDK generation that mirrors Spec Kit's incremental development model.

3. **Spec reference in Registry**: ADIK's `Registry.md` could optionally record a `specRef` field
   per endpoint or symbol, linking back to the `spec.md` that originally described that requirement.
   This would provide traceability across both layers.

---

## Is ADIK a Competitor? No — With Important Nuance

ADIK and Spec Kit **do not compete** in their primary purposes:

- Spec Kit answers: *"What should this software do, and how should we build it?"*
- ADIK answers: *"How do other developers consume this software after it is built?"*

Neither framework provides the other's core capability. Spec Kit has no SDK generation. ADIK has no
specification or planning workflow.

### The Surface Area Overlap

There is one area of conceptual overlap: both frameworks promote a **spec-as-source-of-truth** philosophy.

- Spec Kit's spec is a human-readable requirements document (`spec.md`)
- ADIK's registry is a machine-readable symbol catalog (`Registry.md`)

These serve different audiences at different stages of the lifecycle. They are not the same artifact, and
neither replaces the other.

### The Ecosystem Risk

If Spec Kit's extension ecosystem grows to include SDK generation extensions, there could eventually be
direct overlap. The defensive answer is clear: **ADIK should become a first-class Spec Kit extension**
before that gap is filled by someone else (see below). An ADIK presence in the Spec Kit extension catalog
secures ADIK's position as *the* SDK generation layer in the SDD workflow.

---

## Offering ADIK as a Spec Kit Extension

Spec Kit's extension system is well-defined and publicly documented. Publishing ADIK as a Spec Kit
extension is entirely feasible and strategically important.

### What a Spec Kit Extension Requires

```
spec-kit-adik/
├── extension.yml              ← Extension manifest (required)
├── README.md                  ← Installation and usage guide (required)
├── LICENSE                    ← Apache 2.0 (required)
├── templates/
│   ├── speckit.adik.registry.md    ← Slash command: build Registry from spec artifacts
│   ├── speckit.adik.sdk.md         ← Slash command: generate SDKs from Registry
│   └── speckit.adik.status.md      ← Slash command: report SDK sync status
└── commands/
    ├── claude/                ← Claude Code command files
    ├── copilot/               ← Copilot command files
    └── generic/               ← Generic agent command files
```

### Proposed Commands

| Command | Description |
|---|---|
| `/speckit.adik.registry` | Analyse the current feature branch's contracts and source code, bootstrap or update `Registry.md` |
| `/speckit.adik.sdk` | Generate SDK packages from the current Registry; output to `sdk/` |
| `/speckit.adik.boilerplate` | Generate framework-idiomatic integration boilerplate for the generated SDK |
| `/speckit.adik.status` | Report SDK sync status — which symbols are out of date, which languages are generated |

### Integration Point in the SDD Workflow

```
Constitution → Specify → Clarify → Plan → Tasks → Implement
                                                        │
                                                        ▼
                                          /speckit.adik.registry  ← build Registry from contracts
                                                        │
                                                        ▼
                                          /speckit.adik.sdk       ← generate multi-language SDKs
                                                        │
                                                        ▼
                                          /speckit.adik.boilerplate ← scaffold integration examples
```

The ADIK extension would slot naturally after `/speckit.implement` as a post-implementation SDK
generation phase, or alongside it as a parallel SDK-first development track.

### Publishing to the Spec Kit Community Catalog

The Spec Kit community catalog (`extensions/catalog.community.json`) accepts submissions via Pull
Request to `github/spec-kit`. The submission process:

1. Build and test the extension against a real Spec Kit project
2. Create a GitHub release with semantic versioning (e.g., `v1.0.0`)
3. Submit a PR to `github/spec-kit` adding the entry to `catalog.community.json` and updating
   `extensions/README.md`
4. After merge, the extension becomes discoverable via `specify extension search`

The extension category would be: `code`, effect: `Read+Write` — it reads spec artifacts and generates
SDK files.

---

## Proposing an Extension: What to Build

To submit a meaningful, high-quality ADIK extension to the Spec Kit catalog, the following artifacts
are needed. This is a concrete roadmap:

### Milestone 1 — Minimum Viable Extension (MVP)

| Deliverable | Description |
|---|---|
| `extension.yml` | Manifest declaring extension ID, version, author, commands, and templates |
| `/speckit.adik.registry` template | Command that invokes ADIK's Codebase Analyst agent, using any `contracts/api-spec.json` found in the current feature directory as seed input |
| `/speckit.adik.sdk` template | Command that invokes ADIK's Builder agent to generate TypeScript + Python SDKs from `Registry.md` |
| README | Installation guide, workflow diagrams, prerequisites (Python 3.11+, ADIK deployed in repo) |
| Integration test | One end-to-end test using Spec Kit's Taskify demo project |

### Milestone 2 — Full Integration

| Deliverable | Description |
|---|---|
| OpenAPI → Registry bridge | ADIK Codebase Analyst reads `contracts/api-spec.json` as a first-class input |
| Per-feature registry partitions | ADIK supports `Registry.<feature>.md` aligned with Spec Kit's `001-feature-name` structure |
| Spec traceability fields | `specRef` optional field in Registry symbols linking to `specs/001-xxx/spec.md` |
| `/speckit.adik.status` template | Diff Registry against generated SDKs; report which symbols require regeneration |
| `/speckit.adik.boilerplate` template | Generate framework-idiomatic boilerplate post-SDK-generation |

### Milestone 3 — Community Catalog Submission

| Deliverable | Description |
|---|---|
| Published GitHub release | `spec-kit-adik` v1.0.0 release with zip artifact |
| PR to `github/spec-kit` | Add entry to `extensions/catalog.community.json` and `extensions/README.md` |
| Community walkthrough | A community walkthrough demo (similar to Spec Kit's existing walkthroughs) showing the full Spec Kit + ADIK workflow end-to-end |

---

## Unique Benefits ADIK Offers That Spec Kit Does Not

| Capability | Spec Kit | ADIK |
|---|---|---|
| **Multi-language SDK generation** | ❌ No | ✅ TypeScript, Python, C#, Go, Java, Kotlin |
| **Symbol registry** | ❌ No dedicated registry | ✅ `Registry.md` — structured, versioned, machine-readable |
| **Self-maintaining SDKs via CI** | ❌ Manual re-run required | ✅ CI pipeline regenerates on every commit |
| **Framework-idiomatic boilerplate** | ❌ Left to developer | ✅ NestJS, FastAPI, ASP.NET DI wiring, retry wrappers |
| **AI self-embedding** | ❌ Not produced | ✅ Embeds SDK context into Copilot/Claude/Cursor automatically |
| **MCP Server** | ❌ No | ✅ Full pipeline exposed as MCP tools |
| **Existing codebase analysis** | ✅ Brownfield support exists | ✅ Codebase Analyst reads any existing source code |
| **Registry validation gate** | ❌ No | ✅ `skills/registry-validator.skill.md` — mandatory pre-generation |
| **Append-only audit trail** | ❌ No | ✅ `adik.audit.log` NDJSON build trail |
| **Clean eject** | ❌ Manual removal | ✅ `scripts/adik-eject.py` — one command, zero residue |
| **Spec + plan workflow** | ✅ Core capability | ❌ Not in scope |
| **Multi-agent AI support (20+)** | ✅ Core capability | ✅ Via self-embedding |
| **Extension/preset system** | ✅ Core capability | ✅ Agent/skill architecture |

---

## Recommended Next Steps

### Immediate Actions

1. **Read the Spec Kit extension development guide** — [`github/spec-kit/extensions/EXTENSION-DEVELOPMENT-GUIDE.md`](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-DEVELOPMENT-GUIDE.md)
   to understand exact manifest format and command template requirements.

2. **Open a GitHub Discussion in `github/spec-kit`** — signal intent to build an ADIK extension.
   Community visibility early prevents duplication and invites collaboration. The Spec Kit maintainers
   are active and welcoming to contributors.

3. **Map the OpenAPI → Registry bridge** — identify the minimal ADIK Codebase Analyst changes needed
   to accept `contracts/api-spec.json` as seed input for `Registry.md`. This is the critical technical
   integration point.

### Medium-Term Investigations

4. **Evaluate SDD for ADIK's own development** — ADIK could adopt Spec Kit for its own feature
   development. This would produce a `specs/` directory in the ADIK repository, making every
   framework change traceable to a formal specification. ADIK would then use itself (adik) to generate
   its own MCP server and agent SDKs. The two frameworks feeding each other is a compelling narrative.

5. **Explore a shared contract format** — Investigate whether ADIK's `Registry.md` format and Spec
   Kit's `contracts/api-spec.json` (OpenAPI) could share a common representation, or define a
   well-specified transformation between them. A formal ADIK <-> OpenAPI bridge would make ADIK
   compatible with any OpenAPI-aware toolchain, not just Spec Kit.

6. **Contribute to SDD community documentation** — Write a community walkthrough for the Spec Kit
   repository demonstrating the Spec Kit → ADIK workflow. The existing walkthroughs cover .NET,
   Spring Boot, Go, and ASP.NET — an ADIK integration walkthrough would be novel and add genuine
   value to both communities.

7. **Consider a `speckit.adik` preset** — beyond the extension, a preset could reshape Spec Kit's
   spec and plan templates to produce outputs that are maximally compatible with ADIK's Registry
   format — embedding type names, endpoint signatures, and schema structures in a way that the
   Codebase Analyst can more reliably parse.

### Strategic Positioning

8. **Stake a position in the SDD ecosystem early** — The Spec Kit extension catalog is growing
   rapidly (20+ extensions submitted in its first months). SDK generation is currently absent from
   the catalog. Publishing ADIK as the canonical SDK generation extension for Spec Kit establishes
   a durable position in the emerging SDD tooling ecosystem.

9. **Monitor Spec Kit's governance model** — Spec Kit is currently MIT-licensed and backed by GitHub.
   As it matures, understanding its governance, standardization path, and relationship with
   organizations like Anthropic will be important for long-term alignment decisions.

---

## Further Reading

| Resource | Link |
|---|---|
| GitHub Spec Kit repository | [github.com/github/spec-kit](https://github.com/github/spec-kit) |
| Spec Kit documentation | [github.github.io/spec-kit](https://github.github.io/spec-kit/) |
| Spec-Driven Development methodology | [spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md) |
| Spec Kit extension development guide | [extensions/EXTENSION-DEVELOPMENT-GUIDE.md](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-DEVELOPMENT-GUIDE.md) |
| Spec Kit community extension catalog | [extensions/catalog.community.json](https://github.com/github/spec-kit/blob/main/extensions/catalog.community.json) |
| ADIK Manifesto | [docs/specification/manifesto.md](../specification/manifesto.md) |
| ADIK Standard | [docs/specification/standard.md](../specification/standard.md) |
| ADIK Architecture | [docs/specification/architecture.md](../specification/architecture.md) |
