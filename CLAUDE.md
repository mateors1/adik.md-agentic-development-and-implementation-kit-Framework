# CLAUDE.md — ADIK Framework Source Repository Context

> **Read this file first.** This file establishes the context Claude needs to assist effectively in this repository.

---

## Repository Identity

This is the **ADIK (Agentic Development and Implementation Kit)** source repository — the standard for agentic, automated SDK generation and maintenance.

**GitHub:** `mateors1/adik.md-agentic-development-and-implementation-kit-Framework`

---

## Executive Summary

ADIK is a framework standard that replaces hand-maintained SDKs with an agentic pipeline. A team of cooperating agents reads a project's source code, builds a language-agnostic symbol registry (`Registry.md`), and generates publish-ready SDK packages in TypeScript, Python, and C#.

**Reach of ADIK:**
- Any project with a public API surface (REST API, gRPC service, or importable library)
- Any codebase in TypeScript, Python, C#, Go, or Java (source analysis)
- Any target consuming language: TypeScript, Python, or C# (SDK output)
- Environments with or without vector databases (graceful degradation)
- Any agentic environment: GitHub Copilot, Claude, Cursor, or any MCP-compatible client

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
├── ADIK.md                            ← Implementation orchestrator (deployed)
├── ADIKbuilder.md                     ← Framework orchestrator (source repo only)
├── Registry.md                        ← Symbol registry template (deployed)
├── CLAUDE.md                          ← This file (source repo only)
├── agents.md                          ← Agent/skill registry for agentic sessions (source repo only)
├── .github/
│   └── copilot-instructions.md        ← GitHub Copilot context (source repo only)
├── docs/
│   ├── manifesto.md                   ← ADIK philosophy and principles
│   └── examples/
│       └── ADIKBuilderExample.md      ← Step-by-step guide to building your own ADIK
├── agents/
│   ├── builder.agent.md               ← SDK builder agent (deployed)
│   └── codebase-analyst.agent.md     ← Analysis + env probe agent (deployed)
├── skills/
│   ├── sdk-builder.skill.md           ← SDK code-generation skill (deployed)
│   ├── sdk-consumer.skill.md          ← Consumption boilerplate skill (deployed)
│   └── vectorize.skill.md             ← Vector embedding subskill (deployed)
└── mcp/
    └── adik-mcp-server.md             ← MCP server definition (deployed)
```

---

## Core Principles

1. **One source of truth.** `Registry.md` is the canonical definition of all symbols. No SDK file may define a type not first declared there.
2. **Inference over configuration.** ADIK detects project type, frameworks, and vector capabilities automatically. Config only for what cannot be inferred.
3. **Context cleanliness.** Each agent/skill file does exactly one thing. Vectorization stays in `skills/vectorize.skill.md`. Framework logic stays in `skills/sdk-consumer.skill.md`.
4. **Graceful degradation.** Every feature is additive. Vector mode, MCP server, framework hints — all optional. Core pipeline works with zero config.
5. **ADIK.md never modifies source code.** It only generates SDK output and agentic artifact files.
6. **Self-embedding.** ADIK embeds itself into the agentic context of every project it touches (Copilot instructions, CLAUDE.md, agents.md) so the AI is always aware of its presence and capabilities.

---

## Self-Embedding Protocol

When `ADIK.md` is deployed to a target project, it automatically creates or updates:

1. **`.github/copilot-instructions.md`** — ADIK executive summary and project context for GitHub Copilot
2. **`CLAUDE.md`** — ADIK context for Claude-based sessions
3. **`agents.md`** — Agent/skill registration for agentic sessions

This ensures that any AI assistant working in the target project is always aware that ADIK is present and active.

The same files you are reading now (`CLAUDE.md`, `agents.md`, `.github/copilot-instructions.md`) serve the same purpose for *this* source repository.

---

## When Assisting in This Repository

- Check `ADIKbuilder.md` for the current version and evolution rules before modifying agents, skills, or orchestrators.
- When adding or modifying agents/skills, always update the corresponding references in `ADIK.md` (orchestration workflow + Related Files), `ADIKbuilder.md` (file layout), and `README.md`.
- Keep `docs/examples/ADIKBuilderExample.md` in sync with any ADIK framework contract changes.
- The Registry marker format is `<!-- ADIK:<SECTION>:START -->` / `<!-- ADIK:<SECTION>:END -->`. Never break this contract.
- Versioning: patch bump for new agents/skills; minor bump for Registry schema changes; major bump for backward-incompatible `ADIK.md` changes.
