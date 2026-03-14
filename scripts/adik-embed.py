#!/usr/bin/env python3
"""
adik-embed.py — Deterministic ADIK Self-Embedding Script

Manages the ADIK context blocks in:
  - .github/copilot-instructions.md
  - CLAUDE.md
  - agents.md

Uses <!-- ADIK:START --> / <!-- ADIK:END --> guard markers to ensure idempotent,
non-duplicating writes. Safe to run multiple times and across different LLM models.

Usage:
    python3 scripts/adik-embed.py --action upsert --target <path-to-repo>
    python3 scripts/adik-embed.py --action remove --target <path-to-repo>
    python3 scripts/adik-embed.py --action check  --target <path-to-repo>
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ADIK_START_MARKER = "<!-- ADIK:START -->"
ADIK_END_MARKER = "<!-- ADIK:END -->"

# Templates for each target file.  {vars} are filled at runtime.
COPILOT_BLOCK = """\
<!-- ADIK:START -->
## ADIK — Agentic Development and Implementation Kit

This project uses **ADIK** for automated SDK generation and maintenance.

- **Orchestrator:** `ADIK.md` (implementation orchestrator)
- **Registry:** `{registry_path}` (single source of truth for all public symbols)
- **Agents:** `agents/builder.agent.md`, `agents/codebase-analyst.agent.md`
- **Skills:** `skills/sdk-builder.skill.md`, `skills/sdk-consumer.skill.md`,
  `skills/vectorize.skill.md`, `skills/registry-validator.skill.md`
- **Tier-2 Skills:** `skills/sdk-builder-tier2.skill.md` (Go / Java / Kotlin — opt-in)
- **MCP server:** `mcp/adik-mcp-server.md`
- **Build output:** `sdk/` ({sdk_languages})

**Key rules for Copilot:**
- Never define a type in the SDK that is not first declared in `{registry_path}`.
- SDK files in `sdk/` are generated — do not edit them directly; update the source and re-run ADIK.
- To trigger SDK regeneration: `@agent builder task: build-sdk registry: {registry_path}`
- To refresh the registry: `@agent codebase-analyst task: analyse-and-register`
- To eject ADIK: run `python3 scripts/adik-eject.py --target .` or set `ADIK_EJECT=true`
<!-- ADIK:END -->
"""

CLAUDE_BLOCK = """\
<!-- ADIK:START -->
## ADIK — Agentic Development and Implementation Kit

**Executive Summary:** {project_summary}

**Orchestrator:** `ADIK.md`
**Registry:** `{registry_path}`
**SDK output:** `sdk/` ({sdk_languages})
**ADIK reach:** {adik_reach}

**Key rules:**
- `{registry_path}` is the single source of truth. All public symbols must be declared there.
- Files in `sdk/` are generated. Do not edit them manually.
- Run `@agent codebase-analyst task: analyse-and-register` to refresh the registry.
- Run `@agent builder task: build-sdk` to regenerate the SDK after registry changes.
- To eject ADIK cleanly: `python3 scripts/adik-eject.py --target .`
<!-- ADIK:END -->
"""

AGENTS_BLOCK = """\
<!-- ADIK:START -->
## ADIK — SDK Orchestrator

Loaded agents:
- agents/builder.agent.md
- agents/codebase-analyst.agent.md

Loaded skills:
- skills/sdk-builder.skill.md
- skills/sdk-consumer.skill.md
- skills/registry-validator.skill.md
- skills/vectorize.skill.md (loaded on demand when vectorMode is active)
- skills/sdk-builder-tier2.skill.md (loaded on demand when tier2Languages is configured)

Registry: {registry_path}
MCP server: mcp/adik-mcp-server.md
Vector store: {vector_store}
SDK output: sdk/ ({sdk_languages})
<!-- ADIK:END -->
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    """Read file content, returning empty string if file does not exist."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _write(path: Path, content: str) -> None:
    """Write content to file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [written] {path}")


def _upsert_block(existing: str, new_block: str) -> str:
    """
    Insert or replace the ADIK block in `existing`.

    - If no markers are present: append the block.
    - If markers are present: replace the content between them (inclusive).
    - Never duplicates the block.
    """
    start = existing.find(ADIK_START_MARKER)
    end = existing.find(ADIK_END_MARKER)

    if start == -1 and end == -1:
        # No existing block — append with a leading newline separator.
        separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
        return existing + separator + new_block.rstrip() + "\n"

    if start != -1 and end != -1:
        # Replace existing block (inclusive of markers).
        before = existing[:start]
        after = existing[end + len(ADIK_END_MARKER):]
        return before + new_block.rstrip() + "\n" + after.lstrip("\n")

    # Mismatched markers — append safely and warn.
    print(
        "  [warn] Mismatched ADIK markers detected. Appending new block. "
        "Please manually remove stale markers.",
        file=sys.stderr,
    )
    return existing + "\n\n" + new_block.rstrip() + "\n"


