# Changelog

## [2.0.0] — Unreleased

- Define the producer flow: generate SDK code and matching agentic elements together.
- Define the consumer flow: implement the completed adik in application code.
- Add native skills, a completed manifest, JSON registry schemas, shared validation,
  packaging, registration, and ownership-aware removal.
- Separate producer architecture from consumer framework compatibility.
- Repair the standard linter, active registry selection, and MCP validation handoff.
- Add a runnable reference bundle, consumer fixtures, diagrams, migration guide,
  updated explanatory artifacts, and a live-agent evaluation protocol.
- Breaking: completed adiks must meet the v2 manifest contract. See the migration guide.

All notable changes to the ADIK framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Previous unreleased notes (1.x)

### Added

- **Spec Kit integration documentation** — `docs/ecosystem/integration-guide.md` with step-by-step
  workflow for using ADIK in GitHub Spec Kit projects.
- **`spec-kit-adik` extension** — `docs/ecosystem/spec-kit-adik/` containing `extension.yml`,
  4 slash command templates, agent command files, and README for the Spec Kit community catalog.
- **Spec Kit contract path** in Codebase Analyst — `agents/codebase-analyst.agent.md` now documents
  scanning `.specify/specs/*/contracts/api-spec.json` as a first-class OpenAPI source.
- **Spec traceability convention** — `tags: ["spec:001-feature"]` pattern documented in
  `docs/specification/standard.md` §5.4 for linking Registry symbols to Spec Kit feature specs.
- **Spec Kit config example** in `docs/getting-started/configuration.md` showing `includePatterns`
  and `partitionMappings` for `.specify/` directory integration.
- **5th Manifesto principle: Composability** — ADIK is designed to be one layer in a larger pipeline,
  not the whole pipeline (`docs/specification/manifesto.md`).
- **Ecosystem & Integrations section** in `README.md` positioning Spec Kit as flagship integration.
- **Spec Kit integration launch posts** in `docs/community/launch-posts.md`.

### Changed

- **ROADMAP v1.1.0** — added Spec Kit extension, OpenAPI 3.1 sync (moved from v1.2.0), Spec Kit
  contract path support, and feature-branch registry partitions as tracked items.

## [1.0.0] — 2026-03-16

> First public release of the ADIK standard. All internal iterations have been compressed
> into this single v1.0.0 release.

### Added (post-initial tag)

- **`mcp/adik_mcp_server.py`** — MCP server Python implementation. 12 tools (8 deterministic,
  3 LLM-dependent, 1 conditional) and 4 resources. Supports stdio and streamable-HTTP transports.
- **`scripts/adik-deploy.py`** — factory-side bundle assembly and deployment script (source repo only — not deployed as part of the adik).
- **`docs/quickstart-guide.md`** — step-by-step deployment guide for new users and evaluators.
- **`docs/configuration.md`** — full `adik.config.json` schema and field reference (extracted from orchestrator).
- **GitHub Sponsors** enabled — `❤️ Sponsor` button active on the repository.

### Changed (post-initial tag)

- **`ADIK.md` split into standard + orchestrator** — `ADIK.md` is now the standard definition
  only (terminology, contracts, principles). The operational orchestrator template that ships
  inside every adik is now `ADIK.orchestrator.md`. All cross-references across the repository
  updated accordingly.
- **`ADIK.orchestrator.md` trimmed by 29%** (6.4K → 4.5K tokens) — configuration schema moved to
  `docs/configuration.md`, file layout condensed to key-paths table, eject section compressed,
  related files replaced with pointers. Reduces LLM context burden during pipeline execution.

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

- **`skills/sdk-builder/SKILL.md`** — Tier-1 SDK generation (TypeScript, Python, C#).
- **`skills/sdk-builder-tier2/SKILL.md`** — Tier-2 SDK generation (Go, Java, Kotlin — opt-in via
  `tier2Languages` in `adik.config.json`). Includes `reactiveProfile` for Java and documented
  Known Limitations for all tier-2 languages.
- **`skills/sdk-consumer/SKILL.md`** — Framework-idiomatic consumption boilerplate with auto-inferred
  `frameworkHints` (React, NestJS, FastAPI, ASP.NET, etc.).
- **`skills/registry-validator/SKILL.md`** — Mandatory three-level validation gate (Structural
  Integrity, Type Consistency, Semantic Plausibility) before any SDK generation.
- **`skills/vectorize/SKILL.md`** — Optional vector embedding subskill (loaded on demand when a
  vector DB is detected).

### Scripts

- **`scripts/adik-embed.py`** — Deterministic self-embedding into `.github/copilot-instructions.md`,
  `CLAUDE.md`, and `agents.md` using `<!-- ADIK:START -->` / `<!-- ADIK:END -->` guard markers.
  Includes `_safe()` sanitization of `adik.config.json` values against template injection.
- **`scripts/adik-eject.py`** — Clean uninstall / eject protocol. Supports `--dry-run`, `--confirm`,
  `--remove-sdk`, and `--keep-scripts`. Non-interactive via `ADIK_EJECT=true`.

### Infrastructure

- **`mcp/adik-mcp-server.md`** — MCP server specification defining ADIK tool schemas and transport config.
- **`mcp/adik_mcp_server.py`** — MCP server Python implementation. 12 tools (8 deterministic,
  3 LLM-dependent, 1 conditional) and 4 resources. Supports stdio and streamable-HTTP
  transports. Run with `python mcp/adik_mcp_server.py` or install via `pip install adik-mcp-server`.
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
