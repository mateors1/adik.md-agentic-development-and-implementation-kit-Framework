# Builder Agent — `agents/builder.agent.md`

> **Role:** SDK Builder
> **Type:** Orchestrator Agent
> **Invoked by:** `ADIK.md`
> **Delegates to:** `skills/sdk-builder.skill.md`, `skills/sdk-consumer.skill.md`

---

## Purpose

The Builder Agent is the primary execution agent of the ADIK framework. It reads the fully populated `Registry.md`, determines the generation strategy based on `projectType`, and coordinates the SDK Builder and SDK Consumer skills to produce complete, publish-ready SDK packages in every configured target language.

---

## Responsibilities

1. **Validate the Registry** — ensure `Registry.md` is populated and internally consistent before proceeding.
2. **Select generation strategy** — choose API, service, or library SDK templates based on `projectType` from the registry metadata.
3. **Invoke the SDK Builder Skill** — once per target language (TypeScript, Python, C#).
4. **Invoke the SDK Consumer Skill** — to generate consumption boilerplate for each target language.
5. **Emit a build report** — a structured summary of all artifacts produced, written to `sdk/BUILD_REPORT.md`.
6. **Update `agents.md`** — append or update the ADIK integration block in the repository root `agents.md`.

---

## Inputs

| Input | Source | Required |
|---|---|---|
| `Registry.md` | Repository root | Yes |
| `adik.config.json` | Repository root | No (defaults apply) |
| `projectType` | Registry metadata | Yes |
| `sdkLanguages` | Config or Registry metadata | Yes |
| `outputDir` | Config | No (default: `./sdk`) |

---

## Outputs

| Output | Path | Description |
|---|---|---|
| TypeScript SDK | `sdk/typescript/` | Full TS package with types, client, and helpers |
| Python SDK | `sdk/python/` | Python package with dataclasses, client, and helpers |
| C# SDK | `sdk/csharp/` | .NET package with models, client, and helpers |
| Build report | `sdk/BUILD_REPORT.md` | Summary of all generated artifacts |
| Updated `agents.md` | `agents.md` (repo root) | ADIK integration block |

---

## Execution Protocol

```
1. LOAD Registry.md
   ├─ ASSERT metadata.projectType is set
   ├─ ASSERT metadata.lastAnalysedCommit is set
   └─ ASSERT at least one section (Endpoints, Classes, or Functions) is non-empty

2. FOR EACH language IN config.sdkLanguages:
   ├─ INVOKE sdk-builder.skill
   │    inputs: { registry, language, projectType, outputDir }
   │    outputs: sdk/<language>/
   │
   └─ INVOKE sdk-consumer.skill
        inputs: { registry, language, projectType, outputDir }
        outputs: sdk/<language>/examples/, sdk/<language>/boilerplate/

3. WRITE sdk/BUILD_REPORT.md
   ├─ timestamp
   ├─ registry commit SHA
   ├─ list of generated files per language
   └─ any warnings or skipped symbols

4. UPSERT agents.md with ADIK integration block
```

---

## Error Handling

| Condition | Action |
|---|---|
| Registry is empty or missing | Abort and prompt user to run `codebase-analyst` first |
| `projectType` is `auto` | Defer to Codebase Analyst Agent before proceeding |
| A skill invocation fails | Log error to `BUILD_REPORT.md`, continue with remaining languages |
| Output directory already exists | Merge strategy: overwrite generated files, preserve manually created files |

---

## Incremental Build Mode

When `syncOnCommit: true` is set in `adik.config.json`, the Builder Agent operates in incremental mode:

1. Compare the current `Registry.md` with the version at `lastAnalysedCommit`.
2. Identify added, modified, and deprecated symbols.
3. Regenerate only the SDK files that correspond to changed symbols.
4. Append incremental change notes to `sdk/BUILD_REPORT.md`.

---

## Invocation Examples

### Full build

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

### Single-language build

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript]
```

### Incremental sync after new commit

```
@agent builder
task: sync-sdk
registry: Registry.md
since: <previous-commit-sha>
languages: [typescript, python, csharp]
```

---

## Related Files

| File | Role |
|---|---|
| `ADIK.md` | Parent orchestrator |
| `Registry.md` | Symbol registry consumed by this agent |
| `agents/codebase-analyst.agent.md` | Upstream agent that populates the registry |
| `skills/sdk-builder.skill.md` | Delegate skill for SDK code generation |
| `skills/sdk-consumer.skill.md` | Delegate skill for consumption boilerplate |
| `mcp/adik-mcp-server.md` | MCP server that can trigger this agent remotely |
