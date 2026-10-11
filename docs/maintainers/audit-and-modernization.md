# ADIK audit and modernization pathways

ADIK's useful unit of delivery is an SDK and the knowledge to implement it, released
together. The producer calls the skill suite to generate that adik. The consumer
asks their own agent to implement it. This revision makes that boundary concrete.

Audit baseline: repository commit `4ca7d238175c1c5f6f4c5e43dd1498c1141afce5`.
Scope: architecture, producer/consumer handoff, instruction discovery, artifact
contracts, deterministic helpers, examples, documentation and CI. This is a product
and correctness audit, not a repository security certification or a model benchmark.
The changes below are proposed as framework 2.0.0; no release is implied.

## Findings and changes

| Baseline finding | Consequence | Change in this revision |
|---|---|---|
| Bootstrap deployment and finished adik were described as the same artifact | Copying framework files could be mistaken for SDK generation | Separate bootstrap, generation and completed-bundle commands and guides |
| SDK generation existed, but the implementation kit had no completed-delivery contract | Code and agent knowledge could drift or ship separately | Manifest binds actual SDK entry points, native skills, symbols, examples, references, release versions and hashes |
| Consumer skill mainly generated boilerplate during producer build | Consumer agents lacked an explicit application implementation procedure | Producer skill now generates library-specific implementation skills; consumer flow loads them to edit the app |
| Producer framework hints fed consumer defaults | A library's framework could incorrectly dictate the consumer architecture | Explicit `consumerFrameworks`; application framework inspected during implementation |
| Skills were flat `.skill.md` files and generic guidance used lowercase `agents.md` | Discovery depended on host-specific manual loading | Native `SKILL.md` entries, `AGENTS.md`, and Codex/Claude/Copilot registration adapters |
| MCP symbol parsing handled tables while registries also used YAML | Existing symbol declarations could be ignored | Shared JSON, YAML-in-Markdown and legacy table reader with partition support |
| Marker checks could pass without required sections; build preparation did not gate invalid contracts | Invalid analysis could reach SDK generation | Shared structural validator; FAIL blocks producer build handoff |
| Presence of the index template selected partition mode | An unused template could override a valid monolithic registry | Explicit activation and consistent registry resolution |
| Default specification linter expected a different document shape | Repository's own default check failed | Align the linter and versioned framework documents |
| Producer deployment omitted the linter that MCP invokes | Deployed helper path was incomplete | Deploy the linter, shared contracts module, schemas and dependency instructions |
| Eject inferred ownership from generic directory names | Unrelated project files could be deleted | Per-file deployment receipts and hash checks; preserve modified/unowned files |
| CI used incomplete marker checks and job-level file predicates | Green results did not establish the handoff contract | Behavior tests, reference-bundle validation, Python matrix, package build and docs checks |

Source areas at the baseline: `ADIKbuilder.md`, `ADIK.orchestrator.md`,
`skills/sdk-consumer.skill.md`, `mcp/adik_mcp_server.py`, `adik-lint.py`,
`scripts/adik-embed.py`, `scripts/adik-deploy.py`, `scripts/adik-eject.py`, and
`.github/workflows/adik-ci.yml`. Read those paths at the baseline commit when
comparing the findings with the updated files.

## Pathway 1: make the handoff dependable

Implemented in this revision: completed-bundle schema, native skills, shared
validation, reproducible ZIP packaging, scoped registration/removal, producer and
consumer guides, and the Python reference adik. Review the proposed major-version
contract and use the [migration guide](../getting-started/migration-v2.md).

Acceptance: SDK code and agentic elements exist together, refer to the same release,
and can be registered in a clean consumer application without the producer checkout.
Deterministic checks establish artifact and helper behavior. Native package correctness
still needs the relevant language builds and behavior checks.

## Pathway 2: measure whether agents can use the bundle

Next, run the [consumer evaluation protocol](../examples/consumer-evaluation.md)
with fresh host-agent sessions. Start with Python and TypeScript and a few concrete
capabilities: setup/authentication, a read operation, a mutation with error handling,
and an upgrade. Use realistic application fixtures and record client/model versions.

Measure task completion, SDK symbol correctness, application tests, unnecessary
producer-source reads, manual corrections and context loaded. Compare a docs-only
baseline with the completed adik on the same tasks. Set release thresholds after
collecting evidence. No live-agent performance results are claimed here.

## Pathway 3: expand generation recipes using that evidence

Add mature language/framework recipes one at a time, each with a producer fixture,
a completed SDK-and-skills bundle and a consumer integration exercise. Strengthen
native package-version checks, compatibility guidance and upgrade recipes as real
packages need them. Client adapters should share canonical skills and contracts.

Keep MCP optional. Add retrieval only when measured bundle size and task behavior
justify it. Hosted model execution, scheduling and publishing remain choices for the
developer's environment; they do not need to become ADIK product responsibilities.

## Validation of this revision

- 26 behavior tests passed on Python 3.12: canonical/legacy registries, invalid input,
  artifact relationships, hash drift, reproducible archives, client registration,
  ownership-aware removal, MCP handoffs and reference SDK behavior.
- The MCP wheel built locally, containing the server and shared contracts module.
- Documentation links and native skill metadata passed the repository checker.
- The reference SDK works from a registered bundle without the producer repository.
  Its package also builds, installs into an isolated directory and imports successfully.
- Python 3.10, 3.12 and 3.13 contract checks and package builds passed in
  [PR CI](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/actions/runs/38107183041).
- MkDocs dependencies could not be installed locally. The strict site build runs in
  CI; its first run exposed older ecosystem links that escaped the docs tree. Those
  links were corrected and the local checker now detects this class of problem.
  See [PR checks](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/pull/8/checks)
  for the current site-build result.

Client registration files were exercised deterministically. Live discovery by each
client and actual model-driven generation/implementation remain evaluation work.
