# ADIKbuilder.md — Agentic Development and Implementation Kit Builder

> **Version:** 1.0.0
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
