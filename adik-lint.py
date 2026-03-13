#!/usr/bin/env python3
"""
adik-lint.py — ADIK Specification Linter

Validates that an ADIK.md file (or any ADIK implementation orchestrator) meets
the minimum structural requirements of the ADIK standard:

  1. YAML-like frontmatter block (Version, Role, Scope as Markdown blockquotes)
  2. ## Executive Summary section containing:
       a. A sub-heading or content block
       b. A "## Reach of ADIK" or "### Reach of ADIK" table with pipe-separated columns
  3. At least one ADIK Registry section marker pair
     (<!-- ADIK:<SECTION>:START --> / <!-- ADIK:<SECTION>:END -->)
     — only enforced when the file contains any ADIK markers at all.

Usage:
    python adik-lint.py [FILE]

    FILE defaults to ADIK.md in the current directory.

Exit codes:
    0  All checks passed.
    1  One or more checks failed (details printed to stdout).
    2  File not found or could not be read.
"""

import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_frontmatter(lines: list[str]) -> list[str]:
    """
    Expect blockquote-style frontmatter near the top of the file:
        > **Version:** x.y.z
        > **Role:** ...
        > **Scope:** ...
    The three keys must all appear within the first 20 non-blank lines.
    """
    errors = []
    window = "\n".join(lines[:20])
    required_keys = ["Version", "Role", "Scope"]
    missing = [k for k in required_keys if not re.search(rf"\*\*{k}:\*\*", window)]
    if missing:
        errors.append(
            f"FRONTMATTER: Missing blockquote field(s): {', '.join(missing)}. "
            "Expected '> **Version:** ...', '> **Role:** ...', '> **Scope:** ...' "
            "within the first 20 lines."
        )
    return errors


def check_executive_summary(content: str) -> list[str]:
    """
    The file must contain a '## Executive Summary' heading.
    """
    errors = []
    if not re.search(r"^#{1,3}\s+Executive Summary", content, re.MULTILINE):
        errors.append(
            "EXECUTIVE_SUMMARY: No '## Executive Summary' section found. "
            "Every ADIK orchestrator must have this section."
        )
    return errors


def check_reach_of_adik(content: str) -> list[str]:
    """
    There must be a 'Reach of ADIK' heading followed by a Markdown table
    (lines containing '|') within 30 lines after the heading.
    """
    errors = []
    match = re.search(r"^#{1,4}\s+Reach of ADIK", content, re.MULTILINE)
    if not match:
        errors.append(
            "REACH_TABLE: No 'Reach of ADIK' section found. "
            "The ADIK standard requires a table listing what ADIK covers."
        )
        return errors

    # Find the section content after the heading
    after_heading = content[match.end():]
    lines_after = after_heading.splitlines()[:30]
    has_table = any("|" in line for line in lines_after)
    if not has_table:
        errors.append(
            "REACH_TABLE: 'Reach of ADIK' section exists but no Markdown table "
            "(pipe-separated columns) was found within 30 lines of the heading."
        )
    return errors


def check_registry_markers(content: str) -> list[str]:
    """
    If the file contains ANY ADIK registry markers, every START must have a
    matching END for the same section name.

    This check is skipped if the file contains no ADIK markers at all
    (e.g. the file is the implementation orchestrator template, not a Registry).
    """
    errors = []
    starts = re.findall(r"<!--\s*ADIK:(\w+):START\s*-->", content)
    ends = re.findall(r"<!--\s*ADIK:(\w+):END\s*-->", content)

    if not starts and not ends:
        return errors  # No markers present — skip this check

    starts_set = set(starts)
    ends_set = set(ends)
    unmatched_starts = starts_set - ends_set
    unmatched_ends = ends_set - starts_set

    if unmatched_starts:
        errors.append(
            f"REGISTRY_MARKERS: Section(s) have START but no END: "
            f"{', '.join(sorted(unmatched_starts))}"
        )
    if unmatched_ends:
        errors.append(
            f"REGISTRY_MARKERS: Section(s) have END but no START: "
            f"{', '.join(sorted(unmatched_ends))}"
        )
    return errors


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def lint(path: Path) -> int:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        return 2
    except OSError as exc:
        print(f"ERROR: Could not read {path}: {exc}")
        return 2

    lines = content.splitlines()
    all_errors: list[str] = []

    all_errors += check_frontmatter(lines)
    all_errors += check_executive_summary(content)
    all_errors += check_reach_of_adik(content)
    all_errors += check_registry_markers(content)

    if all_errors:
        print(f"adik-lint: FAIL — {path}")
        for err in all_errors:
            print(f"  ✗ {err}")
        return 1

    print(f"adik-lint: PASS — {path} ({len(lines)} lines, {len(content)} bytes)")
    return 0


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ADIK.md")
    sys.exit(lint(target))


if __name__ == "__main__":
    main()
