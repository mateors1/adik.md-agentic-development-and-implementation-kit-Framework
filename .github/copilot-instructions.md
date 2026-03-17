# GitHub Copilot Instructions — ADIK Framework Source Repository

This is the **ADIK (Agentic Development and Implementation Kit)** source repository. Copilot must be aware of the following context when assisting with any work in this repository.

---

## What This Repository Is

This repository defines and governs the **ADIK framework standard** — a fully agentic system that produces **adiks** (self-sustaining agentic SDKs) for any project (API, service, or library).

It contains the factory orchestrator and the deployable adik bundle:

| File | Role | Deployed? |
|---|---|---|
| `ADIKbuilder.md` | **Factory orchestrator** — produces specialized adiks from this source repository | No |
| `ADIK.md` | **Standard definition** — defines what ADIK is, its terminology, and contracts | Yes |
| `ADIK.orchestrator.md` | **Operational orchestrator** — the brain inside every adik, drives SDK generation and implementation | Yes |
| `Registry.md` | Symbol registry template (monolithic) | Yes |
| `Registry.index.md` | Partitioned registry master index template | Yes |
| `agents/` | Codebase Analyst and Builder agents | Yes |
| `skills/` | SDK Builder (tier-1 & tier-2), SDK Consumer, Registry Validator, and Vectorize skills | Yes |
| `scripts/` | `adik-embed.py` (deterministic self-embedding), `adik-eject.py` (clean uninstall), and `adik-deploy.py` (factory-side bundle deployment — source repo only, not deployed) | Yes *(except `adik-deploy.py`)* |
| `mcp/` | MCP server definition | Yes |

**Source-only files** (never deployed): `ADIKbuilder.md`, root-level `ADIKBuilderExample.md` (redirect), `docs/`, `CLAUDE.md`, `agents.md`, `.github/`.

**Canonical documentation structure:**
- `docs/manifesto.md` — ADIK philosophy and principles
- `docs/examples/ADIKBuilderExample.md` — step-by-step guide to building your own ADIK
- `docs/red-team-audit-v2.md` — post-v2.0 red-team security audit

---

## Core Principles to Follow

1. **DRYness via Registry** — every symbol lives in `Registry.md` (or a domain partition) once. No SDK artifact defines a type not first declared there.
2. **Context cleanliness** — vectorization logic belongs only in `skills/vectorize.skill.md`; framework hints only in `skills/sdk-consumer.skill.md`; tier-2 languages only in `skills/sdk-builder-tier2.skill.md`; orchestrators stay lean.
3. **Inference over configuration** — ADIK infers project type, framework hints, and vector capabilities automatically. Only configure what cannot be inferred.
4. **Every agent/skill file must be independently readable** by an LLM agent without loading the entire repository.
5. **ADIK.md never modifies source code** — it only generates SDK output and agentic artifact files.
6. **Self-embedding is deterministic** — `scripts/adik-embed.py` manages `<!-- ADIK:START -->`/`<!-- ADIK:END -->` guard blocks. Never edit context files directly; always use the script.
7. **Tier-2 languages are strictly opt-in** — Go, Java, and Kotlin SDK generation requires explicit `tier2Languages` in `adik.config.json`.

---

## Key Contracts

- `ADIK.md`, `ADIK.orchestrator.md`, and `Registry.md`/`Registry.index.md` are deployed as part of every adik (along with `agents/`, `skills/`, `scripts/`, `mcp/`).
- `ADIKbuilder.md` is **never** deployed — it is the factory, not part of the adik.
- When `ADIK.md` or `ADIK.orchestrator.md` changes in a backward-incompatible way, bump the major version in both files and `ADIKbuilder.md`.
- The Registry format uses `<!-- ADIK:<SECTION>:START -->` / `<!-- ADIK:<SECTION>:END -->` markers. Agents parse only content between these markers.
- Context files (`.github/copilot-instructions.md`, `CLAUDE.md`, `agents.md`) use `<!-- ADIK:START -->` / `<!-- ADIK:END -->` guard markers managed by `scripts/adik-embed.py`.
- Tier-2 SDK generation (Go, Java, Kotlin) is handled exclusively by `skills/sdk-builder-tier2.skill.md` and is opt-in via `tier2Languages` in `adik.config.json`.

---

## Self-Embedding Awareness

ADIK is designed to **embed itself** into the agentic context of every project it touches. In this source repository, that means:

- **This file** (`.github/copilot-instructions.md`) — makes Copilot aware of ADIK context.
- **`CLAUDE.md`** (repo root) — makes Claude-based sessions aware of ADIK context.
- **`agents.md`** (repo root) — registers ADIK agents and skills for agentic sessions.

When an adik is deployed to a target repository, `scripts/adik-embed.py` creates or updates
`.github/copilot-instructions.md`, `CLAUDE.md`, and `agents.md` using `<!-- ADIK:START -->`/
`<!-- ADIK:END -->` guard markers — idempotent, no duplication across runs.

---

## When Making Changes

- Always check `ADIKbuilder.md` for the current version and evolution workflow before modifying agents, skills, or orchestrator files.
- When adding a new agent or skill, reference it in `ADIK.orchestrator.md`'s orchestration workflow and Related Files table, and update `README.md` and `agents.md`.
- When changing the Registry schema, update `Registry.md`, `Registry.index.md`, all agents and skills that read/write it, and bump the minor version.
- Keep `docs/examples/ADIKBuilderExample.md` in sync with any changes to the ADIK framework contracts.
- Tier-2 language additions go in `skills/sdk-builder-tier2.skill.md` only. Never add tier-2 logic to `skills/sdk-builder.skill.md`.
- Self-embedding changes go in `scripts/adik-embed.py`. Never instruct agents to edit context files directly.
