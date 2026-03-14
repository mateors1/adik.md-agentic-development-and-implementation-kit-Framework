# CLAUDE.md — ADIK Framework Source Repository Context

> **Read this file first.** This file establishes the context Claude needs to assist effectively in this repository.

---

## Repository Identity

This is the **ADIK (Agentic Development and Implementation Kit)** source repository — the standard for agentic, automated SDK generation and maintenance.

**GitHub:** `mateors1/adik.md-agentic-development-and-implementation-kit-Framework`

---

## Executive Summary

ADIK is a framework standard that replaces hand-maintained SDKs with an agentic pipeline. A team of cooperating agents reads a project's source code, builds a language-agnostic symbol registry (`Registry.md`), and generates publish-ready SDK packages in TypeScript, Python, and C# (tier-1), with optional Go, Java, and Kotlin support (tier-2, opt-in).

**Reach of ADIK (v2.0):**
- Any project with a public API surface (REST API, gRPC service, or importable library)
- Any codebase in TypeScript, Python, C#, Go, or Java (source analysis)
- Tier-1 SDK output: TypeScript, Python, C#
- Tier-2 SDK output (opt-in): Go, Java, Kotlin
- Partitioned registry for large codebases (auto-triggered at 500+ symbols)
- Environments with or without vector databases (graceful degradation)
- Any agentic environment: GitHub Copilot, Claude, Cursor, or any MCP-compatible client
- CI/CD headless mode via `ADIK_NON_INTERACTIVE=true`

---

## Two Orchestrators

| File | Role | Deployed to target repos? |
|---|---|---|
| `ADIKbuilder.md` | **Framework Orchestrator** — governs the development and release of ADIK itself. Lives only in this repo. | **No** |
| `ADIK.md` | **Implementation Orchestrator** — drives SDK generation in any target project. Copied into target repos. | **Yes** |

Understanding this distinction is essential. `ADIKbuilder.md` is the meta-level; `ADIK.md` is the operational level.

---

## Repository Structure

```
├── README.md                          ← Manifesto + quick start
├── ADIK.md                            ← Implementation orchestrator (deployed) v2.0.0
├── ADIKbuilder.md                     ← Framework orchestrator (source repo only) v2.0.0
├── Registry.md                        ← Symbol registry template (deployed)
├── Registry.index.md                  ← Partitioned registry master index (deployed)
├── CLAUDE.md                          ← This file (source repo only)
├── agents.md                          ← Agent/skill registry for agentic sessions (source repo only)
├── .github/
│   ├── copilot-instructions.md        ← GitHub Copilot context (source repo only)
│   └── workflows/
│       └── adik-self-deploy.yml       ← CI/CD self-deployment workflow
├── docs/
│   ├── manifesto.md                   ← ADIK philosophy and principles
│   ├── red-team-audit-v2.md           ← Post-v2.0 red-team security audit
│   └── examples/
│       └── ADIKBuilderExample.md      ← Step-by-step guide to building your own ADIK
├── agents/
│   ├── builder.agent.md               ← SDK builder agent (deployed)
│   └── codebase-analyst.agent.md     ← Analysis + env probe agent (deployed)
├── scripts/
│   ├── adik-embed.py                  ← Deterministic self-embedding script (deployed)
│   └── adik-eject.py                  ← Clean uninstall / eject script (deployed)
├── skills/
│   ├── sdk-builder.skill.md           ← Tier-1 SDK skill: TypeScript, Python, C# (deployed)
│   ├── sdk-builder-tier2.skill.md     ← Tier-2 SDK skill: Go, Java, Kotlin (opt-in, deployed)
│   ├── sdk-consumer.skill.md          ← Consumption boilerplate skill (deployed)
│   ├── registry-validator.skill.md    ← Registry schema validation skill (deployed)
│   └── vectorize.skill.md             ← Vector embedding subskill (deployed)
└── mcp/
    └── adik-mcp-server.md             ← MCP server definition (deployed)
```

---

## Core Principles

1. **One source of truth.** `Registry.md` (or domain partitions via `Registry.index.md`) is the canonical definition of all symbols. No SDK file may define a type not first declared there.
2. **Inference over configuration.** ADIK detects project type, frameworks, and vector capabilities automatically. Config only for what cannot be inferred.
3. **Context cleanliness.** Each agent/skill file does exactly one thing. Vectorization stays in `skills/vectorize.skill.md`. Framework logic stays in `skills/sdk-consumer.skill.md`. Tier-2 languages stay in `skills/sdk-builder-tier2.skill.md`.
4. **Graceful degradation.** Every feature is additive. Vector mode, MCP server, framework hints, tier-2 languages — all optional. Core pipeline works with zero config.
5. **ADIK.md never modifies source code.** It only generates SDK output and agentic artifact files.
6. **Self-embedding is deterministic.** `scripts/adik-embed.py` manages `<!-- ADIK:START -->`/`<!-- ADIK:END -->` guard blocks in all three context files. Never edit context files directly in agents — always use the script.
7. **Tier-2 languages are opt-in.** Go, Java, and Kotlin SDK generation requires explicit `tier2Languages` configuration.
8. **Registry validation is mandatory.** `skills/registry-validator.skill.md` must pass before any SDK generation begins.

---

## Self-Embedding Protocol

When `ADIK.md` is deployed to a target project, `scripts/adik-embed.py --action upsert` automatically creates or updates:

1. **`.github/copilot-instructions.md`** — ADIK executive summary and project context for GitHub Copilot
2. **`CLAUDE.md`** — ADIK context for Claude-based sessions
3. **`agents.md`** — Agent/skill registration for agentic sessions

All three files use `<!-- ADIK:START -->` / `<!-- ADIK:END -->` guard markers for idempotent,
non-duplicating writes. The script is safe to run multiple times and across different LLM models.

The same files you are reading now (`CLAUDE.md`, `agents.md`, `.github/copilot-instructions.md`) serve the same purpose for *this* source repository.

---

## When Assisting in This Repository

- Check `ADIKbuilder.md` for the current version and evolution rules before modifying agents, skills, or orchestrators.
- When adding or modifying agents/skills, always update the corresponding references in `ADIK.md` (orchestration workflow + Related Files), `ADIKbuilder.md` (file layout), `agents.md`, and `README.md`.
- Keep `docs/examples/ADIKBuilderExample.md` in sync with any ADIK framework contract changes.
- The Registry section marker format is `<!-- ADIK:<SECTION>:START -->` / `<!-- ADIK:<SECTION>:END -->`. Never break this contract.
- The context file guard marker format is `<!-- ADIK:START -->` / `<!-- ADIK:END -->`. Managed by `scripts/adik-embed.py` only.
- Versioning: patch bump for new agents/skills; minor bump for Registry schema changes; major bump for backward-incompatible `ADIK.md` changes.
- Tier-2 language additions always go into `skills/sdk-builder-tier2.skill.md` only.
- Self-embedding changes always go into `scripts/adik-embed.py` only — never instruct agents to edit context files directly.
