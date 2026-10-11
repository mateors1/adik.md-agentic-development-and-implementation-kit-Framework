#!/usr/bin/env python3
"""Check the structure of ADIK standard and workflow documents."""
import re
import sys
from pathlib import Path


def lint(path: Path) -> int:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"adik-lint: {exc}")
        return 2
    errors = []
    if not re.search(r"\*\*Version:\*\*\s+\d+\.\d+\.\d+", content):
        errors.append("Missing semantic Version field")
    required = ("What Is ADIK?", "What Is an adik?", "Standard Contracts") if path.name == "ADIK.md" else ("Producer Workflow", "Consumer Workflow")
    for heading in required:
        if not re.search(r"^## " + re.escape(heading) + r"\s*$", content, re.M):
            errors.append(f"Missing section: {heading}")
    for section in set(re.findall(r"<!-- ADIK:(\w+):(?:START|END) -->", content)):
        start, end = f"<!-- ADIK:{section}:START -->", f"<!-- ADIK:{section}:END -->"
        if content.count(start) != content.count(end) or content.find(end) < content.find(start):
            errors.append(f"Mismatched or reversed marker pair: {section}")
    print(f"adik-lint: {'FAIL' if errors else 'PASS'} — {path}")
    for error in errors:
        print(f"  {error}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(lint(Path(sys.argv[1] if len(sys.argv) > 1 else "ADIK.md")))
