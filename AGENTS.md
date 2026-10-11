# ADIK framework contributor guidance

Read `ADIKbuilder.md` first. ADIK is the skill suite and thesis; an adik is
actual generated SDK code plus its matching agentic elements, shipped together.
The developer builds an adik from a tool/library. A user's agent implements that
adik in application code using its bundled implementation skill and context.

The host coding agent owns execution. Keep producer source preservation separate
from authorized consumer application edits. Library contracts belong to the producer;
consumer framework detection must not replace them.

## Checks

- Install helper dependencies: `python3 -m pip install -r requirements-dev.txt`.
- Run `python3 -m unittest discover -s tests -v`.
- Run `python3 scripts/check-docs.py` and `python3 adik-lint.py ADIK.md`.
- Run `python3 scripts/adik-bundle.py validate --bundle examples/hello-adik`.

## Maintenance

Update the standard, skills, examples, and docs together when a contract changes.
Keep skill frontmatter discoverable and load detailed references only as needed.
Preserve user files during registration and removal; use ownership receipts.
Use the shared registry validator in `mcp/adik_contracts.py` for CLI and MCP.
Regenerate these context files with `scripts/adik-embed.py --source-context`.

<!-- ADIK:PRODUCER:START -->
## Build an adik from this producer library

ADIK generates actual SDK code and matching implementation skills, contracts,
examples, and supporting context as one versioned adik. The host coding agent
executes the generation and implementation workflows.

- Start with `skills/build-adik/SKILL.md` and `ADIK.orchestrator.md`.
- Producer registry: `Registry.md`. Preserve the producer's source code.
- Declare supported `consumerFrameworks` independently from the producer stack.
- Generate real SDK files AND a library-specific implementation skill.
- Run `python3 scripts/adik-bundle.py seal --bundle <output>` and `validate`.
- Consumer agents use the completed adik's implementation skill to edit their application.
- Install completed bundles with `scripts/adik-bundle.py install`; this producer toolkit
  is not a completed adik and does not implement an SDK into a consumer application.
<!-- ADIK:PRODUCER:END -->
