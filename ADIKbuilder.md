# ADIKbuilder.md — Agentic Development and Implementation Kit Builder

> **Version:** 1.0.0
> **Role:** adik Factory — Source-Repo Orchestrator
> **Scope:** This file lives exclusively in the `adik.md-agentic-development-and-implementation-kit` source repository. It is the **factory** that produces specialized adiks — self-sustaining agentic SDK bundles tailored to each target project. It is **not** part of any deployed adik.

---

## Purpose

ADIKbuilder.md is the **factory orchestrator** of the ADIK framework. Its primary job is to produce specialized **adiks** — complete, self-sustaining agentic SDK bundles that are deployed into target repositories.

> **Terminology:** An **adik** (lowercase) is the deliverable — a specialized bundle containing a tailored orchestrator (`ADIK.orchestrator.md`), standard definition (`ADIK.md`), project-tuned agents and skills, a symbol registry, generated SDK packages, and the agentic infrastructure to maintain them. "ADIK" (uppercase) refers to the framework standard itself.

ADIKbuilder.md is responsible for:

1. **Generating specialized adiks** — assembling and tailoring the orchestrator, agents, skills, registry templates, and scripts into a project-specific bundle that, once deployed, can analyze the target codebase, generate SDKs, produce implementation boilerplate, and self-embed into the project's AI tools.
2. **Governing the ADIK framework** — maintaining all agent definitions, skill templates, registry format, and MCP server specification.
3. **Validating internal consistency** — ensuring that agent, skill, and orchestrator files reference each other correctly and that no cross-file contracts are broken.
4. **Evolving the Registry format** — when the canonical schema changes, propagating updates across all agent and skill definitions.
5. **Tracking framework versions** — maintaining a changelog of ADIK framework releases.

---

## What Is an adik?

An **adik** is a self-sustaining agentic SDK — the complete deliverable produced by this factory. It includes:

| Component | Role |
|---|---|
| `ADIK.md` | Standard definition — what ADIK is, terminology, and contracts |
| `ADIK.orchestrator.md` | Operational orchestrator — tailored to the target project on first run |
| `agents/` | Codebase Analyst + Builder agents — analyze the project and generate SDKs |
| `skills/` | SDK Builder, Consumer, Validator, Vectorize — the skills that do the work |
| `Registry.md` | Language-agnostic symbol registry — populated from the target codebase |
| `sdk/` | Generated SDK packages — the publish-ready output in up to 6 languages |
| `scripts/` | Self-embedding (`adik-embed.py`) + clean eject (`adik-eject.py`) |
| `mcp/` | MCP server — exposes the pipeline to any agentic environment |

When an adik is deployed to a target repository, it **carries its own maintenance pipeline**. The project doesn't just receive SDK packages — it receives the agents and skills that produced them, so the SDKs can be regenerated, validated, and kept in sync automatically on every commit.

This is what distinguishes an adik from a traditional generated SDK: it is **self-sustaining**.

---

## Relationship to ADIK.md and ADIK.orchestrator.md

| File | Scope | Deployed? |
|---|---|---|
| `ADIKbuilder.md` | This source repository only — the factory | No |
| `ADIK.md` | Deployed as part of every adik — the standard definition | Yes |
| `ADIK.orchestrator.md` | Deployed as part of every adik — the operational orchestrator | Yes |

`ADIKbuilder.md` is the **factory** — it produces adiks. `ADIK.md` is the **standard definition** — it defines what ADIK is, its terminology, and contracts. `ADIK.orchestrator.md` is the **orchestrator inside each adik** — it drives analysis, generation, and implementation within a target codebase. On first run, `ADIK.orchestrator.md` tailors itself to the target project (auto-filling project metadata, detecting frameworks, configuring languages).

---

## The adik Bundle

ADIKbuilder assembles the following files into each adik. On deployment to a target repository, `ADIK.orchestrator.md` specializes itself on first run:

```
adik-bundle/
├── ADIK.md                          ← Standard definition
├── ADIK.orchestrator.md             ← Orchestrator (specializes on first run)
├── Registry.md                      ← DRY symbol registry template (monolithic)
├── Registry.index.md                ← Partitioned registry master index template
├── agents/
│   ├── builder.agent.md
│   └── codebase-analyst.agent.md
├── skills/
│   ├── sdk-builder.skill.md
│   ├── sdk-builder-tier2.skill.md   ← Tier-2 SDK skill (Go, Java, Kotlin — opt-in)
│   ├── sdk-consumer.skill.md
│   ├── registry-validator.skill.md  ← Registry schema validation skill
│   └── vectorize.skill.md           ← Vector embedding subskill (loaded on demand)
├── scripts/
│   ├── adik-embed.py                ← Deterministic self-embedding script
│   └── adik-eject.py                ← Clean uninstall / eject script
└── mcp/
    └── adik-mcp-server.md
```

