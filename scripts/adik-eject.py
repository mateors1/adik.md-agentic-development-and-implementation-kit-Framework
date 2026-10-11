#!/usr/bin/env python3
"""Remove unchanged producer-toolkit files recorded by deployment. Preserve host files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'mcp'))
from adik_contracts import ContractError, relative_path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,default=Path('.'))
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--confirm',action='store_true')
    parser.add_argument('--keep-scripts',action='store_true')
    parser.add_argument('--remove-sdk',action='store_true',help='Legacy option: only SDK files in an ownership receipt could be removed')
    args=parser.parse_args()
    target=args.target.resolve()
    receipt=target/'.adik-producer-files.json'
    try:
        if not receipt.is_file():
            raise ContractError('No deployment ownership receipt. Review legacy files manually; directory names do not establish ownership.')
        inventory=json.loads(receipt.read_text())
        if not isinstance(inventory,dict):
            raise ContractError('Invalid producer ownership receipt')
        actions=[]
        preserved={}
        for name,expected in inventory.items():
            path=relative_path(target,name)
            allowed=(name in {'ADIK.md','ADIK.orchestrator.md','Registry.md','Registry.index.md','adik-lint.py','requirements-adik.txt'}
                     or name.startswith(('agents/','skills/','scripts/','mcp/','schemas/','.agents/skills/')))
            if not allowed:
                raise ContractError(f'Receipt claims an unrelated file: {name}')
            if not path.exists():
                continue
            if (args.keep_scripts and name.startswith('scripts/')) or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
                print(f'PRESERVE modified/requested file: {name}')
                preserved[name]=expected
            else:
                actions.append(path)
        for path in actions:
            print('DELETE FILE',path.relative_to(target))
        if args.dry_run:
            return 0
        if not args.confirm and os.environ.get('ADIK_EJECT','').lower()!='true':
            raise ContractError('Use --confirm to execute the reviewed removal plan')
        embed=target/'scripts/adik-embed.py'
        if embed in actions:
            result=subprocess.run([sys.executable,str(embed),'--target',str(target),'--action','remove'])
            if result.returncode:
                return result.returncode
        for path in actions:
            path.unlink()
            parent=path.parent
            while parent!=target:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent=parent.parent
        if preserved:
            receipt.write_text(json.dumps(preserved,indent=2)+'\n')
        else:
            receipt.unlink()
        print('Producer toolkit removed; unowned and modified files preserved. Generated SDK output preserved.')
        return 0
    except (OSError,ValueError,ContractError) as exc:
        print(f'ADIK eject: FAIL — {exc}',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
