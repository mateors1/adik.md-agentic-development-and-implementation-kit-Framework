# ADIK.md — Agentic Development and Implementation Kit

> **Version:** 1.0.0
> **Role:** Orchestrator
> **Scope:** Source repository — resides alongside the codebase whose SDK is being built

---

## Purpose

ADIK.md is the root orchestrator of the Agentic Development and Implementation Kit. It lives inside the **source repository** and drives the automated, end-to-end creation of a fully functional SDK for the project it accompanies.

ADIK.md is responsible for:

1. **Analysing the source project** to determine its nature (service, API, or library).
2. **Orchestrating all agents and skills** required to produce SDK artifacts.
3. **Keeping the Registry up to date** — the single source of truth for all exported symbols.
4. **Generating SDK packages** in TypeScript, Python, and C# that stay in sync with every new feature.
5. **Producing consumption artifacts** (classes, serialization helpers, boilerplate) for downstream consumers.
6. **Exposing an MCP server** so the ADIK can be driven from any agentic environment in the target codebase.
7. **Integrating cleanly with the host repository's `agents.md`** so all context and skills persist.

---

## Project-Type Detection

Before delegating work, ADIK.md instructs the `Codebase Analyst Agent` to classify the source project using the following heuristic:

| Signal | Detected Type |
|---|---|
| HTTP endpoints / OpenAPI spec present | **API** |
| Deployed runtime, message queue, or gRPC interface | **Service** |
| Published package manifest (npm, PyPI, NuGet) with no server entry-point | **Library** |

The detected type is recorded in `Registry.md` under `## Project Metadata` and governs which SDK-generation strategy is applied.

---

## Orchestration Workflow

```
ADIK.md
  │
  ├─► [1] Codebase Analyst Agent      → analyses repo, populates Registry.md
  │         (agents/codebase-analyst.agent.md)
  │
  ├─► [2] Builder Agent               → reads Registry.md, delegates to skills
  │         (agents/builder.agent.md)
  │         │
  │         ├─► SDK Builder Skill     → emits TS / Python / C# SDK packages
  │         │     (skills/sdk-builder.skill.md)
  │         │
  │         └─► SDK Consumer Skill    → emits boilerplate, classes, serializers
  │               (skills/sdk-consumer.skill.md)
  │
  └─► [3] MCP Server                  → exposes ADIK capabilities to external agents
            (mcp/adik-mcp-server.md)
```

### Step 1 — Codebase Analysis

Invoke the **Codebase Analyst Agent**:

```
@agent codebase-analyst
task: analyse-and-register
target: <path-to-source-repo>
output: Registry.md
```

The agent scans all source files, identifies every public symbol (functions, classes, interfaces, schemas, enumerations, endpoints), and writes them to `Registry.md` in the canonical format.

### Step 2 — SDK Generation

Invoke the **Builder Agent** once the registry is populated:

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

The builder delegates to `sdk-builder.skill.md` per language and `sdk-consumer.skill.md` for boilerplate.

### Step 3 — Continuous Sync

Every time new functionality is merged into the source repo, ADIK.md triggers a re-run of steps 1 and 2:

```
@agent codebase-analyst
task: diff-and-update
since: <last-registry-commit-sha>
output: Registry.md
```

Only changed symbols trigger incremental SDK regeneration, keeping build times short.

---

## Integration with `agents.md`

After the first successful run, ADIK.md appends the following snippet to the repository's root `agents.md` (or creates one if absent):

```markdown
## ADIK — SDK Orchestrator

Loaded agents:
- agents/builder.agent.md
- agents/codebase-analyst.agent.md

Loaded skills:
- skills/sdk-builder.skill.md
- skills/sdk-consumer.skill.md

Registry: Registry.md
MCP server: mcp/adik-mcp-server.md
```

This ensures all ADIK agents and skills are available in any agentic session that loads the repository.

---

## File Layout

```
<source-repo>/
├── ADIK.md                          ← this file (orchestrator)
├── Registry.md                      ← DRY symbol registry
├── agents/
│   ├── builder.agent.md             ← SDK builder agent
│   └── codebase-analyst.agent.md   ← codebase analysis subagent
├── skills/
│   ├── sdk-builder.skill.md         ← SDK code-generation skill
│   └── sdk-consumer.skill.md        ← consumption boilerplate skill
└── mcp/
    └── adik-mcp-server.md           ← MCP server definition
```

---

## Configuration

ADIK.md reads configuration from the optional `adik.config.json` file in the repository root. If the file is absent, all defaults apply.

```jsonc
{
  "projectType": "auto",            // "auto" | "api" | "service" | "library"
  "sdkLanguages": ["typescript", "python", "csharp"],
  "outputDir": "./sdk",
  "registryPath": "./Registry.md",
  "mcpPort": 3100,
  "syncOnCommit": true,             // re-run analysis on every commit
  "includePatterns": ["src/**/*"],
  "excludePatterns": ["**/*.test.*", "**/*.spec.*"]
}
```

---

## Constraints and Principles

- **DRYness is enforced through the Registry.** No SDK artifact may define a type or schema that is not first declared in `Registry.md`.
- **ADIK.md never modifies source code.** It only generates SDK output directories and agentic artifact files.
- **Language-specific output is self-contained.** Each generated SDK package includes its own `README`, type definitions, and serialization helpers so it can be published independently.
- **The MCP server is optional.** Teams that do not need remote orchestration can omit the MCP component entirely.

---

## Related Files

| File | Role |
|---|---|
| `Registry.md` | Single source of truth for all exported symbols |
| `agents/builder.agent.md` | Orchestrates SDK generation across languages |
| `agents/codebase-analyst.agent.md` | Analyses source code and populates Registry |
| `skills/sdk-builder.skill.md` | Generates SDK packages per language |
| `skills/sdk-consumer.skill.md` | Generates consumption boilerplate |
| `mcp/adik-mcp-server.md` | MCP server for external agent integration |
