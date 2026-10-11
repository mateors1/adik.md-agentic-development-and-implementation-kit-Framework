# ADIK Standard Specification

> **Standard Version:** 2.0.0
> **Status:** Proposed in the producer/consumer modernization change

## 1. Thesis and terminology

ADIK is a skill suite that generates SDKs for agents. An **adik** is the completed
artifact: actual generated SDK code plus matching implementation skills, contracts,
examples, and context, shipped together. The host coding agent executes the skills.

A **producer** is the developer of the source tool/library. A **consumer** is the
application developer whose agent implements the completed adik. The **producer
toolkit** is the generation scaffolding; it is distinct from a completed adik.

MUST, SHOULD, and MAY express normative requirements in this document.

## 2. Producer requirements

The producer workflow MUST analyze public interfaces, populate and validate a
registry, generate actual SDK source, generate matching agentic elements, run
available checks, and package one completed deliverable. It MUST preserve source
library code unless the developer separately requests source changes.

A producer MUST distinguish its own framework architecture from supported consumer
frameworks. Missing consumer-framework information SHOULD yield framework-neutral
recipes. Optional generation targets MUST be explicitly selected.

## 3. Completed-adik contract

A completed adik MUST contain the generated SDK source and package metadata,
`contracts/registry.json` (or another manifest-declared JSON registry), at least one
native implementation skill for every SDK language, runnable examples, implementation
references, and `adik.manifest.json`. It MUST pass the
[completed bundle contract](bundle-contract.md).

The manifest declares schemaVersion 2 and binds SDK declarations and skill
`metadata.sdk-version` fields to one bundle release version. SDK source code MUST be included;
a remote package URL alone is insufficient. All declared artifact paths MUST be
relative, present, and inside the bundle. Symlinks are excluded. The file inventory
MUST match the payload exactly, using SHA-256 digests. Hashes detect drift, not publisher identity.

Framework version, manifest schema version, and individual bundle release version
are distinct. A bundle generated with ADIK 2.0 may have release version 1.0.0.

## 4. Registry

The canonical JSON registry contains `schemaVersion: 2`, `metadata`, and `symbols`.
Metadata MUST contain nonempty strings: `name`, `version`, `projectType`,
`sourceLanguage`, `lastAnalysed`, and `lastAnalysedCommit`. `projectType` is `api`,
`service`, or `library`. The source revision MUST match the completed-bundle manifest.

Each symbol MUST have a unique nonempty `id`, a supported `kind`, `name`, `namespace`,
and `signature`. Kinds are function, class, interface, enum, schema, endpoint, and
type. Descriptions, parameters, return types, errors, source locations, and behavioral
constraints SHOULD supply implementation knowledge. A completed registry MUST have
at least one symbol. Implementations MAY add fields needed for their tool/library.

Producer compatibility readers support legacy Markdown metadata, YAML symbol blocks,
and simple symbol tables. Required section markers must be unique and ordered.
Explicit `registryPath` takes precedence; otherwise a completed manifest or canonical
JSON registry is used. A legacy index is active only when partitioned mode is declared.
An unused index template does not activate partitioning. Partition identities and
source revisions must agree; IDs are unique across all partitions.

## 5. Implementation skills

Generated consumer skills MUST use `SKILL.md` with name and description frontmatter plus `metadata.sdk-version`. Portable generated descriptions are single-line strings. The skill MUST
identify its SDK and version, route capabilities to exact references and symbols,
explain configuration and lifecycle, provide runnable examples, describe error
handling and limitations, and define verification steps.

The manifest MUST list each skill's SDK languages, symbol IDs, references, and examples.
The helper checks these declarations. SDK semantics and the quality of the instructions
require SDK tests and representative consumer exercises; a structural pass alone
MUST NOT be reported as proof of correct integration.

## 6. Consumer workflow

The consumer agent MUST use the bundled producer contract as its library knowledge.
It SHOULD inspect the application's manifests, conventions, composition root, and
relevant call sites to select and adapt a recipe. The user's implementation request
authorizes the appropriate application edits. Producer source-preservation rules do
not prohibit these requested consumer changes.

The consumer MUST keep producer contracts and generated SDK files distinct from
application integration code. It MUST report checks actually run and unresolved
requirements. It SHOULD load a capability index first, then task-specific references.

## 7. Registration and removal

Registration MUST preserve unrelated project instructions and files. The reference
installer copies the entire completed adik under `.adik/<id>/`, creates a native
client adapter, and appends a package-specific context block. Ownership receipts
record files and hashes. Removal MUST be restricted to owned files and MUST preserve
modified or additional host files. The reference consumer remover refuses a removal
when recorded files or the owned context block have changed.

Producer toolkit removal likewise uses a deployment receipt. Legacy installations
without ownership evidence require manual review. Generic directory names such as
`agents/` and `skills/` never prove ownership.

## 8. Optional integrations

MCP MAY expose deterministic helpers and instruction payloads for the host agent.
Vector retrieval and scheduled refresh MAY be provided by the developer's environment.
Neither a built-in model runner nor a hosted execution service is required for conformance.
The base contract is a completed SDK-and-agentic-elements handoff.

## 9. Verification

Verify registry structure, skill metadata and references, bundle inventory, SDK
build/import behavior, and representative consumer use. A fresh-agent exercise SHOULD
provide only the completed bundle and the consumer application. Record skill selection,
correctness, application-convention adherence, context reads, and unnecessary searches.

See the [reference exercise](../examples/reference-adik.md) and
[consumer evaluation protocol](../examples/consumer-evaluation.md).
