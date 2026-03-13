# GitHub Copilot Instructions — ADIK Framework Source Repository

This is the **ADIK (Agentic Development and Implementation Kit)** source repository. Copilot must be aware of the following context when assisting with any work in this repository.

---

## What This Repository Is

This repository defines and governs the **ADIK framework standard** — a fully agentic system for automating the creation and maintenance of SDKs for any project (API, service, or library).

It contains two orchestrators and a deployable bundle:

| File | Role | Deployed? |
|---|---|---|
| `ADIKbuilder.md` | **Source-repo orchestrator** — governs the development, validation, and release of the ADIK framework | No |
| `ADIK.md` | **Implementation orchestrator** — copied into every target repository to drive SDK generation | Yes |
| `Registry.md` | Symbol registry template | Yes |
| `agents/` | Codebase Analyst and Builder agents | Yes |
| `skills/` | SDK Builder, SDK Consumer, and Vectorize skills | Yes |
| `mcp/` | MCP server definition | Yes |

**Source-only files** (never deployed): `ADIKbuilder.md`, root-level `ADIKBuilderExample.md` (redirect), `docs/`, `CLAUDE.md`, `agents.md`, `.github/`.

**Canonical documentation structure:**
- `docs/manifesto.md` — ADIK philosophy and principles
- `docs/examples/ADIKBuilderExample.md` — step-by-step guide to building your own ADIK

---

## Core Principles to Follow

1. **DRYness via Registry** — every symbol lives in `Registry.md` once. No SDK artifact defines a type not first declared there.
2. **Context cleanliness** — vectorization logic belongs only in `skills/vectorize.skill.md`; framework hints only in `skills/sdk-consumer.skill.md`; orchestrators stay lean.
3. **Inference over configuration** — ADIK infers project type, framework hints, and vector capabilities automatically. Only configure what cannot be inferred.
4. **Every agent/skill file must be independently readable** by an LLM agent without loading the entire repository.
5. **ADIK.md never modifies source code** — it only generates SDK output and agentic artifact files.

---

## Key Contracts

- `ADIK.md` is the **only** file that gets deployed to target repositories (along with `Registry.md`, `agents/`, `skills/`, `mcp/`).
- `ADIKbuilder.md` is **never** deployed.
- When `ADIK.md` changes in a backward-incompatible way, bump the major version in both `ADIK.md` and `ADIKbuilder.md`.
- The Registry format uses `ADIK:<SECTION>:START` / `ADIK:<SECTION>:END` markers. Agents parse only content between these markers.

---

## Self-Embedding Awareness

ADIK is designed to **embed itself** into the agentic context of every project it touches. In this source repository, that means:

- **This file** (`.github/copilot-instructions.md`) — makes Copilot aware of ADIK context.
- **`CLAUDE.md`** (repo root) — makes Claude-based sessions aware of ADIK context.
- **`agents.md`** (repo root) — registers ADIK agents and skills for agentic sessions.

When `ADIK.md` is deployed to a target repository, it follows the same embedding pattern — creating or updating `.github/copilot-instructions.md`, `CLAUDE.md`, and `agents.md` in that target project.

---

## When Making Changes

- Always check `ADIKbuilder.md` for the current version and evolution workflow before modifying agents, skills, or orchestrator files.
- When adding a new agent or skill, reference it in `ADIK.md`'s orchestration workflow and Related Files table, and update `README.md`.
- When changing the Registry schema, update `Registry.md`, all agents and skills that read/write it, and bump the minor version.
- Keep `docs/examples/ADIKBuilderExample.md` in sync with any changes to the ADIK framework contracts.
