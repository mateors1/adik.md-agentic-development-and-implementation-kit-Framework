# ADIK producer builder

Execute `skills/build-adik/SKILL.md` in the developer's coding agent. The result
is a completed adik: SDK source code plus matching agentic elements.

1. Read the producer registry and validate it using the shared helpers in
   `mcp/adik_contracts.py` or MCP `adik_validate_registry`. Resolve canonical JSON
   or explicitly active legacy Markdown partitions; stop on FAIL.
2. Select the requested SDK languages and bundle version. Use
   `skills/sdk-builder/SKILL.md` for TypeScript, Python and C#, and
   `skills/sdk-builder-tier2/SKILL.md` for Go, Java and Kotlin.
3. Write real source packages under `<bundle>/sdk/<language>/`. Run the relevant
   language build and behavior checks. Preserve producer source files.
4. Use `skills/sdk-consumer/SKILL.md` to generate library-specific implementation
   skills, focused references and executable examples. `consumerFrameworks`
   describes intended consumers; the producer's framework does not determine it.
5. Write `contracts/registry.json` and `adik.manifest.json` with matching source
   revision, SDK versions, skill versions and symbol relationships. Use the
   schemas in `schemas/`. Describe checks actually run and unresolved limitations.
6. Seal, validate and pack using `scripts/adik-bundle.py`. Hand the bundle to the
   developer for distribution. Publication belongs to their release process.

The MCP build tool supplies instructions; it does not execute this workflow.
Consumer application integration is performed later by the consumer's agent,
using the generated implementation skill. No hosted runner is required.
