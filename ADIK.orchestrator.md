# ADIK operational workflows

> **Version:** 2.0.0
> **Role:** Producer and consumer workflow contract
> **Scope:** Generation of completed adiks and their implementation by host agents

## Select the Workflow

- A developer asking to build an adik from a tool/library uses the **producer workflow**.
- A user asking to implement an existing adik uses the **consumer workflow**.
- A bootstrap containing empty Registry templates supplies producer tooling. It is
  not a completed SDK bundle. A completed adik has `adik.manifest.json` and real SDK code.

Use the user's request and artifact identity to select the workflow. Do not treat
absence of local producer source as a reason to regenerate an existing consumer SDK.

## Producer Workflow

1. Read `skills/build-adik/SKILL.md`. Resolve source path, requested SDK languages,
   output directory, bundle ID/version, and supported consumer environments.
2. Analyze the producer's public symbols using `agents/codebase-analyst.agent.md`.
   Populate `contracts/registry.json`, including the authoritative source revision.
3. Validate the registry through `mcp/adik_contracts.py`. Missing fields, duplicate
   symbols, invalid kinds, or empty contracts block generation. Perform the skill's
   semantic review of types and behavior as well.
4. Follow `agents/builder.agent.md` to generate actual SDK packages and matching
   implementation skills. Consumer frameworks come from `consumerFrameworks` or an
   explicit request; producer framework detection is descriptive only.
5. Run available SDK build/import checks and representative examples. Record exact
   results and limitations. A failed required check blocks a release-ready result.
6. Seal and validate the completed bundle with `scripts/adik-bundle.py`. Package the
   SDK code, implementation skills, contracts, examples, and manifest together.
7. Report the artifact and checks. The host agent carries out requested publishing
   through its normal tools and permission model.

For a new producer with no source, ask for the tool/library source or contract.
The user may separately request scaffolding. Never claim an empty template is a
completed adik. Optional generation of Go/Java/Kotlin remains explicit.

## Consumer Workflow

1. Locate the completed bundle manifest and the requested capability. Validate the
   bundle where the helper is available. Register it through `adik-bundle.py install`
   for native discovery, or explicitly load its implementation skill with the host.
2. Read the matching bundled skill and the precise capability references and examples.
   The contract and SDK version describe the producer library.
3. Inspect the consumer's dependency manifest, conventions, composition root, and
   relevant call sites. Select a supported recipe; surface material missing information.
4. Install the included SDK package using the application's dependency manager and
   implement the requested integration in application code.
5. Follow library-specific configuration, errors, lifecycle, serialization, and retry
   rules. Preserve unrelated application behavior and the bundled producer artifacts.
6. Run the documented example and application checks; report actual results.

The consumer does not need the producer repository to use the completed adik.
A source reference remains available when deeper investigation is necessary.

## Context and Ownership

`adik-embed.py` registers producer guidance in a producer repository.
`adik-bundle.py install` registers a completed adik's consumer implementation skill.
Consumer files live under `.adik/<id>/` and client adapters use package-specific
names. The host's context files receive a package-specific guarded block.

SDK generation preserves producer source. Consumer implementation edits are scoped
by the user's request. Removal never infers ownership from generic directory names.

## Execution and Optional Integrations

ADIK supplies procedures and artifact contracts. A host agent executes them. A
scheduled refresh requires the developer's chosen agent/CI integration; installing
ADIK does not create an automatic agent execution service. MCP instruction payloads
are a supported handoff. Vector retrieval is optional and only used when configured.

## Related Files

- `ADIK.md`: thesis and shared contracts.
- `skills/build-adik/SKILL.md`: producer procedure.
- `skills/sdk-consumer/SKILL.md`: generation of implementation skills and examples.
- `schemas/adik-manifest.schema.json`: completed-adik manifest.
- `scripts/adik-bundle.py`: sealing, validation, packaging, registration, and removal.
