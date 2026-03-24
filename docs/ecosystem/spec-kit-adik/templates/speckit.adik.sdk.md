# /speckit.adik.sdk — Generate SDK Packages

## When to Use

Run this command **after** `/speckit.adik.registry` has populated `Registry.md`. This is the
second step in the ADIK SDK generation pipeline.

## What It Does

Invokes the ADIK **Builder Agent** to:

1. **Validate the Registry** — run the three-level validation gate (Structural, Type, Semantic)
2. **Generate SDK packages** — produce complete, publish-ready packages for all configured languages
3. **Type-check the output** — run `tsc`, `mypy`, `dotnet build` (and `go build` for tier-2) on generated code
4. **Write the audit log** — append a structured NDJSON entry to `adik.audit.log`

## Instructions for the AI Agent

### Step 1 — Load ADIK Context

Read the following files:
- `ADIK.orchestrator.md` — operational orchestrator
- `agents/builder.agent.md` — the agent you will invoke
- `skills/registry-validator.skill.md` — validation rules
- `skills/sdk-builder.skill.md` — tier-1 generation rules

### Step 2 — Check Configuration

Read `adik.config.json` (if present) for:
- `sdkLanguages` — which tier-1 languages to generate (default: TypeScript, Python, C#)
- `tier2Languages` — which tier-2 languages to generate (default: none)
- `outputDir` — where to write packages (default: `./sdk`)

### Step 3 — Invoke the Builder Agent

Execute the Builder Agent:

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

If `tier2Languages` are configured, they will be included automatically.

### Step 4 — Report

Summarize the generation results:
- Languages generated and output paths
- Number of models, clients, and types per language
- Validation gate result (PASS / FAIL with specific rule violations)
- Type-check results (pass/fail per language)
- Audit log entry reference

## Prerequisites

- `Registry.md` must be populated (run `/speckit.adik.registry` first)
- Registry Validator must PASS — if it fails, report the violations and do NOT generate

## Next Step

Run `/speckit.adik.boilerplate` to generate framework-idiomatic integration code.