def _remove_block(existing: str) -> str:
    """Remove the ADIK block from `existing`, including surrounding blank lines."""
    start = existing.find(ADIK_START_MARKER)
    end = existing.find(ADIK_END_MARKER)

    if start == -1 or end == -1:
        return existing  # Nothing to remove.

    before = existing[:start].rstrip("\n")
    after = existing[end + len(ADIK_END_MARKER):].lstrip("\n")
    return (before + "\n" + after).rstrip() + "\n"


def _has_block(content: str) -> bool:
    return ADIK_START_MARKER in content and ADIK_END_MARKER in content


# ---------------------------------------------------------------------------
# Context gathering
# ---------------------------------------------------------------------------


def _gather_context(target: Path) -> dict:
    """Collect runtime values used in template rendering."""
    import json

    registry_path = "Registry.md"
    sdk_languages = "typescript, python, csharp"
    vector_store = "none"
    project_summary = "[auto-filled on deployment]"
    adik_reach = "src/**/* → Registry.md → sdk/"

    def _safe(value: str) -> str:
        """Escape curly braces in user-supplied strings to prevent format-string injection."""
        return str(value).replace("{", "{{").replace("}", "}}")

    # Read adik.env.json if present.
    env_file = target / "adik.env.json"
    if env_file.exists():
        try:
            env = json.loads(env_file.read_text(encoding="utf-8"))
            if env.get("vectors", {}).get("storeUri"):
                vector_store = _safe(env["vectors"]["storeUri"])
        except (json.JSONDecodeError, KeyError):
            pass

    # Read adik.config.json if present.
    config_file = target / "adik.config.json"
    if config_file.exists():
        try:
            cfg = json.loads(config_file.read_text(encoding="utf-8"))
            languages = list(cfg.get("sdkLanguages", ["typescript", "python", "csharp"]))
            tier2 = cfg.get("tier2Languages", [])
            if tier2:
                languages += [f"{_safe(l)} (tier-2)" for l in tier2]
            sdk_languages = ", ".join(_safe(l) for l in languages)
            if cfg.get("registryPath"):
                registry_path = _safe(cfg["registryPath"])
            if cfg.get("includePatterns"):
                adik_reach = (
                    ", ".join(_safe(p) for p in cfg["includePatterns"])
                    + f" → {registry_path} → sdk/"
                )
        except (json.JSONDecodeError, KeyError):
            pass

    # Use partitioned index if present.
    if (target / "Registry.index.md").exists():
        registry_path = "Registry.index.md"

    return {
        "registry_path": registry_path,
        "sdk_languages": sdk_languages,
        "vector_store": vector_store,
        "project_summary": project_summary,
        "adik_reach": adik_reach,
    }


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


def _escape_braces(value):
    """Escape braces in strings so they are treated as literals by str.format."""
    if isinstance(value, str):
        return value.replace("{", "{{").replace("}", "}}")
    return value


def action_upsert(target: Path) -> None:
    """Insert or update the ADIK block in all three context files."""
    ctx = _gather_context(target)
    safe_ctx = {key: _escape_braces(val) for key, val in ctx.items()}

    files = {
        target / ".github" / "copilot-instructions.md": COPILOT_BLOCK.format(**safe_ctx),
        target / "CLAUDE.md": CLAUDE_BLOCK.format(**safe_ctx),
        target / "agents.md": AGENTS_BLOCK.format(**safe_ctx),
    }

    for path, block in files.items():
        existing = _read(path)
        updated = _upsert_block(existing, block)
        if updated != existing:
            _write(path, updated)
        else:
            print(f"  [up-to-date] {path}")


def action_remove(target: Path) -> None:
    """Remove the ADIK block from all three context files."""
    paths = [
        target / ".github" / "copilot-instructions.md",
        target / "CLAUDE.md",
        target / "agents.md",
    ]
    for path in paths:
        if not path.exists():
            continue
        existing = _read(path)
        updated = _remove_block(existing)
        if updated != existing:
            _write(path, updated)
        else:
            print(f"  [no block found] {path}")


def action_check(target: Path) -> None:
    """Check whether the ADIK block is present in all three context files."""
    paths = {
        ".github/copilot-instructions.md": target / ".github" / "copilot-instructions.md",
        "CLAUDE.md": target / "CLAUDE.md",
        "agents.md": target / "agents.md",
    }
    all_ok = True
    for label, path in paths.items():
        content = _read(path)
        if _has_block(content):
            print(f"  [OK]      {label}")
        else:
            print(f"  [MISSING] {label}")
            all_ok = False
    sys.exit(0 if all_ok else 1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministically manage ADIK self-embedding blocks."
    )
    parser.add_argument(
        "--action",
        choices=["upsert", "remove", "check"],
        required=True,
        help="upsert: insert/update block; remove: strip block; check: verify block present",
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Root directory of the target repository (default: current directory)",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"Error: target directory '{target}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"ADIK embed — action={args.action}, target={target}")

    if args.action == "upsert":
        action_upsert(target)
    elif args.action == "remove":
        action_remove(target)
    elif args.action == "check":
        action_check(target)


if __name__ == "__main__":
    main()
