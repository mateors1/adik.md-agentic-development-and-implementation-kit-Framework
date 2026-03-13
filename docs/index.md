# ADIK — Agentic Development and Implementation Kit

**ADIK.md** is a fully agentic framework for automating the creation and maintenance of SDKs for any project — whether it is an API, a service, or a library.

---

## What ADIK Does

ADIK inverts the traditional SDK workflow. Instead of hand-maintaining client libraries, a team of specialised agents reads your codebase, builds a language-agnostic symbol registry, and generates publish-ready SDK packages in TypeScript, Python, and C#. When your code changes, the SDK changes automatically.

### Core Pipeline

1. **Codebase Analyst Agent** scans your source and populates `Registry.md` with every public symbol.
2. **Builder Agent** reads the registry and generates complete, idiomatic SDK packages.
3. **SDK Consumer Skill** produces ready-to-use examples and DI wiring — framework-specific when hints are available.
4. **Vectorize Skill** optionally embeds the registry for semantic search when a vector DB is present.

---

## Quick Start

### 1. Add ADIK to Your Repository

Copy the ADIK bundle into the root of the repository whose SDK you want to generate:

```bash
cp -r adik.md-bundle/* /path/to/your/source-repo/
```

### 2. Run the Codebase Analyst Agent

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
output: Registry.md
```

### 3. Run the Builder Agent

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

Generated SDKs appear in `sdk/typescript/`, `sdk/python/`, and `sdk/csharp/`.

---

## Four Core Principles

| Principle | Summary |
|---|---|
| **One Source of Truth** | Every symbol is declared once in `Registry.md` and generated into all target languages |
| **Inference Over Configuration** | ADIK detects frameworks, project type, and vector capabilities automatically |
| **Context Cleanliness** | Each agent and skill file does exactly one thing, keeping every context window manageable |
| **Graceful Degradation** | All features are additive — ADIK works with zero configuration |

---

## Supported Languages

| Language | Package Manager | Output Formats |
|---|---|---|
| TypeScript | npm / pnpm / yarn | ESM + CJS + `.d.ts` |
| Python | pip / poetry / uv | Wheel + sdist |
| C# | NuGet | `.nupkg` |

---

## Key Files

| File | Role | Deployed? |
|---|---|---|
| `ADIK.md` | Implementation orchestrator — drives SDK generation in target repositories | Yes |
| `ADIKbuilder.md` | Framework orchestrator — governs ADIK's own development | No |
| `Registry.md` | DRY symbol registry template | Yes |
| `agents/builder.agent.md` | SDK builder agent | Yes |
| `agents/codebase-analyst.agent.md` | Codebase analysis + frameworkHints inference | Yes |
| `skills/sdk-builder.skill.md` | SDK code-generation skill (TS / Python / C#) | Yes |
| `skills/sdk-consumer.skill.md` | Framework-idiomatic consumption boilerplate | Yes |
| `skills/vectorize.skill.md` | Vector embedding subskill (loaded on demand) | Yes |
| `mcp/adik-mcp-server.md` | MCP server definition | Yes |

---

## Licensing

ADIK uses a dual-license model:

- **Specification** (`ADIK.md`, `ADIKbuilder.md`, `Registry.md`, docs) — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Reference Implementation** (agents, skills, MCP server, `adik-lint.py`) — [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)

See [`LICENSE`](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/LICENSE) for full terms.

---

## Learn More

- [Manifesto](manifesto.md) — The philosophy and principles behind ADIK
- [Build Your Own ADIK](examples/ADIKBuilderExample.md) — Step-by-step guide to implementing the ADIK pattern from scratch
- [GitHub Repository](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework)
