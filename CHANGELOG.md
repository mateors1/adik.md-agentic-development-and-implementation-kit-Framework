# Changelog

All notable changes to the ADIK framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **`scripts/adik-deploy.py`** — factory-side bundle assembly and deployment script (source repo only — not deployed as part of the adik).
- **`docs/quickstart-guide.md`** — step-by-step deployment guide for new users and evaluators.
- **`docs/configuration.md`** — full `adik.config.json` schema and field reference (extracted from orchestrator).
- **GitHub Sponsors** enabled — `❤️ Sponsor` button active on the repository.

### Changed

- **`ADIK.md` split into standard + orchestrator** — `ADIK.md` is now the standard definition
  only (terminology, contracts, principles). The operational orchestrator template that ships
  inside every adik is now `ADIK.orchestrator.md`. All cross-references across the repository
  updated accordingly.
- **`ADIK.orchestrator.md` trimmed by 29%** (6.4K → 4.5K tokens) — configuration schema moved to
  `docs/configuration.md`, file layout condensed to key-paths table, eject section compressed,
  related files replaced with pointers. Reduces LLM context burden during pipeline execution.

## [1.0.0] — 2026-03-16

> First public release of the ADIK standard. All internal iterations have been compressed
> into this single v1.0.0 release.

### Core Framework

- **`ADIK.md`** — Standard definition — what ADIK is, its terminology, and contracts.
- **`ADIK.orchestrator.md`** — Operational orchestrator — the brain inside every adik. Drives the
  end-to-end analysis → validate → build → implement → embed pipeline.
- **`ADIKbuilder.md`** — Factory orchestrator for this source repository. Produces specialized
  adiks (self-sustaining agentic SDK bundles). Never deployed.
- **`Registry.md`** — Language-agnostic symbol registry template (monolithic mode).
- **`Registry.index.md`** — Partitioned registry master index for large codebases.

### Agents

- **`agents/builder.agent.md`** — SDK Builder Agent. Orchestrates validation, tier-1 and tier-2
  SDK generation, post-generation type-checking, audit logging, and self-embedding.
- **`agents/codebase-analyst.agent.md`** — Codebase Analyst Agent. Environment probe, framework
  hints inference, dev-state tracking, symbol discovery, and registry population.

### Skills

- **`skills/sdk-builder.skill.md`** — Tier-1 SDK generation (TypeScript, Python, C#).
- **`skills/sdk-builder-tier2.skill.md`** — Tier-2 SDK generation (Go, Java, Kotlin — opt-in via
  `tier2Languages` in `adik.config.json`). Includes `reactiveProfile` for Java and documented
  Known Limitations for all tier-2 languages.
- **`skills/sdk-consumer.skill.md`** — Framework-idiomatic consumption boilerplate with auto-inferred
  `frameworkHints` (React, NestJS, FastAPI, ASP.NET, etc.).
- **`skills/registry-validator.skill.md`** — Mandatory three-level validation gate (Structural
  Integrity, Type Consistency, Semantic Plausibility) before any SDK generation.
- **`skills/vectorize.skill.md`** — Optional vector embedding subskill (loaded on demand when a
  vector DB is detected).

### Scripts

- **`scripts/adik-embed.py`** — Deterministic self-embedding into `.github/copilot-instructions.md`,
  `CLAUDE.md`, and `agents.md` using `<!-- ADIK:START -->` / `<!-- ADIK:END -->` guard markers.
  Includes `_safe()` sanitization of `adik.config.json` values against template injection.
- **`scripts/adik-eject.py`** — Clean uninstall / eject protocol. Supports `--dry-run`, `--confirm`,
  `--remove-sdk`, and `--keep-scripts`. Non-interactive via `ADIK_EJECT=true`.

### Infrastructure

- **`mcp/adik-mcp-server.md`** — MCP server exposing ADIK capabilities to any MCP-compatible client.
- **`.github/workflows/adik-self-deploy.yml`** — CI/CD self-deployment workflow. Uses fine-grained
  PAT with least-privilege scopes. Defaults to `private` repository visibility.
- **`.github/workflows/adik-ci.yml`** — Optional integration testing workflow. Validates registry
  markers and type-checks all generated SDKs (TS/Python/C#/Go/Java/Kotlin).
- **`adik-lint.py`** — Specification linter for `ADIK.md` structural requirements.

### Key Features

- **Registry partitioning** — auto-triggered at ≥ 500 symbols or ≥ 200 KB. Configurable
  `partitionStrategy`: `"auto"` (namespace-based), `"manual"` (explicit mappings), `"file"`
  (directory-based).
- **Headless / CI mode** — `ADIK_NON_INTERACTIVE=true` and `ADIK_STARTUP_MODE` bypass interactive
  prompts for pipeline use.
- **Audit log** — `adik.audit.log` append-only NDJSON trail with commit SHA, registry hash,
  validation status, type-check results, and exit status per build.
- **Post-generation type-checking** — `tsc`, `mypy`, `dotnet build`, `go build`, `mvn`/`gradle`
  run after SDK generation. Advisory by default; blocking via `ADIK_STRICT_TYPECHECK=true`.
- **Crosstailing prevention** — dev-state snapshot in `adik.env.json` detects stale artifacts from
  prior runs.

### Documentation

- **`docs/standard.md`** — Formal ADIK Standard Specification.
- **`docs/architecture.md`** — System architecture with Mermaid diagrams.
- **`docs/manifesto.md`** — ADIK philosophy and principles.
- **`docs/red-team-audit-v2.md`** — Security audit and risk matrix. All pre-release vulnerabilities
  resolved; one systemic item (S-01: LLM-native framework lacks runtime guarantees) partially
  mitigated via `adik-ci.yml`.
- **`docs/examples/`** — Pre-deployment walkthrough, three full showcases (Payments API, Task
  Manager, Chat Service), scaffold master prompt, and Build Your Own ADIK guide.
- **MkDocs Material site** — `mkdocs.yml` with auto-deploy to GitHub Pages.

### Licensing

- **Specification** (ADIK.md, ADIK.orchestrator.md, ADIKbuilder.md, Registry.md, docs/) — CC BY 4.0
- **Reference Implementation** (agents/, skills/, scripts/, mcp/, adik-lint.py) — Apache 2.0
