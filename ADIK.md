# ADIK — Agentic Development and Implementation Kit

> **Version:** 2.0.0
> **Role:** Framework thesis and artifact contract
> **Scope:** Producer generation and consumer implementation

## What Is ADIK?

ADIK is a skill suite for tool and library developers to generate **adiks**: SDKs
for agents, containing actual SDK code and the agentic elements that help an agent
implement that SDK in a user's application. The host coding agent executes the
skills with its own tools.

## What Is an adik?

An adik is one versioned deliverable containing:

- Generated SDK source code and its package metadata.
- A producer symbol contract, tied to a source revision.
- Library-specific implementation skills in native `SKILL.md` format.
- Capability guidance, configuration and lifecycle rules, runnable examples,
  implementation assets, and known limitations.
- A manifest binding those elements to the same release and file inventory.

A user asks their agent to implement the adik in their code. The agent loads the
bundled implementation context, selects the relevant capability, inspects the
application's integration points, and implements the requested behavior. The bundle
supplies library knowledge so the agent does not need to rediscover the library.

## Producer Workflow

1. The tool/library developer calls ADIK in a coding agent.
2. Producer skills analyze public contracts and generate the SDK itself.
3. Producer skills generate matching implementation skills, examples, and context.
4. The agent runs SDK checks and validates the completed-adik contract.
5. The developer distributes the complete bundle: **SDK code + agentic elements**.

`ADIKbuilder.md` maintains the framework. `ADIK.orchestrator.md` describes the two
workflows. `skills/build-adik/SKILL.md` is the producer entry point.

## Consumer Workflow

1. Obtain the completed adik and register its implementation skill with the host agent.
2. Ask the agent to implement the required capability in the application.
3. The agent uses the bundled SDK, recipes, contracts, and examples, with targeted
   inspection of application conventions and integration points.
4. The agent edits the application as requested and runs the relevant checks.

## Standard Contracts

1. **SDK code and agentic elements ship together.** A toolkit bootstrap or a set of
   instructions without generated SDK code is not a completed adik.
2. **The producer owns the library contract.** The registry identifies public symbols
   and source revision. Consumer application inspection never replaces that registry.
3. **Generation preserves producer source.** Consumer implementation may modify the
   user's application under the implementation request.
4. **Versioned handoff.** Manifest, SDK declarations, and implementation skills agree
   on a release version. References and examples resolve inside the completed bundle.
5. **Discoverable implementation skills.** Skills use `SKILL.md` with `name` and
   `description`; generated consumer skills also declare `metadata.sdk-version`.
6. **Progressive context.** Load a short capability index, then the relevant recipe,
   symbols, and examples. Include authoritative source references for deeper inquiry.
7. **Explicit consumer support.** Supported consumer frameworks are declared separately
   from the producer's architecture. Unknown behavior is recorded as a limitation.
8. **Verifiable output.** Validate registry structure, file inventory, and skill references;
   run SDK and representative consumer checks. Record actual results, never implied passes.
9. **Host execution.** The coding agent orchestrates tools and applies implementation
   changes. MCP can expose helpers and instruction payloads.
10. **Owned installation.** Registration preserves project instructions and unrelated
    files. Removal uses receipts and refuses to delete modified consumer artifacts.

The completed bundle format is in `schemas/adik-manifest.schema.json`; the symbol
contract is in `schemas/registry.schema.json`. Human documentation:
[standard](docs/specification/standard.md), [bundle contract](docs/specification/bundle-contract.md),
[architecture](docs/specification/architecture.md), and [migration](docs/getting-started/migration-v2.md).
