# ADIK.md — Agentic Development and Implementation Kit

> **Version:** 1.0.0
> This file defines the **ADIK standard** — what the framework is, what an adik contains, and the contracts every implementation must follow. For the operational orchestrator template, see [`ADIK.orchestrator.md`](ADIK.orchestrator.md).

---

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- THE STANDARD                                                               -->
<!-- This section defines what ADIK is. It is reference material that explains  -->
<!-- the framework, its terminology, what an adik contains, and the contracts   -->
<!-- that all implementations must follow.                                      -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

## What Is ADIK?

**ADIK (Agentic Development and Implementation Kit)** is an open framework standard for fully automated, AI-driven SDK generation, implementation, and maintenance. It defines how cooperating AI agents analyze a codebase, build a language-agnostic symbol registry, generate publish-ready SDK packages, produce framework-idiomatic integration boilerplate, and self-embed into developer tools — as a single, self-sustaining deliverable.

## What Is an adik?

An **adik** (lowercase) is the deliverable — a **self-sustaining agentic SDK**. It is a complete bundle containing:

| Component | Role |
|---|---|
| `ADIK.md` | Standard definition — what ADIK is and the contracts it follows |
| `ADIK.orchestrator.md` | Operational orchestrator — drives the pipeline |
| `agents/` | Codebase Analyst + Builder agents |
| `skills/` | SDK Builder (tier-1 & tier-2), SDK Consumer, Registry Validator, Vectorize |
| `Registry.md` | Language-agnostic symbol registry — populated from the target codebase |
| `Registry.index.md` | Master index for partitioned registries (auto-created for large projects) |
| `sdk/` | Generated SDK packages — publish-ready output in up to 6 languages |
| `scripts/` | Self-embedding (`adik-embed.py`) + clean eject (`adik-eject.py`) |
| `mcp/` | MCP server — exposes the pipeline to any agentic environment |

What distinguishes an adik from a traditional generated SDK:

1. **Self-sustaining** — it carries the agents that produced it, so the SDKs regenerate automatically on every commit.
2. **Implementation-aware** — it doesn't just deliver packages; it generates framework-idiomatic integration code (DI wiring, retry logic, serialization helpers, examples).
3. **AI-aware** — it self-embeds into developer tools (Copilot, Claude, Cursor) so any assistant in the repo understands the SDK and can help implement it.
4. **Ejectable** — one command removes everything; source code is never touched.

> **Convention:** "ADIK" (uppercase) refers to the framework standard. "adik" (lowercase) refers to a specific deployed instance — the self-sustaining agentic SDK.

## How ADIKbuilder Produces an adik

`ADIKbuilder.md` is the **factory** that lives in the ADIK source repository. It assembles the adik bundle (this file + agents + skills + scripts + registry templates + MCP) and deploys it into target repositories. On first run, this orchestrator tailors itself to the target project — auto-filling project metadata, detecting frameworks, and configuring languages.

```
ADIKbuilder.md (factory, never deployed)
    │
    └──► produces adik bundle ──► deployed to target repo
              │
              ├── ADIK.md              ← standard definition
              ├── ADIK.orchestrator.md ← operational orchestrator (specializes on first run)
              ├── agents/              ← analysis + builder agents
              ├── skills/              ← generation, validation, consumer, vectorize
              ├── scripts/             ← embed + eject
              ├── mcp/                 ← MCP server
              ├── Registry.md          ← empty template (populated on first run)
              └── Registry.index.md
```

## Lifecycle of an adik

```
Deploy ──► First Run ──► Specialized ──► Continuous Sync
  │            │              │                │
  │            │              │                └── every commit re-runs
  │            │              │                    steps 0–3, regenerates
  │            │              │                    only what changed
  │            │              └── ADIK.orchestrator.md auto-fills project metadata,
  │            │                  Registry is populated, SDKs generated,
  │            │                  context files embedded
  │            └── startup prompt: blanket or guided mode
  └── adik bundle copied into target repo
```

## Reach of an adik

Once deployed and initialized, an adik covers the following lifecycle automatically:

| Stage | What the adik Does |
|---|---|
| **Analysis** | Scans the source codebase and populates `Registry.md` (or partitioned `Registry.<domain>.md` files) with every public symbol |
| **Framework inference** | Detects frameworks in use (React, NestJS, FastAPI, etc.) without manual configuration |
| **SDK generation** | Emits complete, publish-ready packages in TypeScript, Python, C#, and optionally Go, Java, or Kotlin (tier-2, opt-in) |
| **Implementation boilerplate** | Generates idiomatic usage examples, DI wiring, retry wrappers, and serialization helpers per framework |
| **Continuous sync** | Re-runs on every commit, regenerating only what changed |
| **Vector search** | Optionally embeds the Registry for semantic symbol lookup (when a vector DB is present) |
| **MCP server** | Exposes all capabilities to any connected agentic environment |
| **Context embedding** | Injects itself into `.github/copilot-instructions.md`, `CLAUDE.md`, and `agents.md` so the AI always knows the adik is active |

## Standard Contracts

These contracts apply to every ADIK-compliant implementation:

1. **Registry is the single source of truth.** No SDK artifact may define a type or schema not first declared in `Registry.md` (or a domain partition).
2. **The orchestrator never modifies source code.** It only generates SDK output and agentic artifact files.
3. **Self-embedding is deterministic and idempotent.** `scripts/adik-embed.py` manages `<!-- ADIK:START -->` / `<!-- ADIK:END -->` guard blocks. Agents must never edit context files directly.
4. **Registry validation is mandatory before generation.** The Registry Validator must report `PASS` or `WARN` before the Builder Agent proceeds. `FAIL` aborts the run.
5. **Tier-2 languages are strictly opt-in.** Go, Java, and Kotlin SDK generation requires explicit `tier2Languages` in `adik.config.json`.
6. **Every agent and skill file must be independently readable** by an LLM agent without loading the entire repository.
7. **Vectorization is isolated.** All vector-store interactions live in `skills/vectorize.skill.md`. The orchestrator and agents never contain embedding logic.
8. **Registry markers use the format** `<!-- ADIK:<SECTION>:START -->` / `<!-- ADIK:<SECTION>:END -->`.
9. **Context file markers use the format** `<!-- ADIK:START -->` / `<!-- ADIK:END -->`.
10. **An adik is ejectable.** `scripts/adik-eject.py` must cleanly remove all ADIK artifacts without touching source code.

---

## Related Documents

| Document | Role | Audience |
|---|---|---|
| **[`ADIK.orchestrator.md`](ADIK.orchestrator.md)** | Operational orchestrator template — deployed inside every adik | AI agents, developers deploying ADIK |
| **[`docs/specification/standard.md`](docs/specification/standard.md)** | Formal specification (RFC-style, conformance levels, MUST/SHOULD) | Implementors building ADIK-compatible tools |
| **[`ADIKbuilder.md`](ADIKbuilder.md)** | Factory orchestrator — produces specialized adiks (source repo only) | ADIK framework maintainers |
| **[`README.md`](README.md)** | Quick start, repository layout, getting started | Everyone |
