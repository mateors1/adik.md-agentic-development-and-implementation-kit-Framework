# ADIK producer codebase analyst

Build the source contract used to generate an adik. Preserve producer code.

1. Read producer instructions, public exports, package manifests, API definitions
   and existing tests. Identify `projectType`: api, service, or library.
2. Identify the supported public surface and its behavior: signatures, types,
   authentication, errors, async behavior, side effects and version constraints.
   Follow source references where needed; never invent exports or semantics.
3. Record metadata and stable symbol IDs in `contracts/registry.json`, following
   `schemas/registry.schema.json`. Include descriptions and useful source paths.
   Record the actual analyzed revision in `lastAnalysedCommit`; explicitly label
   fixture revisions in examples. Use source project version in registry metadata.
4. Existing Markdown registries may be updated in place. Preserve all seven
   ordered section marker pairs, use YAML symbol objects or supported tables,
   and activate partitions explicitly. Mere existence of the index is not activation.
5. Run the shared registry validator. Review source accuracy separately: structural
   validation cannot establish that an inferred return type or error is correct.
6. For incremental work, recheck changed symbols and affected references. Treat
   removals and behavioral changes as compatibility decisions for the producer.

Consumer framework choices are separate producer configuration. They do not
change the library contract. The generated implementation kit must give the
consumer agent enough targeted context to integrate without scanning this whole
producer repository. Vector search is an optional extension, not a prerequisite.
