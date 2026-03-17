# agents.md — ADIK Framework Source Repository

> **ADIK Self-Embedding:** This file registers all ADIK agents and skills so that any agentic session operating in this repository has full awareness of the framework's capabilities.
>
> **See also:** `CLAUDE.md` for executive summary and context, `.github/copilot-instructions.md` for Copilot context.

---

## ADIK — Factory, Standard, and Orchestrator

This repository contains the factory, the standard definition, and the orchestrator template that ships in every adik:

| File | Role |
|---|---|
| `ADIKbuilder.md` | **Factory** — produces specialized adiks (source repo only, never deployed) |
| `ADIK.md` | **Standard Definition** — defines what ADIK is, its terminology, and contracts (deployed) |
| `ADIK.orchestrator.md` | **Operational Orchestrator** — the brain inside every adik, drives SDK generation and implementation in target repositories (deployed) |

**Always load `ADIKbuilder.md` first** when working on the ADIK framework itself. Load `ADIK.md` for the standard definition and `ADIK.orchestrator.md` to understand what ships inside every adik.

---

## Loaded Agents

```yaml
agents:
  - file: agents/builder.agent.md
    role: SDK Builder
    invoked_by: ADIK.orchestrator.md
    delegates_to:
      - skills/registry-validator.skill.md  # mandatory pre-generation gate
      - skills/sdk-builder.skill.md         # tier-1 (TypeScript, Python, C#)
      - skills/sdk-builder-tier2.skill.md   # tier-2 (Go, Java, Kotlin — opt-in)
      - skills/sdk-consumer.skill.md
      - scripts/adik-embed.py               # deterministic self-embedding post-build

  - file: agents/codebase-analyst.agent.md
    role: Codebase Analysis, Environment Probe, Framework Hints Inference, Registry Partitioning
    invoked_by: ADIK.orchestrator.md
    writes_to:
      - Registry.md           # monolithic mode
      - Registry.index.md     # partitioned mode (auto-triggered by size threshold)
      - Registry.<domain>.md  # domain partitions (partitioned mode)
      - adik.env.json
    delegates_to:
      - skills/vectorize.skill.md
```

---

## Loaded Skills

```yaml
skills:
  - file: skills/sdk-builder.skill.md
    role: Tier-1 SDK Code Generation (TypeScript, Python, C#)
    invoked_by: agents/builder.agent.md
    reads_from:
      - Registry.md or Registry.index.md

  - file: skills/sdk-builder-tier2.skill.md
    role: Tier-2 SDK Code Generation (Go, Java, Kotlin — opt-in)
    invoked_by: agents/builder.agent.md
    condition: adik.config.json tier2Languages is non-empty
    reads_from:
      - Registry.md or Registry.index.md

  - file: skills/registry-validator.skill.md
    role: Registry Schema Validation (mandatory pre-generation gate)
    invoked_by: agents/builder.agent.md
    reads_from:
      - Registry.md or Registry.index.md
    writes_to:
      - sdk/VALIDATION_REPORT.md

  - file: skills/sdk-consumer.skill.md
    role: Framework-idiomatic Consumption Boilerplate
    invoked_by: agents/builder.agent.md
    reads_from:
      - Registry.md or Registry.index.md
      - adik.env.json (frameworkHints)

  - file: skills/vectorize.skill.md
    role: Vector Embedding and Upsert (loaded on demand)
    invoked_by: agents/codebase-analyst.agent.md
    condition: adik.env.json vectorMode == "active"
```

---

## Scripts

```yaml
scripts:
  - file: scripts/adik-embed.py
    role: Deterministic self-embedding — manages ADIK guard blocks in context files
    invoked_by: agents/builder.agent.md (post-build)
    actions: [upsert, remove, check]
    targets:
      - .github/copilot-instructions.md
      - CLAUDE.md
      - agents.md

  - file: scripts/adik-eject.py
    role: Clean uninstall / eject — removes all ADIK artefacts from a repository
    invoked_manually: true
    supports_ci: true  # ADIK_EJECT=true env var
    removes:
      - ADIK framework files and directories
      - ADIK guard blocks from context files
      - sdk/ (optional, requires --remove-sdk)

  - file: scripts/adik-deploy.py
    role: Factory-side bundle assembly and deployment — assembles the adik and copies it to target repos
    invoked_manually: true
    source_repo_only: true  # never deployed as part of the adik
    actions: [assemble, deploy]
```

---

## CI/CD Workflows

```yaml
workflows:
  - file: .github/workflows/adik-self-deploy.yml
    role: CI/CD self-deployment — publishes ADIK bundle as <reponame>-ADIK repository
    triggers: [release published, workflow_dispatch]
    requires_secret: ADIK_DEPLOY_TOKEN
    creates_repo: <org>/<reponame>-adik
```

---

## MCP Server

```yaml
mcp:
  - file: mcp/adik-mcp-server.md
    role: Exposes ADIK capabilities to external agentic environments
    transport: [stdio, http+sse]
    defaultPort: 3100
    tools:
      - adik_get_registry
      - adik_build_sdk
      - adik_analyse_codebase
      - adik_scaffold_boilerplate
      - adik_get_symbol
      - adik_get_build_report
      - adik_vector_search  # available when vectorMode is active
```

---

## Registry

```yaml
registry:
  monolithic: Registry.md
  partitioned:
    index: Registry.index.md
    partitions: Registry.<domain>.md
  format: ADIK symbol registry (<!-- ADIK:<SECTION>:START --> / <!-- ADIK:<SECTION>:END --> markers)
  partitionThreshold:
    symbols: 500
    bytes: 204800
  sections:
    - Project Metadata
    - Endpoints
    - Classes
    - Interfaces and Types
    - Schemas
    - Enumerations
    - Functions and Methods
    - Error Catalogue
    - Changelog
```

---

## Documentation

```yaml
docs:
  - file: docs/manifesto.md
    role: ADIK philosophy and principles

  - file: docs/examples/ADIKBuilderExample.md
    role: Step-by-step guide for building a custom ADIK implementation from scratch
    audience: Developers implementing the ADIK pattern independently

  - file: docs/red-team-audit-v2.md
    role: Post-v2.0 red-team security and improvement audit
    audience: Security reviewers, framework maintainers
```

---

## Self-Embedding Note

`ADIK.orchestrator.md` and `ADIKbuilder.md` embed themselves into the agentic context of any project they
operate in. When an adik is deployed to a target project, `scripts/adik-embed.py` creates or
updates:

- `.github/copilot-instructions.md` — ADIK project context for GitHub Copilot
- `CLAUDE.md` — ADIK context for Claude-based sessions
- `agents.md` — this file structure, populated for the target project

All three files use `<!-- ADIK:START -->` / `<!-- ADIK:END -->` guard markers to ensure
idempotent, non-duplicating writes.

The files you are reading now serve this same purpose for the ADIK source repository itself.
