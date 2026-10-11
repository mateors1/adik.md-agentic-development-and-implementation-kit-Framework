#!/usr/bin/env python3
"""Check local Markdown targets, native skill metadata and framework document shape."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'mcp'))
from adik_contracts import ContractError, skill_metadata


def main():
    errors=[]
    files=[p for p in ROOT.rglob('*.md') if not any(x in p.parts for x in ('.git','build','site','__pycache__'))]
    for path in files:
        content=re.sub(r'```.*?```','',path.read_text(),flags=re.S)
        links=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',content)
        links+=re.findall(r'^\s*\[[^\]]+\]:\s*(\S+)',content,re.M)
        for link in links:
            link=link.strip().strip('<>')
            if not link or link.startswith(('#','http:','https:','mailto:','adik:')):
                continue
            target=unquote(link.split('#')[0])
            resolved=(path.parent/target).resolve()
            if not resolved.exists():
                errors.append(f'{path.relative_to(ROOT)}: missing {link}')
            elif path.is_relative_to(ROOT/'docs') and not resolved.is_relative_to(ROOT/'docs'):
                errors.append(f'{path.relative_to(ROOT)}: site link leaves docs directory: {link}')
    for path in ROOT.rglob('SKILL.md'):
        try:
            skill_metadata(path)
        except (ContractError,OSError) as exc:
            errors.append(str(exc))
    for error in errors:
        print(error)
    print(f'Documentation: {len(files)} Markdown files, {len(errors)} errors')
    return bool(errors)


if __name__=='__main__':
    raise SystemExit(main())
