# CLAUDE.md — ADIK Framework Source Repository Context

> **Read this file first.** This file gives Claude the minimum context needed to assist in this repository. For full agent/skill details, see `agents.md`.

---

## Repository Identity

This is the **ADIK (Agentic Development and Implementation Kit)** source repository — the factory that produces **adiks** (self-sustaining agentic SDKs).

**GitHub:** `mateors1/adik.md-agentic-development-and-implementation-kit-Framework`
**Version:** 1.0.0

---

## Executive Summary

ADIK replaces hand-maintained SDKs with **adiks** — self-sustaining agentic SDK bundles. An adik is a complete deliverable: cooperating AI agents that read a project's source code, build a symbol registry (`Registry.md`), generate publish-ready SDK packages in TypeScript, Python, C# (tier-1) with optional Go, Java, Kotlin (tier-2, opt-in), produce framework-idiomatic implementation boilerplate, and self-embed into your AI tools. The adik carries its own maintenance pipeline — SDKs stay in sync on every commit, automatically.

> **Terminology:** "ADIK" (uppercase) = the framework standard. "adik" (lowercase) = a specific deployed instance — the self-sustaining agentic SDK.

**v1.0.0 highlights:** configurable `partitionStrategy` (auto/manual/file) for registry domain assignment, append-only `adik.audit.log` NDJSON build trail, `adik-ci.yml` integration testing workflow, post-generation type-checking, and a red-team-audited security posture.

---

## Two Orchestrators

| File | Role | Deployed? |
|---|---|---|
| `ADIKbuilder.md` | **Factory** — produces specialized adiks | No |
| `ADIK.md` | **Standard Definition** — defines what ADIK is, its terminology, and contracts | Yes |
| `ADIK.orchestrator.md` | **Operational Orchestrator** — the brain inside every adik, drives SDK generation in target projects | Yes |

`ADIKbuilder.md` is the factory; `ADIK.md` is the standard definition; `ADIK.orchestrator.md` is the orchestrator inside every adik. Always check `ADIKbuilder.md` first when working on the framework itself.

---

## Key Contracts

1. **Registry is the single source of truth.** No SDK file may define a type not declared in `Registry.md` (or domain partitions via `Registry.index.md`).
2. **ADIK.md never modifies source code** — only generates SDK output and agentic artifacts.
3. **Self-embedding is deterministic** — `scripts/adik-embed.py` manages guard blocks. Never edit context files directly.
4. **Registry validation is mandatory** — `skills/registry-validator.skill.md` must pass before SDK generation.
5. **Tier-2 languages are opt-in** — require `tier2Languages` in `adik.config.json`.
6. **Registry markers:** `<!-- ADIK:<SECTION>:START -->` / `<!-- ADIK:<SECTION>:END -->`.
7. **Context file markers:** `<!-- ADIK:START -->` / `<!-- ADIK:END -->`.

---

## When Assisting in This Repository

- Check `ADIKbuilder.md` for version and evolution rules before modifying agents, skills, or orchestrators.
- When adding/modifying agents or skills, update references in `ADIK.orchestrator.md`, `ADIKbuilder.md`, `agents.md`, and `README.md`.
- Keep `docs/examples/ADIKBuilderExample.md` in sync with framework contract changes.
- Versioning: patch for new agents/skills; minor for Registry schema changes; major for backward-incompatible `ADIK.md` or `ADIK.orchestrator.md` changes.
- Tier-2 additions go in `skills/sdk-builder-tier2.skill.md` only.
- Self-embedding changes go in `scripts/adik-embed.py` only.
- Use `scripts/adik-deploy.py` for factory-side bundle assembly and deployment to target repositories (source repo only — never deployed as part of the adik).
- Full agent/skill/script registry is in `agents.md` — do not duplicate it here.
