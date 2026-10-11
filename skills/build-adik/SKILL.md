---
name: build-adik
description: Build a completed adik from a developer's tool or library by generating SDK source code together with matching implementation skills, contracts, and examples.
---

# Build an adik

ADIK is a skill suite. The calling coding agent executes this procedure with its
own tools. The output is a versioned bundle containing **actual SDK code plus the
agentic elements needed to implement that SDK**.

## Inputs

- Producer library/API source and its authoritative contracts.
- Requested SDK languages, bundle ID and release version.
- Consumer capabilities and supported consumer frameworks, when known.
- A dedicated output directory outside the producer's source tree.

## Procedure

1. Read the producer's project instructions and relevant public interfaces. Record
   source revision and build architecture separately from supported consumer frameworks.
2. Follow `agents/codebase-analyst.agent.md` from the producer toolkit root to populate
   `contracts/registry.json`. Use the registry schema bundled in `schemas/`.
3. Invoke the registry validator through the host agent. Resolve missing contracts;
   do not invent public symbols or behavioral guarantees.
4. Follow the SDK builder skill for each requested language. Write real SDK source,
   package metadata, public exports, configuration, and error handling. Preserve
   producer source. Run its build/import checks and record the actual results.
5. Follow the SDK consumer skill to generate library-specific `SKILL.md` procedures,
   capability references, runnable examples, and implementation assets that match
   the emitted SDK. The generated skill is what the consumer's agent will invoke.
6. Write `adik.manifest.json`: schemaVersion 2, bundle id/version, source revision,
   canonical registry path, SDK entries, implementation skill declarations, and files.
   Each SDK entry declares language, version, path, packageManifest and entryPoint.
   Each skill declares path, sdkLanguages, symbolIds, references and examples.
7. Run `python3 scripts/adik-bundle.py seal --bundle <output>` from the toolkit root.
   Then run `validate` against the same output. These helpers verify the handoff;
   they do not generate code or prove its runtime behavior.
8. Exercise a documented SDK example. Package using
   `python3 scripts/adik-bundle.py pack --bundle <output> --output <release>.zip`.
9. Report the complete bundle path, SDK and skill coverage, checks actually run,
   and any known limitations. Publishing is a separate user-directed action.

## Completion

The bundle includes SDK code, usable implementation skills, matching contracts,
examples, and a verified inventory. Metadata-only output is incomplete. Generation
and consumer implementation run in the host coding agent; ADIK supplies their
contracts and procedures. Consumer application changes never rewrite producer
registry data.
