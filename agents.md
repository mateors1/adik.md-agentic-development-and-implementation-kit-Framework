# agents.md — ADIK Framework Source Repository

> **ADIK Self-Embedding:** This file registers all ADIK agents and skills so that any agentic session operating in this repository has full awareness of the framework's capabilities.
>
> **See also:** `CLAUDE.md` for executive summary and context, `.github/copilot-instructions.md` for Copilot context.

---

## ADIK — Framework Orchestrators

This repository contains two orchestrators:

| File | Role |
|---|---|
| `ADIKbuilder.md` | **Framework Orchestrator** — governs development and release of ADIK itself (source repo only, never deployed) |
| `ADIK.md` | **Implementation Orchestrator** — drives SDK generation in target repositories (deployed) |

**Always load `ADIKbuilder.md` first** when working on the ADIK framework itself. Load `ADIK.md` to understand what is deployed to target projects.

---

## Loaded Agents

```yaml
agents:
  - file: agents/builder.agent.md
    role: SDK Builder
    invoked_by: ADIK.md
    delegates_to:
      - skills/sdk-builder.skill.md
      - skills/sdk-consumer.skill.md

  - file: agents/codebase-analyst.agent.md
    role: Codebase Analysis, Environment Probe, Framework Hints Inference
    invoked_by: ADIK.md
    writes_to:
      - Registry.md
      - adik.env.json
    delegates_to:
      - skills/vectorize.skill.md
```

---

## Loaded Skills

```yaml
skills:
  - file: skills/sdk-builder.skill.md
    role: SDK Code Generation (TypeScript, Python, C#)
    invoked_by: agents/builder.agent.md
    reads_from: Registry.md

  - file: skills/sdk-consumer.skill.md
    role: Framework-idiomatic Consumption Boilerplate
    invoked_by: agents/builder.agent.md
    reads_from:
      - Registry.md
      - adik.env.json (frameworkHints)

  - file: skills/vectorize.skill.md
    role: Vector Embedding and Upsert (loaded on demand)
    invoked_by: agents/codebase-analyst.agent.md
    condition: adik.env.json vectorMode == "active"
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
registry: Registry.md
format: ADIK symbol registry (ADIK:<SECTION>:START / ADIK:<SECTION>:END markers)
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
```

---

## Self-Embedding Note

`ADIK.md` and `ADIKbuilder.md` embed themselves into the agentic context of any project they operate in. When `ADIK.md` is deployed to a target project, it creates or updates:

- `.github/copilot-instructions.md` — ADIK project context for GitHub Copilot
- `CLAUDE.md` — ADIK context for Claude-based sessions
- `agents.md` — this file structure, populated for the target project

The files you are reading now serve this same purpose for the ADIK source repository itself.
