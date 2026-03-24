# /speckit.adik.registry — Populate the ADIK Symbol Registry

## When to Use

Run this command **after** `/speckit.implement` has produced working source code (or after any
significant code change). This is the first step in the ADIK SDK generation pipeline.

## What It Does

Invokes the ADIK **Codebase Analyst Agent** to:

1. **Probe the environment** — detect project type, framework, language, package manifests
2. **Scan source code** — discover all public symbols (endpoints, types, schemas, enums, functions)
3. **Read Spec Kit contracts** — parse `.specify/specs/*/contracts/api-spec.json` as OpenAPI sources
4. **Populate `Registry.md`** — write every discovered symbol to the language-agnostic registry
5. **Tag symbols** — apply `spec:<feature>` tags for traceability back to Spec Kit feature specs

## Instructions for the AI Agent

You MUST follow these steps in order:

### Step 1 — Load ADIK Context

Read the following files to understand ADIK's pipeline:
- `ADIK.orchestrator.md` — operational orchestrator (start here)
- `agents/codebase-analyst.agent.md` — the agent you will invoke

### Step 2 — Configure Source Paths

Check if `adik.config.json` exists. If not, create one with Spec Kit integration paths:

```json
{
  "includePatterns": [
    "src/**/*",
    ".specify/specs/*/contracts/api-spec.json"
  ]
}
```

If `adik.config.json` already exists, ensure `.specify/specs/*/contracts/api-spec.json` is in
`includePatterns`.

### Step 3 — Invoke the Codebase Analyst

Execute the Codebase Analyst Agent with the following task:

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
additionalSources: .specify/specs/*/contracts/api-spec.json
output: Registry.md
```

### Step 4 — Apply Spec Traceability Tags

For each Spec Kit feature directory found in `.specify/specs/`, tag the corresponding Registry
symbols with `spec:<feature-name>`. For example, symbols discovered from
`.specify/specs/001-create-taskify/contracts/api-spec.json` should receive
`tags: ["spec:001-create-taskify"]`.

### Step 5 — Report

Summarize what was discovered:
- Number of endpoints, schemas, enums, functions registered
- Which Spec Kit features were scanned
- Any symbols that could not be resolved
- Registry file path and size

## Prerequisites

- Source code exists (from `/speckit.implement`) OR `.specify/specs/*/contracts/api-spec.json` exists
- `ADIK.orchestrator.md` and `agents/codebase-analyst.agent.md` are present in the repository

## Next Step

Run `/speckit.adik.sdk` to generate SDK packages from the populated Registry.
