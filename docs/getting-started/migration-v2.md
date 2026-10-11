# Migrating ADIK 1.x to the completed-adik contract

Version 2 makes the producer/consumer handoff explicit. It changes the completed
artifact contract and consumer workflow, so it is a major framework revision.

| Previous convention | Version 2 |
|---|---|
| A deployed generation toolkit was called an adik | Bootstrap toolkit and completed SDK-and-skills bundle are distinct |
| `skills/<name>.skill.md` | Canonical `skills/<name>/SKILL.md`; legacy entries remain pointers |
| Lowercase `agents.md` for generic discovery | Uppercase `AGENTS.md` for Codex; client-specific registration adapters |
| Consumer boilerplate inferred producer framework | Declare supported `consumerFrameworks`; inspect the application during implementation |
| SDK files and instructions had no completed-bundle manifest | One manifest, release version, references, and file inventory |
| Generic directories treated as owned during eject | Per-file receipts; modified and unowned files preserved |
| Every commit claimed to refresh SDKs automatically | A developer's host agent/scheduler performs refresh when configured |

## Producer migration

1. Preserve your existing generated SDK and local modifications before updating the toolkit.
2. Use the legacy entry pointers or the new native skills. Add `consumerFrameworks`
   separately from producer environment hints.
3. Normalize your validated registry to the JSON contract. Legacy YAML-in-Markdown,
   simple tables, and explicitly active partitions remain readable by the shared helper.
4. Generate matching implementation skills for the SDK code, with exact public symbols,
   release version, examples, and capability references.
5. Populate the completed manifest, run SDK checks, seal, validate, and package.

An empty registry template is suitable only before producer analysis. An unused
`Registry.index.md` no longer overrides monolithic mode.

## Consumer migration

Obtain the completed code-and-skills bundle. Register its implementation skill and
ask your agent to implement or migrate the desired capability. The consumer's
application becomes the integration target, not a new source for SDK generation.

## Existing installations

Legacy installations without a producer ownership receipt are not automatically
removed. Inspect those files manually. Do not infer ownership from `agents/`,
`skills/`, or `mcp/`. Completed-adik registration records its own file inventory and
refuses to overwrite preexisting unowned paths. Review local changes before upgrading.

The reference installer supports one client per bundle ID. Remove its registration
before switching clients or replacing a version. Application code and dependencies
remain the application's responsibility.