`ADIKbuilder.md`, `docs/`, `CLAUDE.md`, `agents.md`, and `.github/` are **never** included in the adik. `ADIK.orchestrator.md` handles self-embedding into the target project's `CLAUDE.md`, `agents.md`, and `.github/copilot-instructions.md` during its first run.

---

## Source Repository Self-Embedding

`ADIKbuilder.md`, `ADIK.md`, and `ADIK.orchestrator.md` must be reflected in the source repository's own agentic context files. When any of these files is modified, verify that the following files in this source repository remain current:

| File | Purpose |
|---|---|
| `.github/copilot-instructions.md` | GitHub Copilot context for this source repository |
| `CLAUDE.md` | Claude session context for this source repository |
| `agents.md` | Agent and skill registry for agentic sessions in this source repository |

These files must reference `ADIKbuilder.md`, `ADIK.md`, and `ADIK.orchestrator.md` so that any AI assistant working in the source repository understands the factory/standard/orchestrator model and the deployable bundle boundaries.

**Verification checklist (run after any change to `ADIK.md`, `ADIK.orchestrator.md`, or `ADIKbuilder.md`):**

- [ ] `.github/copilot-instructions.md` mentions `ADIK.md`, `ADIK.orchestrator.md`, and `ADIKbuilder.md` and their respective roles.
- [ ] `CLAUDE.md` contains an up-to-date executive summary and the correct file layout.
- [ ] `agents.md` lists all current agents, skills, and the MCP server accurately.
- [ ] `docs/specification/manifesto.md` reflects the current principles.
- [ ] `docs/examples/ADIKBuilderExample.md` is in sync with framework contract changes.

---

## Deploy Workflow

The factory's primary output is the adik bundle. Deployment is handled by `scripts/adik-deploy.py` — a deterministic script that validates, assembles, and copies the bundle to a target.

### Quick Deploy

```bash
# Deploy to a target repo (validates source, copies bundle, runs self-embedding)
python3 scripts/adik-deploy.py --source . --target /path/to/target-repo --embed

# Dry-run first to see what would be deployed
python3 scripts/adik-deploy.py --source . --target /path/to/target-repo --dry-run

# Force overwrite if target already has an adik
python3 scripts/adik-deploy.py --source . --target /path/to/target-repo --embed --force
```

### Deploy to a Distribution Repo

```bash
# Deploy as a clean distribution bundle (factory-only files excluded)
python3 scripts/adik-deploy.py --source . --target /path/to/dist-repo --dist
```

### What the Deploy Script Does

1. **Validates** — confirms all required files and directories exist in the source repo.
2. **Checks conflicts** — warns if the target already contains adik files.
3. **Copies** — deploys only bundle files: `ADIK.md`, `ADIK.orchestrator.md`, `Registry.md`, `Registry.index.md`, `agents/`, `skills/`, `scripts/` (minus `adik-deploy.py`), `mcp/`.
4. **Never copies** — `ADIKbuilder.md`, `docs/`, `CLAUDE.md`, `agents.md`, `.github/`, `README.md`, `CHANGELOG.md`.
5. **Optionally embeds** — runs `adik-embed.py --action upsert` in the target to set up context files.

### CI/CD Deploy

```yaml
env:
  ADIK_DEPLOY_EMBED: 'true'
  ADIK_DEPLOY_FORCE: 'true'

steps:
  - run: python3 scripts/adik-deploy.py --source . --target ${{ env.TARGET_REPO }}
```

---

## Framework Evolution Workflow

### Adding a New Agent or Skill

1. Create the new `.agent.md` or `.skill.md` file in `agents/` or `skills/`.
2. Reference it from `ADIK.orchestrator.md` (the operational orchestrator) in both the orchestration workflow diagram and the Related Files table.
3. Update `README.md` to document the new capability.
4. Bump the patch version in this file and in `ADIK.md` / `ADIK.orchestrator.md`.

### Changing the Registry Schema

1. Update the Symbol Entry Schema in `Registry.md`.
2. Update all agent and skill files that read from or write to the Registry.
3. Update the `ADIK.orchestrator.md` orchestration workflow if the change affects step ordering.
4. Bump the minor version in this file and in `ADIK.md` / `ADIK.orchestrator.md`.

### Releasing a New adik Version

1. Increment the version in this file and in `ADIK.md` / `ADIK.orchestrator.md`.
2. Tag the release in git (`vX.Y.Z`).
3. Update `README.md` with the release notes.
4. Deploy the adik bundle using the deploy script:

```bash
# Deploy to a target repository
python3 scripts/adik-deploy.py --source . --target /path/to/target-repo --embed

# Or dry-run first to verify
python3 scripts/adik-deploy.py --source . --target /path/to/target-repo --dry-run
```

