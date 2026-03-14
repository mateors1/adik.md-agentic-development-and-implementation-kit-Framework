#!/usr/bin/env python3
"""
adik-eject.py — ADIK Clean Uninstall / Eject Script

Removes all ADIK-generated and ADIK-owned artifacts from a target repository
so the team can stop using ADIK without leaving stale files behind.

Eject is SAFE by default:
  - Dry-run mode shows what would be deleted without touching anything.
  - Destructive operations require --confirm.
  - Source code is NEVER deleted.
  - Generated SDK directories are removed only when --remove-sdk is supplied.

Usage:
    # Preview what would be ejected
    python3 scripts/adik-eject.py --target <path-to-repo> --dry-run

    # Eject ADIK framework files (keep generated sdk/)
    python3 scripts/adik-eject.py --target <path-to-repo> --confirm

    # Eject everything including generated SDKs
    python3 scripts/adik-eject.py --target <path-to-repo> --confirm --remove-sdk

Environment variables:
    ADIK_EJECT=true   Equivalent to --confirm (enables non-interactive eject in CI)
    ADIK_EJECT_SDK=true  Also remove sdk/ directory (equivalent to --remove-sdk)
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# What gets removed
# ---------------------------------------------------------------------------

# Files that are always candidates for removal (ADIK framework files)
ADIK_FRAMEWORK_FILES = [
    "ADIK.md",
    "Registry.md",
    "Registry.index.md",
    "adik.env.json",
    "adik.config.json",
]

# Glob patterns for domain registry partitions
ADIK_REGISTRY_PATTERNS = ["Registry.*.md"]

# Directories that are always candidates for removal
ADIK_FRAMEWORK_DIRS = [
    "agents",
    "skills",
    "mcp",
    "vectors",
    "scripts",
]

# Generated SDK directory (only removed with --remove-sdk)
ADIK_SDK_DIR = "sdk"

# Context file handling: remove the ADIK block, NOT the entire file
ADIK_CONTEXT_FILES = [
    ".github/copilot-instructions.md",
    "CLAUDE.md",
    "agents.md",
]

ADIK_START_MARKER = "<!-- ADIK:START -->"
ADIK_END_MARKER = "<!-- ADIK:END -->"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _remove_adik_block(content: str) -> Tuple[str, bool]:
    """Remove the ADIK block from file content. Returns (updated_content, was_modified)."""
    start = content.find(ADIK_START_MARKER)
    end = content.find(ADIK_END_MARKER)

    if start == -1 or end == -1:
        return content, False

    before = content[:start].rstrip("\n")
    after = content[end + len(ADIK_END_MARKER):].lstrip("\n")
    updated = (before + "\n" + after).rstrip() + "\n"
    return updated, True


def _collect_removals(target: Path, remove_sdk: bool, keep_scripts: bool = False) -> List[Tuple[str, Path, str]]:
    """
    Collect all paths that would be removed.
    Returns list of (action, path, reason) tuples.
    action: "delete_file" | "delete_dir" | "strip_block"
    """
    actions = []

    # Framework files
    for fname in ADIK_FRAMEWORK_FILES:
        p = target / fname
        if p.exists():
            actions.append(("delete_file", p, "ADIK framework file"))

    # Registry partition files (exclude files already added from ADIK_FRAMEWORK_FILES)
    already_collected = {p for _, p, _ in actions}
    for pattern in ADIK_REGISTRY_PATTERNS:
        for p in sorted(target.glob(pattern)):
            if p not in already_collected:
                actions.append(("delete_file", p, "ADIK registry partition"))
                already_collected.add(p)

    # Framework directories
    for dname in ADIK_FRAMEWORK_DIRS:
        if keep_scripts and dname == "scripts":
            continue
        p = target / dname
        if p.exists() and p.is_dir():
            actions.append(("delete_dir", p, "ADIK framework directory"))

    # SDK directory (optional)
    if remove_sdk:
        sdk_path = target / ADIK_SDK_DIR
        if sdk_path.exists() and sdk_path.is_dir():
            actions.append(("delete_dir", sdk_path, "ADIK generated SDK (--remove-sdk)"))

    # Context files: strip block only
    for cfile in ADIK_CONTEXT_FILES:
        p = target / cfile
        if p.exists():
            content = p.read_text(encoding="utf-8")
            if ADIK_START_MARKER in content:
                actions.append(("strip_block", p, "ADIK context block"))

    return actions


def _print_plan(actions: List[Tuple[str, Path, str]]) -> None:
    print("\nEject plan:")
    print("-" * 60)
    for action, path, reason in actions:
        verb = {
            "delete_file": "DELETE FILE",
            "delete_dir": "DELETE DIR ",
            "strip_block": "STRIP BLOCK",
        }[action]
        print(f"  {verb}  {path}  ({reason})")
    print("-" * 60)
    print(f"  {len(actions)} operation(s) total.\n")


def _execute_plan(
    actions: List[Tuple[str, Path, str]], dry_run: bool
) -> None:
    for action, path, reason in actions:
        if dry_run:
            print(f"  [dry-run] would {action} → {path}")
            continue

        try:
            if action == "delete_file":
                path.unlink()
                print(f"  [deleted]  {path}")
            elif action == "delete_dir":
                shutil.rmtree(path)
                print(f"  [deleted]  {path}/")
            elif action == "strip_block":
                content = path.read_text(encoding="utf-8")
                updated, changed = _remove_adik_block(content)
                if changed:
                    path.write_text(updated, encoding="utf-8")
                    print(f"  [stripped] {path}")
                else:
                    print(f"  [skipped]  {path} (no block found)")
        except OSError as exc:
            print(f"  [error]    {path}: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cleanly eject ADIK from a repository."
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Root directory of the target repository (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without making any changes",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required to execute destructive operations (or set ADIK_EJECT=true)",
    )
    parser.add_argument(
        "--remove-sdk",
        action="store_true",
        help="Also remove the generated sdk/ directory (or set ADIK_EJECT_SDK=true)",
    )
    parser.add_argument(
        "--keep-scripts",
        action="store_true",
        help=(
            "Preserve the scripts/ directory during eject. "
            "Recommended when you want to verify the eject or re-run the script afterwards."
        ),
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"Error: target directory '{target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Honour environment variables for non-interactive / CI usage.
    confirmed = args.confirm or os.environ.get("ADIK_EJECT", "").lower() == "true"
    remove_sdk = args.remove_sdk or os.environ.get("ADIK_EJECT_SDK", "").lower() == "true"
    keep_scripts = args.keep_scripts or os.environ.get("ADIK_EJECT_KEEP_SCRIPTS", "").lower() == "true"
    dry_run = args.dry_run

    print(f"ADIK Eject — target={target}")
    print(f"  dry-run={dry_run}, confirmed={confirmed}, remove-sdk={remove_sdk}, keep-scripts={keep_scripts}\n")

    actions = _collect_removals(target, remove_sdk, keep_scripts)

    if not actions:
        print("Nothing to eject — no ADIK artefacts found.")
        sys.exit(0)

    _print_plan(actions)

    if dry_run:
        print("Dry-run complete. No files were modified.")
        print("Re-run with --confirm to execute.")
        sys.exit(0)

    if not confirmed:
        print(
            "Eject requires --confirm (or ADIK_EJECT=true) to execute.\n"
            "Run with --dry-run first to preview what would be removed.",
        )
        sys.exit(1)

    print("Executing eject...")
    _execute_plan(actions, dry_run=False)
    print("\nADIK has been ejected. Source code was not modified.")
    if keep_scripts:
        print("Note: scripts/ directory was preserved (--keep-scripts).")
    if not remove_sdk:
        print(
            "Note: generated sdk/ directory was preserved. "
            "Re-run with --remove-sdk to delete it."
        )


if __name__ == "__main__":
    main()
