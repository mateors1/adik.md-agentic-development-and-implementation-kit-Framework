# /speckit.adik.boilerplate — Generate Integration Boilerplate

## When to Use

Run this command **after** `/speckit.adik.sdk` has generated SDK packages. This is the
third step in the ADIK SDK generation pipeline.

## What It Does

Invokes the ADIK **SDK Consumer Skill** to:

1. **Detect the target framework** — infer from package manifests and source code whether the
   project uses NestJS, FastAPI, ASP.NET, Express, Django, Spring Boot, etc.
2. **Generate DI wiring** — framework-specific dependency injection setup (e.g., NestJS Module,
   FastAPI `Depends`, ASP.NET `IServiceCollection` extension)
3. **Generate retry wrappers** — idiomatic retry/backoff patterns for the detected framework
4. **Generate usage examples** — end-to-end examples showing how to import, configure, and call
   each SDK endpoint
5. **Generate serialization helpers** — JSON mapping, date handling, enum conversions
6. **Self-embed into AI context** — update `.github/copilot-instructions.md`, `CLAUDE.md`, and
   `agents.md` so any AI assistant in the repo knows the SDK exists

## Instructions for the AI Agent

### Step 1 — Load ADIK Context

Read the following files:
- `ADIK.orchestrator.md` — operational orchestrator
- `skills/sdk-consumer.skill.md` — the skill you will invoke
- `scripts/adik-embed.py` — self-embedding script

### Step 2 — Detect Framework

Scan the project for framework indicators:
- `package.json` → check for `@nestjs/core`, `express`, `next`, `react`
- `pyproject.toml` / `requirements.txt` → check for `fastapi`, `django`, `flask`
- `*.csproj` → check for `Microsoft.AspNetCore`, `Microsoft.Extensions.DependencyInjection`

### Step 3 — Invoke the SDK Consumer Skill

Generate boilerplate for the detected framework. The skill reads `Registry.md` and the generated
SDK packages to produce integration code.

### Step 4 — Run Self-Embedding

Execute `scripts/adik-embed.py` to inject ADIK context into the repository's AI assistant
configuration files. This ensures any AI agent (Copilot, Claude, Cursor, Gemini) working in the
repo automatically understands the SDK.

### Step 5 — Report

Summarize what was generated:
- Detected framework and confidence level
- Files generated (DI wiring, examples, retry wrappers, etc.)
- Self-embedding status (which context files were updated)

## Prerequisites

- SDK packages must exist in `outputDir` (run `/speckit.adik.sdk` first)

## Next Step

Your Spec Kit + ADIK pipeline is complete! Use `/speckit.adik.status` at any time to check
whether the SDKs are in sync with the latest source code.