5. Ensure the adik bundle does not include `ADIKbuilder.md`.
6. **Prompt the user:** *"Would you like to create a separate GitHub repository within the same organization to distribute this adik internally? (Recommended for teams sharing ADIK across multiple internal projects.)"*
   - If **yes**: follow the [Internal Distribution Repository](#internal-distribution-repository) workflow below.
   - If **no**: distribution is complete — the adik is available via this repository's tags.

---

## Internal Distribution Repository

When the user chooses to create a dedicated distribution repository, execute the following steps:

### 1. Confirm Organisation and Repository Name

Prompt the user for:

| Field | Default | Notes |
|---|---|---|
| GitHub organisation | *(current repo owner)* | The org under which the new repo will be created |
| Repository name | `adik-bundle` | Should be descriptive; e.g. `adik-dist`, `adik-internal`, `adik-bundle` |
| Visibility | `internal` | `internal` is recommended for inner-source distribution; `private` is also acceptable |
| Description | `Internal adik distribution` | Short description shown on the GitHub repo page |

### 2. Create the Repository

```bash
gh repo create <org>/<repo-name> \
  --description "<description>" \
  --internal \
  --confirm
```

> **Note:** Replace `--internal` with `--private` if the organisation does not have GitHub Enterprise (which is required for `internal` visibility). Requires the GitHub CLI (`gh`) with `repo:write` scope in the target organisation. If `gh` is unavailable, instruct the user to create the repository manually on GitHub and then clone it.

### 3. Initialise and Push the Bundle

```bash
# Clone the new empty repo
git clone https://github.com/<org>/<repo-name>.git adik-dist-repo

# Deploy the adik bundle using the deploy script
python3 scripts/adik-deploy.py --source . --target adik-dist-repo --dist

# Enter the dist repo, commit, and tag
cd adik-dist-repo

# Commit and tag
git add .
git commit -m "chore: initialise ADIK bundle vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

### 4. Document the Distribution Repository

Add a **Distribution** section to this source repository's `README.md` pointing consumers to the adik distribution repo:

```markdown
## Internal Distribution

The deployable adik is published to:
**https://github.com/<org>/<repo-name>**

Each release is tagged `vX.Y.Z`. To deploy the adik into a new repository:

    git clone https://github.com/<org>/<repo-name>.git adik-bundle --branch vX.Y.Z --depth 1
    cp -r adik-bundle/* /path/to/your/target-repo/
```

### 5. Verify the Distribution Repository

- [ ] Confirm the new repo is visible to the intended teams/members within the organisation.
- [ ] Confirm `ADIKbuilder.md` and `ADIKBuilderExample.md` are **not** present in the distribution repo.
- [ ] Confirm `CLAUDE.md`, `agents.md`, and `.github/copilot-instructions.md` are **not** in the distribution repo.
- [ ] Confirm `Registry.index.md` and `scripts/` **are** present in the distribution repo.
- [ ] Confirm the `vX.Y.Z` tag resolves to the correct commit.
- [ ] Share the repository URL with relevant teams.

---

## File Layout (Source Repository)

```
adik.md-agentic-development-and-implementation-kit/
├── ADIKbuilder.md                   ← this file (source-repo orchestrator, not deployed)
├── ADIK.md                          ← standard definition (deployed to target repos)
├── ADIK.orchestrator.md             ← operational orchestrator (deployed to target repos)
├── Registry.md                      ← DRY symbol registry template
├── Registry.index.md                ← Partitioned registry master index template
├── README.md                        ← manifesto + dual-audience guide
├── CLAUDE.md                        ← Claude session context (source repo only)
├── agents.md                        ← agent/skill registry for agentic sessions (source repo only)
├── .github/
│   ├── copilot-instructions.md      ← GitHub Copilot context (source repo only)
│   └── workflows/
│       ├── adik-self-deploy.yml     ← CI/CD self-deployment workflow (source repo)
│       └── adik-ci.yml              ← optional integration testing workflow (source repo)
├── docs/
│   ├── index.md                     ← Documentation site home
│   ├── getting-started/
│   │   ├── quickstart-guide.md      ← 15-minute first-run walkthrough
│   │   ├── pre-deployment.md        ← Bundle walkthrough before first run
│   │   └── configuration.md         ← adik.config.json reference
│   ├── specification/
│   │   ├── standard.md              ← ADIK Standard Specification
│   │   ├── architecture.md          ← System architecture with Mermaid diagrams
│   │   └── manifesto.md             ← ADIK philosophy and principles
│   ├── examples/
│   │   └── ADIKBuilderExample.md    ← self-sufficient guide for building your own ADIK (not deployed)
│   ├── security/
│   │   └── red-team-audit-v2.md     ← Post-v2.0 security audit
│   └── community/
│       └── launch-posts.md          ← Social media launch content
├── agents/
│   ├── builder.agent.md
│   └── codebase-analyst.agent.md
├── scripts/
│   ├── adik-embed.py                ← deterministic self-embedding script
│   ├── adik-eject.py                ← clean uninstall / eject script
│   └── adik-deploy.py               ← bundle assembly and deployment (factory-side only)
├── skills/
│   ├── sdk-builder.skill.md
│   ├── sdk-builder-tier2.skill.md   ← tier-2 SDK skill (Go, Java, Kotlin — opt-in)
│   ├── sdk-consumer.skill.md
│   ├── registry-validator.skill.md  ← registry schema validation skill
│   └── vectorize.skill.md           ← vector embedding subskill
└── mcp/
    └── adik-mcp-server.md
```

---

## Constraints and Principles

- **ADIKbuilder.md is never deployed.** It lives only in this source repository as the factory and must not be included in any adik distributed to target repositories.
- **ADIKBuilderExample.md is never deployed.** It is a guide for developers who want to build their own ADIK; it is not part of the operational framework.
- **Source-only context files are never deployed.** `CLAUDE.md`, `agents.md`, `.github/copilot-instructions.md`, and `docs/` are source repository files; they are not part of any adik. `ADIK.md` creates equivalent files in target repositories during its first run.
- **An adik is self-sustaining.** The deployed bundle must contain everything needed to analyze the target codebase, generate SDKs, produce implementation boilerplate, and maintain itself — without depending on this source repository.
- **ADIK.md is the standard.** It defines what ADIK is, its terminology, and contracts.
- **ADIK.orchestrator.md is the operational contract.** When `ADIK.orchestrator.md` changes in a backward-incompatible way, consumers must be notified via a version bump.
- **Every agent and skill file must be independently readable.** Each file must be fully actionable by an LLM agent without loading the entire repository.
- **The Registry format is stable.** Breaking changes to the registry schema require a major version bump.
- **Vectorization stays in the subskill.** `skills/vectorize.skill.md` is the only file that may contain embedding or vector-store logic.
- **Self-embedding is deterministic.** `scripts/adik-embed.py` is the only mechanism for writing ADIK guard blocks. LLM agents must not edit context files directly.
- **Tier-2 languages are opt-in.** `skills/sdk-builder-tier2.skill.md` is only invoked when explicitly listed in `tier2Languages`. It must never be auto-activated.
- **Registry validation is mandatory.** `skills/registry-validator.skill.md` must be invoked before every SDK generation. No exceptions.
- **Self-embedding is bidirectional.** `ADIK.orchestrator.md` embeds itself into target projects; `ADIKbuilder.md` maintains the source repository's own context files (`CLAUDE.md`, `agents.md`, `.github/copilot-instructions.md`).

---

## Related Files

| File | Role |
|---|---|
| `ADIK.md` | Standard definition — what ADIK is, terminology, and contracts |
| `ADIK.orchestrator.md` | Operational orchestrator — the brain inside every deployed adik |
| `docs/examples/ADIKBuilderExample.md` | Step-by-step guide for building a custom ADIK implementation |
| `docs/security/red-team-audit-v2.md` | Post-v2.0 red-team security and improvement audit |
| `Registry.md` | Symbol registry template (monolithic) |
| `Registry.index.md` | Partitioned registry master index template |
| `README.md` | Manifesto + dual-audience guide |
| `CLAUDE.md` | Claude session context for this source repository |
| `agents.md` | Agent and skill registry for agentic sessions in this source repository |
| `.github/copilot-instructions.md` | GitHub Copilot context for this source repository |
| `.github/workflows/adik-self-deploy.yml` | CI/CD workflow for self-deploying the bundle as `<reponame>-ADIK` |
| `.github/workflows/adik-ci.yml` | Optional integration testing workflow (registry validation + type-checking) |
| `docs/specification/manifesto.md` | ADIK philosophy and principles |
| `agents/builder.agent.md` | SDK builder agent |
| `agents/codebase-analyst.agent.md` | Codebase analysis + frameworkHints inference + dev-state check |
| `skills/sdk-builder.skill.md` | Tier-1 SDK code-generation skill (TypeScript, Python, C#) |
| `skills/sdk-builder-tier2.skill.md` | Tier-2 SDK skill (Go, Java, Kotlin — opt-in) |
| `skills/sdk-consumer.skill.md` | Consumption boilerplate skill |
| `skills/registry-validator.skill.md` | Registry schema validation skill |
| `skills/vectorize.skill.md` | Vector embedding subskill |
| `scripts/adik-embed.py` | Deterministic self-embedding script |
| `scripts/adik-eject.py` | Clean uninstall / eject script |
| `scripts/adik-deploy.py` | Bundle assembly and deployment script (factory-side only, not deployed) |
| `mcp/adik-mcp-server.md` | MCP server definition |
