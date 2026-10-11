# ADIKbuilder — framework maintainer guide

> **Version:** 2.0.0
> **Role:** Source-repository factory guide
> **Scope:** Maintaining the ADIK skill suite; not shipped as a consumer skill

## Purpose

ADIK is the thesis and producer skill suite. A developer invokes it to generate an
adik: **actual SDK code plus matching agentic elements**, packaged as one release.
A user's agent implements that adik in application code using its bundled skills.

Maintain the producer/consumer distinction throughout code, instructions, and docs.
The host coding agent owns execution. Helpers make artifact contracts repeatable.

## Producer Workflow

`skills/build-adik/SKILL.md` coordinates producer analysis, SDK generation, creation
of implementation skills and examples, and completed-bundle verification.
`agents/codebase-analyst.agent.md` and `agents/builder.agent.md` retain the detailed
analysis and build responsibilities. Canonical native skills live in `skills/*/SKILL.md`;
legacy `*.skill.md` files point to those entries for compatibility.

## Consumer Workflow

A completed adik includes its actual SDK, canonical contracts, versioned implementation
skills, and referenced assets. The consumer agent loads its capability guidance,
inspects the application's integration points, and makes the requested application
changes. It does not populate a new library registry from consumer application code.

## Three Artifacts

| Artifact | Purpose | Mechanism |
|---|---|---|
| ADIK framework source | Develop the thesis, skills, helpers, and tests | This repository |
| Producer toolkit bootstrap | Bring generation skills into a library repository | `scripts/adik-deploy.py` |
| Completed adik | Distribute generated SDK code and matching implementation knowledge | `scripts/adik-bundle.py pack` |

The producer bootstrap includes the standard, workflow, registry templates, agents,
skills, schemas, dependency instructions, and helpers. Empty templates are not a
completed adik. `--dist` on the legacy deploy script still distributes the producer
toolkit; completed release archives use the bundle command.

## Development Checks

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/check-docs.py
python3 adik-lint.py ADIK.md
python3 adik-lint.py ADIK.orchestrator.md
python3 scripts/adik-bundle.py validate --bundle examples/hello-adik
```

For the documentation site, install `requirements-docs.txt` and run `mkdocs build --strict`.

## Changing a Contract

1. Update the standard and the relevant schema/helper together.
2. Update producer skills and the generated consumer-skill requirements.
3. Add behavior-based fixtures for changed contracts; keep the reference adik valid.
4. Update README, architecture, quickstarts, examples, migration notes, and changelog.
5. Run the checks and regenerate source instructions with
   `python3 scripts/adik-embed.py --source-context --target .`.

Use a major version for incompatible artifact/workflow changes, a minor version for
backward-compatible additions, and a patch version for compatible fixes. Framework
version, manifest schema version, and an individual library's SDK release version are
separate concepts. The three root framework documents must share a version.

## Distribution and Publication

Producer bootstrap:

```bash
python3 scripts/adik-deploy.py --source . --target /path/to/library --embed
```

Completed adik, after the host agent generates its SDK and agentic elements:

```bash
python3 scripts/adik-bundle.py seal --bundle /path/to/generated-adik
python3 scripts/adik-bundle.py validate --bundle /path/to/generated-adik
python3 scripts/adik-bundle.py pack --bundle /path/to/generated-adik --output /path/to/adik.zip
```

Publishing an archive/package or creating a separate distribution repository is an
explicit user-directed action. Repository work can be reviewed through a draft PR.

## Constraints

- Preserve producer source during generation.
- Bind actual SDK code and implementation knowledge to one completed-adik version.
- Record unknown behavior; do not create unsupported API or runtime guarantees.
- Keep producer architecture and consumer compatibility separate.
- Use deterministic helpers for context registration and file ownership.
- Keep optional languages, vector retrieval, and MCP integrations explicit.
- Validate the handoff without requiring ADIK to own the host's execution platform.
