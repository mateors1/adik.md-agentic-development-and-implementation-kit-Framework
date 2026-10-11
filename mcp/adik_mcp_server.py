#!/usr/bin/env python3
"""
adik_mcp_server.py — ADIK MCP Server

Exposes ADIK capabilities as Model Context Protocol tools so any MCP-compatible
agentic environment can drive the ADIK pipeline via natural language.

Deterministic tools (registry read, symbol lookup, build report, validate,
lint, embed, eject, status) are fully implemented.

LLM-dependent tools (build_sdk, analyse_codebase, scaffold_boilerplate) return
structured instruction payloads that the calling LLM should execute — they
cannot run autonomously without an LLM backend.

Transport: stdio (default) or streamable-http via --transport flag.

Usage:
    # stdio (for Copilot, Claude Desktop, Cursor, etc.)
    python mcp/adik_mcp_server.py

    # streamable-http on port 3100
    python mcp/adik_mcp_server.py --transport http --port 3100
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from adik_contracts import ContractError, load_registry, resolve_registry, registry_report, validate_bundle, validate_registry, relative_path

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "adik-mcp-server",
    instructions=(
        "MCP server exposing ADIK SDK generation, registry query, "
        "and boilerplate scaffolding capabilities.  Version 2.0.0."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SECTION_MAP = {
    "endpoints": "ENDPOINTS",
    "classes": "CLASSES",
    "interfaces": "INTERFACES",
    "schemas": "SCHEMAS",
    "enums": "ENUMS",
    "functions": "FUNCTIONS",
    "errors": "ERRORS",
}

ADIK_START = "<!-- ADIK:START -->"
ADIK_END = "<!-- ADIK:END -->"


def _find_project_root() -> Path:
    """Walk up from CWD to find a directory containing ADIK.md or Registry.md."""
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        if any((candidate / name).exists() for name in ("ADIK.md", "Registry.md", "adik.manifest.json", ".adik")):
            return candidate
    return cwd


def _read_file(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def _extract_section(content: str, section_key: str) -> str | None:
    """Extract content between ADIK:<SECTION>:START and ADIK:<SECTION>:END."""
    marker = SECTION_MAP.get(section_key)
    if not marker:
        return None
    start_tag = f"<!-- ADIK:{marker}:START -->"
    end_tag = f"<!-- ADIK:{marker}:END -->"
    start = content.find(start_tag)
    end = content.find(end_tag)
    if start == -1 or end == -1:
        return None
    return content[start: end + len(end_tag)]


def _extract_metadata(content: str) -> str | None:
    """Extract the YAML metadata block from Registry.md."""
    match = re.search(r"```yaml\n(.*?)```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _parse_symbols_from_section(section_content: str) -> list[dict[str, str]]:
    """Parse pipe-separated table rows into dicts with at least id and name."""
    rows = []
    lines = section_content.strip().splitlines()
    header_line = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "---" not in stripped and "ADIK:" not in stripped:
            if header_line is None:
                header_line = [c.strip() for c in stripped.strip("|").split("|")]
            else:
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if len(cells) >= len(header_line):
                    row = dict(zip(header_line, cells))
                    rows.append(row)
    return rows


def _get_all_symbols(root: Path) -> list[dict]:
    data = load_registry(root)
    errors = validate_registry(data)
    if errors:
        raise ContractError("; ".join(errors))
    return data["symbols"]


def _load_config(root: Path) -> dict[str, Any]:
    """Load adik.config.json or return defaults."""
    config_path = root / "adik.config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {
        "sdkLanguages": ["typescript", "python", "csharp"],
        "tier2Languages": [],
        "outputDir": "./sdk",
        "projectType": "auto",
    }


def _load_env(root: Path) -> dict[str, Any]:
    """Load adik.env.json or return defaults."""
    env_path = root / "adik.env.json"
    if env_path.exists():
        return json.loads(env_path.read_text(encoding="utf-8"))
    return {}


# ---------------------------------------------------------------------------
# DETERMINISTIC TOOLS — fully implemented, no LLM needed
# ---------------------------------------------------------------------------


@mcp.tool()
def adik_get_registry(section: str = "all", filter: str = "") -> str:
    """Read canonical symbols from the producer registry or a completed adik."""
    try:
        data = load_registry(_find_project_root())
        errors = validate_registry(data)
        if errors:
            raise ContractError("; ".join(errors))
        if section == "metadata":
            return json.dumps(data["metadata"], indent=2, default=str)
        kinds = {"endpoints": "endpoint", "classes": "class", "interfaces": "interface",
                 "schemas": "schema", "enums": "enum", "functions": "function", "errors": "type"}
        if section != "all" and section not in kinds:
            raise ContractError(f"Unknown section: {section}")
        symbols = data["symbols"]
        if section != "all":
            symbols = [s for s in symbols if s.get("kind") == kinds[section]]
        if filter:
            symbols = [s for s in symbols if filter.lower() in json.dumps(s).lower()]
        return json.dumps({**data, "symbols": symbols}, indent=2, default=str)
    except (ContractError, OSError) as exc:
        return json.dumps({"status": "FAIL", "errors": [str(exc)]})


@mcp.tool()
def adik_get_symbol(id: str = "", name: str = "") -> str:
    """Read a declared SDK symbol by exact ID or name."""
    if not id and not name:
        return json.dumps({"status": "FAIL", "errors": ["Provide id or name"]})
    try:
        symbols = _get_all_symbols(_find_project_root())
        matches = [s for s in symbols if s.get("id") == id] if id else [s for s in symbols if s.get("name") == name]
        return json.dumps(matches[0] if len(matches) == 1 else matches, indent=2)
    except (ContractError, OSError) as exc:
        return json.dumps({"status": "FAIL", "errors": [str(exc)]})


@mcp.tool()
def adik_get_build_report(
    language: str = "",
) -> str:
    """Return the most recent sdk/BUILD_REPORT.md.

    Args:
        language: Optional filter to a single language section.
    """
    root = _find_project_root()
    report = _read_file(root / "sdk" / "BUILD_REPORT.md")
    if not report:
        return "No BUILD_REPORT.md found. Run the Builder Agent first."

    if language:
        # Extract the section for this language
        pattern = re.compile(
            rf"(##\s+.*{re.escape(language)}.*?\n)(.*?)(?=\n## |\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(report)
        if match:
            return match.group(0)
        return f"No section for '{language}' in BUILD_REPORT.md."
    return report


@mcp.tool()
def adik_validate_registry(strict: bool = False) -> str:
    """Validate the same JSON or legacy Markdown contract used by build preparation."""
    return json.dumps(registry_report(_find_project_root(), strict), indent=2)


@mcp.tool()
def adik_lint(
    file: str = "ADIK.md",
) -> str:
    """Run the ADIK specification linter on a file.

    Args:
        file: Path to the file to lint (default: ADIK.md).
    """
    root = _find_project_root()
    lint_script = root / "adik-lint.py"
    target = relative_path(root, file)
    if not lint_script.exists():
        return "ERROR: adik-lint.py not found in project root."
    if not target.exists():
        return f"ERROR: {file} not found."

    result = subprocess.run(
        [sys.executable, str(lint_script), str(target)],
        capture_output=True,
        text=True,
        cwd=str(root),
        timeout=30,
    )
    output = result.stdout.strip()
    if result.returncode == 0:
        return output or "All checks passed."
    return f"Lint failed (exit {result.returncode}):\n{output}\n{result.stderr.strip()}"


@mcp.tool()
def adik_embed(
    action: str = "check",
    target: str = ".",
) -> str:
    """Run the ADIK self-embedding script.

    Args:
        action: One of 'upsert', 'remove', or 'check'.
        target: Target directory (default: current project root).
    """
    if action not in ("upsert", "remove", "check"):
        return "ERROR: action must be 'upsert', 'remove', or 'check'."

    root = _find_project_root()
    script = root / "scripts" / "adik-embed.py"
    if not script.exists():
        return "ERROR: scripts/adik-embed.py not found."

    target_path = root / target if target != "." else root
    result = subprocess.run(
        [sys.executable, str(script), "--action", action, "--target", str(target_path)],
        capture_output=True,
        text=True,
        cwd=str(root),
        timeout=30,
    )
    return result.stdout.strip() or result.stderr.strip() or f"Embed {action} completed."


@mcp.tool()
def adik_eject(
    dry_run: bool = True,
    remove_sdk: bool = False,
) -> str:
    """Run the ADIK eject script. Defaults to dry-run for safety.

    Args:
        dry_run: If true (default), show what would be removed without removing.
        remove_sdk: Legacy compatibility flag. Generated SDK files are preserved.
    """
    root = _find_project_root()
    script = root / "scripts" / "adik-eject.py"
    if not script.exists():
        return "ERROR: scripts/adik-eject.py not found."

    args = [sys.executable, str(script), "--target", str(root)]
    if dry_run:
        args.append("--dry-run")
    else:
        args.append("--confirm")
    if remove_sdk:
        args.append("--remove-sdk")

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(root),
        timeout=30,
    )
    return result.stdout.strip() or result.stderr.strip() or "Eject completed."


@mcp.tool()
def adik_status() -> str:
    """Report producer registry health and installed consumer adiks."""
    root = _find_project_root()
    info = {"projectRoot": str(root), "registry": registry_report(root),
            "completedBundle": (root / "adik.manifest.json").is_file(),
            "installedAdiks": []}
    for receipt in sorted((root / ".adik/.receipts").glob("*.json")):
        try:
            item = json.loads(receipt.read_text())
            if not isinstance(item, dict):
                raise ValueError("Invalid receipt")
            info["installedAdiks"].append({k: item.get(k) for k in ("id", "version", "client")})
        except (ValueError, OSError):
            info["installedAdiks"].append({"error": f"Unreadable receipt {receipt.name}"})
    return json.dumps(info, indent=2)


# ---------------------------------------------------------------------------
# LLM-DEPENDENT TOOLS — return instruction payloads for the calling LLM
# ---------------------------------------------------------------------------


@mcp.tool()
def adik_build_sdk(languages: list[str] | None = None, incremental: bool = False,
                   output_dir: str = "") -> str:
    """Prepare producer instructions to generate SDK code AND matching agentic elements."""
    root = _find_project_root()
    validation = registry_report(root)
    if validation["status"] == "FAIL":
        return json.dumps({"status": "BLOCKED", "validation": validation}, indent=2)
    config = _load_config(root)
    return json.dumps({
        "status": "READY", "action": "build_adik", "validation": validation,
        "instruction": "Read skills/build-adik/SKILL.md. Generate actual SDK source code, matching implementation skills, references, and examples. Validate and package one completed adik. The host agent executes this work.",
        "context": {"registryPath": str(resolve_registry(root).relative_to(root)),
                    "languages": languages or config.get("sdkLanguages", ["typescript", "python", "csharp"]),
                    "incremental": incremental, "outputDir": output_dir or config.get("outputDir", "generated/adik"),
                    "consumerFrameworks": config.get("consumerFrameworks", []),
                    "tier2Languages": config.get("tier2Languages", [])},
        "skillFiles": ["skills/build-adik/SKILL.md", "skills/sdk-builder/SKILL.md", "skills/sdk-consumer/SKILL.md"]
    }, indent=2)


@mcp.tool()
def adik_analyse_codebase(
    since: str = "",
    target: str = "./src",
) -> str:
    """Trigger codebase analysis. Returns a structured instruction payload that
    the calling LLM should execute by loading the Codebase Analyst Agent.

    Args:
        since: Git commit SHA for incremental analysis.
        target: Source directory to scan (default: ./src).
    """
    root = _find_project_root()
    config = _load_config(root)
    env = _load_env(root)

    # Check if target directory exists
    target_path = root / target
    has_source = target_path.exists() and any(target_path.rglob("*"))

    if not has_source:
        return json.dumps({
            "status": "BLOCKED",
            "reason": f"Source directory '{target}' not found or empty. "
                      "ADIK generates SDKs from existing source code.",
        })

    return json.dumps({
        "status": "READY",
        "action": "analyse_codebase",
        "instruction": (
            "Load agents/codebase-analyst.agent.md and execute its full protocol. "
            "Scan the target directory, discover public symbols, and populate the configured registry. Prefer contracts/registry.json for new producers."
        ),
        "context": {
            "target": target,
            "since": since or None,
            "incremental": bool(since),
            "includePatterns": config.get("includePatterns", ["src/**/*"]),
            "excludePatterns": config.get("excludePatterns", ["**/*.test.*"]),
            "vectorMode": env.get("vectorMode", "inactive"),
        },
        "agentFile": "agents/codebase-analyst.agent.md",
        "skillFiles": (
            ["skills/vectorize/SKILL.md"] if env.get("vectorMode") == "active" else []
        ),
    }, indent=2)


@mcp.tool()
def adik_scaffold_boilerplate(language: str = "typescript", framework: str = "",
                             symbols: list[str] | None = None) -> str:
    """Prepare producer instructions for implementation skills and runnable examples."""
    root = _find_project_root()
    validation = registry_report(root)
    if validation["status"] == "FAIL":
        return json.dumps({"status": "BLOCKED", "validation": validation})
    config = _load_config(root)
    return json.dumps({"status": "READY", "action": "build_implementation_kit",
        "instruction": "Read skills/sdk-consumer/SKILL.md and generate implementation skills for the actual SDK, including references and runnable examples.",
        "context": {"language": language, "consumerFrameworks": [framework] if framework else config.get("consumerFrameworks", []),
                    "symbols": symbols or "all", "outputDir": config.get("outputDir", "generated/adik")},
        "skillFiles": ["skills/sdk-consumer/SKILL.md"]}, indent=2)


@mcp.tool()
def adik_vector_search(
    query: str = "",
    scope: str = "all",
    top_k: int = 10,
) -> str:
    """Semantic similarity search over vectorized Registry and codebase.
    Only available when vector mode is active.

    Args:
        query: Natural language or code fragment to search for.
        scope: Search scope — registry, codebase, or all.
        top_k: Maximum number of results.
    """
    root = _find_project_root()
    env = _load_env(root)

    if env.get("vectorMode") != "active":
        return json.dumps({
            "status": "UNAVAILABLE",
            "reason": (
                "Vector search is not available. Ensure a vector database is "
                "configured (via VECTOR_DB_URL or adik.config.json vectors.storeUri) "
                "or that bundled vectors are present in the vectors/ directory."
            ),
        })

    # When vector mode IS active, this would query the vector store.
    # Placeholder until vector store integration is implemented.
    return json.dumps({
        "status": "NOT_IMPLEMENTED",
        "reason": (
            "Vector store integration is not yet implemented in the MCP server. "
            "The vectorize skill (skills/vectorize/SKILL.md) defines the protocol."
        ),
        "query": query,
        "scope": scope,
        "topK": top_k,
    })


# ---------------------------------------------------------------------------
# Resources — expose key files as MCP resources
# ---------------------------------------------------------------------------


@mcp.tool()
def adik_implement(bundle: str, capability: str = "") -> str:
    """Prepare a consumer implementation handoff from a validated completed adik."""
    try:
        root = _find_project_root()
        bundle_root = relative_path(root, bundle)
        manifest = validate_bundle(bundle_root)
        return json.dumps({"status": "READY", "action": "implement_adik",
            "bundleId": manifest["id"], "version": manifest["version"], "capability": capability,
            "instruction": "Load the matching bundled implementation skill. Use its SDK contracts and examples, inspect application integration points, implement the user's request, and run the documented checks.",
            "skillFiles": [str((bundle_root / s["path"]).relative_to(root)) for s in manifest["implementationSkills"]]}, indent=2)
    except (ContractError, OSError) as exc:
        return json.dumps({"status": "BLOCKED", "reason": str(exc)})

@mcp.resource("adik://registry")
def resource_registry() -> str:
    """The normalized producer or completed-adik registry."""
    return adik_get_registry()


@mcp.resource("adik://config")
def resource_config() -> str:
    """The adik.config.json contents."""
    root = _find_project_root()
    content = _read_file(root / "adik.config.json")
    return content or "{}"


@mcp.resource("adik://env")
def resource_env() -> str:
    """The adik.env.json contents."""
    root = _find_project_root()
    content = _read_file(root / "adik.env.json")
    return content or "{}"


@mcp.resource("adik://orchestrator")
def resource_orchestrator() -> str:
    """The ADIK.orchestrator.md contents."""
    root = _find_project_root()
    return _read_file(root / "ADIK.orchestrator.md") or "ADIK.orchestrator.md not found."


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point — invoked by `adik-mcp-server` console script or `python -m adik_mcp_server`."""
    import argparse

    parser = argparse.ArgumentParser(description="ADIK MCP Server")
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--port", type=int, default=3100,
        help="Port for HTTP transport (default: 3100)",
    )
    args = parser.parse_args()

    if args.transport == "http":
        mcp.settings.host = "127.0.0.1"
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
