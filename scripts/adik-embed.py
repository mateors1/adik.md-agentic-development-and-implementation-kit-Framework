#!/usr/bin/env python3
"""Manage producer guidance. Completed consumer adiks use adik-bundle.py install."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mcp'))
from adik_contracts import ContractError, relative_path, resolve_registry

START = '<!-- ADIK:PRODUCER:START -->'
END = '<!-- ADIK:PRODUCER:END -->'
CONTEXTS = ('AGENTS.md', 'CLAUDE.md', '.github/copilot-instructions.md')


def _upsert_block(content, block):
    for start,end in [(START,END),('<!-- ADIK:START -->','<!-- ADIK:END -->')]:
        if start in content or end in content:
            if content.count(start) != 1 or content.count(end) != 1 or content.index(end) < content.index(start):
                raise ContractError('Repair malformed or repeated context markers before embedding')
            before,rest=content.split(start,1)
            _,after=rest.split(end,1)
            return before+block+after
    return content.rstrip('\n')+('\n\n' if content else '')+block+'\n'


def producer_block(target):
    registry=resolve_registry(target).relative_to(target).as_posix()
    return f'''{START}
## Build an adik from this producer library

ADIK generates actual SDK code and matching implementation skills, contracts,
examples, and supporting context as one versioned adik. The host coding agent
executes the generation and implementation workflows.

- Start with `skills/build-adik/SKILL.md` and `ADIK.orchestrator.md`.
- Producer registry: `{registry}`. Preserve the producer's source code.
- Declare supported `consumerFrameworks` independently from the producer stack.
- Generate real SDK files AND a library-specific implementation skill.
- Run `python3 scripts/adik-bundle.py seal --bundle <output>` and `validate`.
- Consumer agents use the completed adik's implementation skill to edit their application.
- Install completed bundles with `scripts/adik-bundle.py install`; this producer toolkit
  is not a completed adik and does not implement an SDK into a consumer application.
{END}'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,default=Path('.'))
    parser.add_argument('--action',choices=['upsert','remove','check'],default='upsert')
    parser.add_argument('--source-context',action='store_true',help='Regenerate framework-maintainer context in the ADIK source repository')
    args=parser.parse_args()
    target=args.target.resolve()
    try:
        if args.source_context and not (target/'ADIKbuilder.md').is_file():
            raise ContractError('--source-context requires the framework source repository')
        block=producer_block(target) if args.action=='upsert' else ''
        planned={}
        for name in CONTEXTS:
            path=relative_path(target,name)
            existing=path.read_text() if path.exists() else ''
            if args.action=='check':
                if existing.count(START) != 1 or existing.count(END) != 1 or existing.index(END) < existing.index(START):
                    raise ContractError(f'Producer context missing: {name}')
                continue
            if args.action=='remove':
                updated=existing
                for start,end in [(START,END),('<!-- ADIK:START -->','<!-- ADIK:END -->')]:
                    if start in updated or end in updated:
                        if updated.count(start)!=1 or updated.count(end)!=1 or updated.index(end)<updated.index(start):
                            raise ContractError(f'Malformed markers in {name}')
                        before,rest=updated.split(start,1)
                        _,after=rest.split(end,1)
                        updated=before+after
            elif args.source_context:
                updated='''# ADIK framework contributor guidance

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

'''+block+'\n'
            else:
                updated=_upsert_block(existing,block)
            planned[path]=updated
        for path,content in planned.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content)
        print('ADIK producer context: PASS')
        return 0
    except (ContractError,OSError) as exc:
        print(f'ADIK producer context: FAIL — {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
