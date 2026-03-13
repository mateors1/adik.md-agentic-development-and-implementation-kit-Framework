# ADIKbuilder.md — Agentic Development and Implementation Kit Builder

> **Version:** 1.1.0
> **Role:** Source-Repo Orchestrator
> **Scope:** This file lives exclusively in the `adik.md-agentic-development-and-implementation-kit` source repository and governs the development, validation, and release of the ADIK framework itself. It is **not** part of the deployable bundle.

---

## Purpose

ADIKbuilder.md is the root orchestrator of this source repository. It manages the authoring, validation, and release of all ADIK artefacts that are subsequently deployed into consumer repositories.

ADIKbuilder.md is responsible for:

1. **Governing the ADIK framework** — maintaining all agent definitions, skill templates, registry format, and MCP server specification.
2. **Validating internal consistency** — ensuring that agent, skill, and orchestrator files reference each other correctly and that no cross-file contracts are broken.
3. **Preparing the deployable bundle** — assembling the files that are copied into a target repository.
4. **Evolving the Registry format** — when the canonical schema changes, propagating updates across all agent and skill definitions.
5. **Tracking framework versions** — maintaining a changelog of ADIK framework releases.

---

## Relationship to ADIK.md

| File | Scope | Deployed? |
|---|---|---|
| `ADIKbuilder.md` | This source repository only | No |
| `ADIK.md` | Copied into every target repository | Yes |

`ADIK.md` is the **implementation orchestrator** — the file that drives SDK generation inside a target codebase. `ADIKbuilder.md` is the **framework orchestrator** — the file that governs how ADIK itself is built, tested, and released.

---

## Deployable Bundle

The following files are assembled into the ADIK bundle and copied into target repositories:

```
adik-bundle/
├── ADIK.md                          ← Implementation orchestrator
├── Registry.md                      ← DRY symbol registry template
├── agents/
│   ├── builder.agent.md
│   └── codebase-analyst.agent.md
├── skills/
│   ├── sdk-builder.skill.md
│   ├── sdk-consumer.skill.md
│   └── vectorize.skill.md           ← Vector embedding subskill (loaded on demand)
└── mcp/
    └── adik-mcp-server.md
```

`ADIKbuilder.md` and `ADIKBuilderExample.md` are **never** included in the bundle.

---

## Framework Evolution Workflow

### Adding a New Agent or Skill

1. Create the new `.agent.md` or `.skill.md` file in `agents/` or `skills/`.
2. Reference it from `ADIK.md` (the implementation orchestrator) in both the orchestration workflow diagram and the Related Files table.
3. Update `README.md` to document the new capability.
4. Bump the patch version in this file and in `ADIK.md`.

### Changing the Registry Schema

1. Update the Symbol Entry Schema in `Registry.md`.
2. Update all agent and skill files that read from or write to the Registry.
3. Update the `ADIK.md` orchestration workflow if the change affects step ordering.
4. Bump the minor version in this file and in `ADIK.md`.

### Releasing a New Bundle Version

1. Increment the version in this file and in `ADIK.md`.
2. Tag the release in git (`vX.Y.Z`).
3. Update `README.md` with the release notes.
4. Ensure the bundle does not include `ADIKbuilder.md`.
5. **Prompt the user:** *"Would you like to create a separate GitHub repository within the same organization to distribute this bundle internally? (Recommended for teams sharing ADIK across multiple internal projects.)"*
   - If **yes**: follow the [Internal Distribution Repository](#internal-distribution-repository) workflow below.
   - If **no**: distribution is complete — the bundle is available via this repository's tags.

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
| Description | `Internal ADIK bundle distribution` | Short description shown on the GitHub repo page |

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
cd adik-dist-repo

# Copy only the deployable bundle files (never ADIKbuilder.md or ADIKBuilderExample.md)
cp -r ../ADIK.md ../Registry.md ../agents ../skills ../mcp .

# (Optional) copy adik.config.json if a canonical default is provided
# cp ../adik.config.json .

# Commit and tag
git add .
git commit -m "chore: initialise ADIK bundle vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

### 4. Document the Distribution Repository

Add a **Distribution** section to this source repository's `README.md` pointing consumers to the new repo:

```markdown
## Internal Distribution

The deployable ADIK bundle is published to:
**https://github.com/<org>/<repo-name>**

Each release is tagged `vX.Y.Z`. To add ADIK to a new repository:

    git clone https://github.com/<org>/<repo-name>.git adik-bundle --branch vX.Y.Z --depth 1
    cp -r adik-bundle/* /path/to/your/target-repo/
```

### 5. Verify the Distribution Repository

- [ ] Confirm the new repo is visible to the intended teams/members within the organisation.
- [ ] Confirm `ADIKbuilder.md` and `ADIKBuilderExample.md` are **not** present in the distribution repo.
- [ ] Confirm the `vX.Y.Z` tag resolves to the correct commit.
- [ ] Share the repository URL with relevant teams.

---

## File Layout (Source Repository)

```
adik.md-agentic-development-and-implementation-kit/
├── ADIKbuilder.md                   ← this file (source-repo orchestrator, not deployed)
├── ADIKBuilderExample.md            ← self-sufficient guide for building your own ADIK (not deployed)
├── ADIK.md                          ← implementation orchestrator (deployed to target repos)
├── Registry.md                      ← DRY symbol registry template
├── README.md                        ← manifesto + dual-audience guide
├── agents/
│   ├── builder.agent.md
│   └── codebase-analyst.agent.md
├── skills/
│   ├── sdk-builder.skill.md
│   ├── sdk-consumer.skill.md
│   └── vectorize.skill.md           ← vector embedding subskill
└── mcp/
    └── adik-mcp-server.md
```

---

## Constraints and Principles

- **ADIKbuilder.md is never deployed.** It lives only in this source repository and must not be included in any bundle distributed to target repositories.
- **ADIKBuilderExample.md is never deployed.** It is a guide for developers who want to build their own ADIK; it is not part of the operational framework.
- **ADIK.md is the contract.** When `ADIK.md` changes in a backward-incompatible way, consumers must be notified via a version bump.
- **Every agent and skill file must be independently readable.** Each file must be fully actionable by an LLM agent without loading the entire repository.
- **The Registry format is stable.** Breaking changes to the registry schema require a major version bump.
- **Vectorization stays in the subskill.** `skills/vectorize.skill.md` is the only file that may contain embedding or vector-store logic.

---

## Related Files

| File | Role |
|---|---|
| `ADIK.md` | Implementation orchestrator — deployed to target repositories |
| `ADIKBuilderExample.md` | Step-by-step guide for building a custom ADIK implementation |
| `Registry.md` | Symbol registry template |
| `README.md` | Manifesto + dual-audience guide |
| `agents/builder.agent.md` | SDK builder agent |
| `agents/codebase-analyst.agent.md` | Codebase analysis + frameworkHints inference + dev-state check |
| `skills/sdk-builder.skill.md` | SDK code-generation skill |
| `skills/sdk-consumer.skill.md` | Consumption boilerplate skill |
| `skills/vectorize.skill.md` | Vector embedding subskill |
| `mcp/adik-mcp-server.md` | MCP server definition |
