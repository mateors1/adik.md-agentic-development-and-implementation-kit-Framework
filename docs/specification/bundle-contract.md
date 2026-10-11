# Completed-adik bundle contract

A completed adik contains **actual generated SDK code + matching agentic elements**.
Producer bootstrap tooling and completed deliverables use separate commands.

## Manifest fields

| Field | Meaning |
|---|---|
| `schemaVersion` | `2`; the artifact-format version |
| `id` | Stable lowercase kebab-case package identity, maximum 48 characters |
| `version` | Bundle release version, e.g. `1.0.0` |
| `source.revision` | Producer revision used to generate code and context |
| `registry` | Relative path to the canonical JSON registry |
| `sdks` | Language, version, directory, package manifest, and source entry point |
| `implementationSkills` | Skill path, sdkLanguages, symbolIds, references, examples |
| `files` | Exact relative payload paths and SHA-256 digests; excludes the manifest itself |

A skill's `metadata.sdk-version` and each SDK's declared `version` must match the bundle
version. Version declarations are checked; the producer remains responsible for
correct native package metadata and behavior. Each declared SDK needs nonempty source
and package metadata and at least one implementation skill. Every skill-declared
symbol must exist in the registry, and every reference/example must exist.

See the complete example in `examples/hello-adik/adik.manifest.json` in the repository
and the schema at `schemas/adik-manifest.schema.json`.

## Build and package

1. The host coding agent writes SDK source and matching skills/context into a dedicated
   output directory. It records provenance and fills manifest relationships.
2. Run SDK builds/imports and examples. Keep caches and dependencies outside the bundle.
3. `seal` validates structural relationships and writes the exact inventory.
4. `validate` checks structure, references, and inventory without changing the bundle.
5. `pack` validates and produces a ZIP with deterministic ordering and timestamps.

```bash
python3 scripts/adik-bundle.py seal --bundle /path/to/adik
python3 scripts/adik-bundle.py validate --bundle /path/to/adik
python3 scripts/adik-bundle.py pack --bundle /path/to/adik --output /path/to/release.zip
```

Sealing is a producer operation after reviewed changes. A consumer should validate an
obtained bundle, not reseal unexpected changes. The helper does not execute SDK code
or authenticate a publisher. Distribution trust follows the user's chosen source.

## Register and implement

```bash
python3 scripts/adik-bundle.py install --bundle /path/to/adik --target /path/to/app --client codex
```

Supported registration adapters:

| Client | Native skill directory | Context pointer |
|---|---|---|
| Codex | `.agents/skills/<id>-<skill>/SKILL.md` | `AGENTS.md` |
| Claude | `.claude/skills/<id>-<skill>/SKILL.md` | `CLAUDE.md` |
| Copilot | `.github/skills/<id>-<skill>/SKILL.md` | `.github/copilot-instructions.md` |

Registration copies the entire bundle to `.adik/<id>/`; it does not invoke a model or
install language dependencies. The native adapter points to the canonical bundled
skill, whose relative references remain valid. The consumer agent then installs the
included SDK package and makes the requested application changes. Build/install from
a temporary copy of SDK source so package-manager caches and metadata do not alter
the sealed bundle.

Repeated identical installation for the same client is idempotent. Conflicting files,
modified owned content, and a different installed version/client cause a refusal.
This release registers one client per installed bundle ID; changing it requires removal
and registration. Additional project files survive removal.

## Remove or upgrade

```bash
python3 scripts/adik-bundle.py remove --target /path/to/app --id hello --dry-run
python3 scripts/adik-bundle.py remove --target /path/to/app --id hello
```

Review and preserve local modifications first. Removal checks the receipt and owned
context block before deleting any file. It does not undo consumer application edits
or uninstall the SDK from the language environment. For an upgrade, remove the old
registration, register the new completed bundle, and ask the agent to migrate the
application using that release's guidance.
