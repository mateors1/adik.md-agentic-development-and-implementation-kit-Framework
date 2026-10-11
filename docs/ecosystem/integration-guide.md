# Using ADIK with GitHub Spec Kit — Integration Guide

> **Part of:** [ADIK — Agentic Development and Implementation Kit](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/README.md)
> **See also:** [Full Analysis & Comparison](spec-kit.md), [`spec-kit-adik` Extension](spec-kit-adik/README.md)

This guide walks you through setting up ADIK in a [GitHub Spec Kit](https://github.com/github/spec-kit)
project so that after `/speckit.implement` produces working code, ADIK automatically generates
publish-ready SDK packages and framework-idiomatic integration boilerplate.

---

## The Big Picture

Spec Kit drives the lifecycle from **idea → spec → code**. ADIK picks up from **code → registry → SDK**.

```
Spec Kit                                   ADIK
────────                                   ────
/speckit.constitution                      
/speckit.specify                           
/speckit.plan   → api-spec.json            
/speckit.tasks                             
/speckit.implement → source code ──────────┐
                                           ▼
                                  Codebase Analyst → Registry.md
                                           │
                                  Registry Validator (3-level gate)
                                           │
                                  Builder Agent → sdk/typescript/
                                                  sdk/python/
                                                  sdk/csharp/
                                           │
                                  SDK Consumer → DI wiring, examples,
                                                 retry wrappers
                                           │
                                  Self-embed → AI tools aware of SDK
```

Together: **spec → code → registry → SDK → maintained SDK**.

---

## Prerequisites

- A Spec Kit project (`specify init <project> --ai <agent>`)
- Python 3.11+
- ADIK source repo cloned (for deployment)

---

## Step 1 — Deploy ADIK into Your Project

From the ADIK source repository:

```bash
python3 scripts/adik-deploy.py --target /path/to/your/speckit-project/
```

This copies the adik bundle (`ADIK.orchestrator.md`, `agents/`, `skills/`, `scripts/`, `mcp/`,
`Registry.md`, `Registry.index.md`) into your project.

---

## Step 2 — Configure ADIK for Spec Kit

Create `adik.config.json` in your project root:

```json
{
  "includePatterns": [
    "src/**/*",
    ".specify/specs/*/contracts/api-spec.json"
  ],
  "sdkLanguages": ["typescript", "python", "csharp"],
  "outputDir": "./sdk"
}
```

The key line is adding `.specify/specs/*/contracts/api-spec.json` to `includePatterns` — this tells
the Codebase Analyst to read Spec Kit's per-feature API contracts as first-class OpenAPI sources.

### Optional: Feature-Branch Registry Partitions

If your Spec Kit project has multiple features, align Registry partitions to feature names:

```json
{
  "includePatterns": [
    "src/**/*",
    ".specify/specs/*/contracts/api-spec.json"
  ],
  "partitionStrategy": "manual",
  "partitionMappings": {
    "create-taskify": ".specify/specs/001-create-taskify/**/*",
    "user-profiles": ".specify/specs/002-user-profiles/**/*"
  }
}
```

---

## Step 3 — Run the Standard Spec Kit Workflow

```
/speckit.constitution   Create principles focused on ...
/speckit.specify        Build an application that ...
/speckit.clarify
/speckit.plan           Use Vite with vanilla JS, SQLite ...
/speckit.tasks
/speckit.implement
```

After `/speckit.implement` completes, you have working source code and
`.specify/specs/<feature>/contracts/api-spec.json`.

---

## Step 4 — Run the ADIK Pipeline

### Option A: Using `/speckit.adik.*` Commands (with extension installed)

```
/speckit.adik.registry      ← scans source + api-spec.json → Registry.md
/speckit.adik.sdk            ← validates → generates sdk/typescript/, sdk/python/, sdk/csharp/
/speckit.adik.boilerplate    ← detects framework → generates DI wiring, examples, retry logic
/speckit.adik.status         ← reports sync status
```

### Option B: Using ADIK Directly (without extension)

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
output: Registry.md
```

Then:

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

---

## Step 5 — Spec Traceability

ADIK uses the Registry's `tags` field to link symbols back to Spec Kit features. When the Codebase
Analyst scans `.specify/specs/001-create-taskify/contracts/api-spec.json`, it tags those symbols:

```yaml
- id: create-taskify.tasks.list
  kind: Endpoint
  name: listTasks
  tags: ["spec:001-create-taskify"]
```

This provides traceability from SDK method → Registry symbol → Spec Kit feature spec → original
user story.

---

## Step 6 — Ongoing Maintenance

Once the adik is deployed, SDKs stay in sync automatically:

- **On every commit** (if `syncOnCommit: true`): the Codebase Analyst re-scans, the Registry
  updates, and the Builder regenerates only the changed symbols
- **On new features**: run `/speckit.implement` then `/speckit.adik.registry` → `/speckit.adik.sdk`
- **At any time**: run `/speckit.adik.status` to check whether SDKs are current

---

## Frequently Asked Questions

**Q: Do I need to install ADIK to use Spec Kit?**
No. Spec Kit works perfectly on its own. ADIK is an optional post-implementation extension.

**Q: Does ADIK modify my source code?**
Never. ADIK only generates SDK packages in `./sdk/`, updates `Registry.md`, writes `adik.audit.log`,
and updates AI context files using guard markers.

**Q: Can I eject ADIK later?**
Yes. Run `python3 scripts/adik-eject.py --target . --confirm`. All ADIK artifacts are removed.
Source code and Spec Kit artifacts are untouched.

**Q: Do the context file guard markers conflict with Spec Kit?**
No. ADIK uses `<!-- ADIK:START -->` / `<!-- ADIK:END -->` markers. Spec Kit does not use ADIK-format
guard blocks. Both write to `.github/copilot-instructions.md` and `CLAUDE.md` without conflicting.

---

## Related

| Resource | Link |
|---|---|
| Full Spec Kit analysis | [docs/ecosystem/spec-kit.md](spec-kit.md) |
| `spec-kit-adik` extension | [docs/ecosystem/spec-kit-adik/](spec-kit-adik/README.md) |
| ADIK Configuration Reference | [docs/getting-started/configuration.md](../getting-started/configuration.md) |
| ADIK Quickstart Guide | [docs/getting-started/quickstart-guide.md](../getting-started/quickstart-guide.md) |
| GitHub Spec Kit | [github.com/github/spec-kit](https://github.com/github/spec-kit) |
