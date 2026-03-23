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

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "adik-mcp-server",
    instructions=(
        "MCP server exposing ADIK SDK generation, registry query, "
        "and boilerplate scaffolding capabilities.  Version 1.0.0."
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
        if (candidate / "ADIK.md").exists() or (candidate / "Registry.md").exists():
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


def _get_all_symbols(root: Path) -> list[dict[str, str]]:
    """Load all symbols from all registry sections."""
    registry = _read_file(root / "Registry.md")
    if not registry:
        return []
    symbols = []
    for section_key in SECTION_MAP:
        section = _extract_section(registry, section_key)
        if section:
            symbols.extend(_parse_symbols_from_section(section))
    return symbols


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
def adik_get_registry(
    section: str = "all",
    filter: str = "",
) -> str:
    """Return the full contents of Registry.md or a filtered subset.

    Args:
        section: Which section to return. One of: all, endpoints, classes,
                 interfaces, schemas, enums, functions, errors, metadata.
        filter: Optional substring filter applied to symbol names.
    """
    root = _find_project_root()
    content = _read_file(root / "Registry.md")
    if not content:
        return "ERROR: Registry.md not found. Run the Codebase Analyst first."

    if section == "metadata":
        meta = _extract_metadata(content)
        return meta or "No metadata block found in Registry.md."

    if section != "all":
        extracted = _extract_section(content, section)
        if not extracted:
            return f"Section '{section}' not found or empty in Registry.md."
        if filter:
            lines = extracted.splitlines()
            filtered = [l for l in lines if filter.lower() in l.lower() or "ADIK:" in l or "---" in l or l.strip().startswith("|") and "ID" in l]
            return "\n".join(filtered) if filtered else f"No symbols matching '{filter}' in section '{section}'."
        return extracted

    # section == "all"
    if filter:
        lines = content.splitlines()
        filtered = [l for l in lines if filter.lower() in l.lower()]
        return "\n".join(filtered) if filtered else f"No lines matching '{filter}' in Registry.md."
    return content


@mcp.tool()
def adik_get_symbol(
    id: str = "",
    name: str = "",
) -> str:
    """Look up a specific symbol in the Registry by ID or name.

    Args:
        id: The unique registry ID (e.g. 'fn:getUserById').
        name: The symbol name. Used if id is not provided.
    """
    if not id and not name:
        return "ERROR: Provide either 'id' or 'name' to look up a symbol."

    root = _find_project_root()
    symbols = _get_all_symbols(root)
    if not symbols:
        return "ERROR: Registry.md not found or contains no symbols."

    search = id or name
    search_lower = search.lower()

    for sym in symbols:
        sym_id = sym.get("ID", "").lower()
        sym_name = sym.get("Name", sym.get("name", "")).lower()
        if search_lower in (sym_id, sym_name):
            return json.dumps(sym, indent=2)

    # Fuzzy match
    matches = []
    for sym in symbols:
        values = " ".join(str(v) for v in sym.values()).lower()
        if search_lower in values:
            matches.append(sym)

    if matches:
        return json.dumps(matches, indent=2)
    return f"No symbol found matching '{search}'."


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
def adik_validate_registry(
    strict: bool = False,
) -> str:
    """Run deterministic structural validation on Registry.md.

    Checks marker pairs, required metadata fields, unique IDs, valid kinds,
    and valid projectType. Returns a structured validation result.

    Args:
        strict: When true, warnings become errors.
    """
    root = _find_project_root()
    content = _read_file(root / "Registry.md")
    if not content:
        return json.dumps({"status": "FAIL", "errors": ["Registry.md not found."]})

    errors: list[str] = []
    warnings: list[str] = []

    # S-001: Marker pairs
    for section_key, marker in SECTION_MAP.items():
        start_tag = f"<!-- ADIK:{marker}:START -->"
        end_tag = f"<!-- ADIK:{marker}:END -->"
        has_start = start_tag in content
        has_end = end_tag in content
        if has_start != has_end:
            errors.append(f"S-001: Mismatched markers for {marker}.")

    # S-002: Required metadata
    meta = _extract_metadata(content)
    if meta:
        required = ["name", "version", "projectType", "sourceLanguage", "lastAnalysed", "lastAnalysedCommit"]
        for field in required:
            pattern = rf'^{field}:\s*".+"'
            if not re.search(pattern, meta, re.MULTILINE):
                # Check non-quoted values too
                pattern2 = rf"^{field}:\s+\S+"
                if not re.search(pattern2, meta, re.MULTILINE):
                    errors.append(f"S-002: Required metadata field '{field}' missing or empty.")
    else:
        errors.append("S-002: No YAML metadata block found in Registry.md.")

    # S-004: Unique symbol IDs
    symbols = _get_all_symbols(root)
    ids = [s.get("ID", "") for s in symbols if s.get("ID")]
    seen: set[str] = set()
    for sym_id in ids:
        if sym_id in seen:
            errors.append(f"S-004: Duplicate symbol ID '{sym_id}'.")
        seen.add(sym_id)

    # S-005: Valid kind values
    valid_kinds = {"function", "class", "interface", "enum", "schema", "endpoint", "type"}
    for sym in symbols:
        kind = sym.get("Kind", sym.get("kind", "")).lower().strip()
        if kind and kind not in valid_kinds:
            errors.append(f"S-005: Invalid kind '{kind}' on symbol '{sym.get('ID', '?')}'.")

    # S-006: Valid projectType
    if meta:
        pt_match = re.search(r'projectType:\s*"?(\w+)"?', meta)
        if pt_match:
            pt = pt_match.group(1)
            if pt not in ("api", "service", "library"):
                errors.append(f"S-006: Invalid projectType '{pt}'. Must be api, service, or library.")

    # P-001: Empty descriptions (warning)
    for sym in symbols:
        desc = sym.get("Description", sym.get("description", "")).strip()
        if not desc or len(desc.split()) <= 1:
            w = f"P-001: Symbol '{sym.get('ID', sym.get('Name', '?'))}' has empty or single-word description."
            warnings.append(w)

    if strict:
        errors.extend(warnings)
        warnings = []

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return json.dumps({
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "symbolCount": len(symbols),
    }, indent=2)


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
    target = root / file
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
        remove_sdk: If true, also remove the sdk/ directory.
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
    """Return a summary of the current ADIK project state.

    Reports: project root, registry presence, symbol count, SDK directories,
    last build info, config, and environment state.
    """
    root = _find_project_root()
    info: dict[str, Any] = {"projectRoot": str(root)}

    # Registry
    reg = _read_file(root / "Registry.md")
    if reg:
        info["registryFound"] = True
        meta = _extract_metadata(reg)
        if meta:
            for field in ["name", "version", "projectType", "sourceLanguage", "lastAnalysed"]:
                m = re.search(rf'{field}:\s*"?([^"\n]+)"?', meta)
                if m:
                    info[field] = m.group(1).strip()
        symbols = _get_all_symbols(root)
        info["symbolCount"] = len(symbols)
    else:
        info["registryFound"] = False
        info["symbolCount"] = 0

    # Partitioned?
    info["partitioned"] = (root / "Registry.index.md").exists()

    # SDK directories
    sdk_dir = root / "sdk"
    if sdk_dir.exists():
        langs = [d.name for d in sdk_dir.iterdir() if d.is_dir()]
        info["sdkLanguages"] = langs
        info["buildReportExists"] = (sdk_dir / "BUILD_REPORT.md").exists()
        info["validationReportExists"] = (sdk_dir / "VALIDATION_REPORT.md").exists()
    else:
        info["sdkLanguages"] = []
        info["buildReportExists"] = False
        info["validationReportExists"] = False

    # Config
    info["configExists"] = (root / "adik.config.json").exists()
    info["envExists"] = (root / "adik.env.json").exists()
    info["auditLogExists"] = (root / "adik.audit.log").exists()

    # Audit log last entry
    audit_path = root / "adik.audit.log"
    if audit_path.exists():
        lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
        if lines:
            try:
                last = json.loads(lines[-1])
                info["lastBuild"] = {
                    "timestamp": last.get("timestamp"),
                    "exitStatus": last.get("exitStatus"),
                    "commitSha": last.get("commitSha", "")[:8],
                }
            except json.JSONDecodeError:
                info["lastBuild"] = None

    # Embedding status
    for ctx_file in [".github/copilot-instructions.md", "CLAUDE.md", "agents.md"]:
        p = root / ctx_file
        if p.exists():
            content = p.read_text(encoding="utf-8")
            info[f"embedded_{ctx_file.replace('/', '_').replace('.', '_')}"] = ADIK_START in content
        else:
            info[f"embedded_{ctx_file.replace('/', '_').replace('.', '_')}"] = False

    return json.dumps(info, indent=2)


# ---------------------------------------------------------------------------
# LLM-DEPENDENT TOOLS — return instruction payloads for the calling LLM
# ---------------------------------------------------------------------------


@mcp.tool()
def adik_build_sdk(
    languages: list[str] | None = None,
    incremental: bool = False,
    output_dir: str = "./sdk",
) -> str:
    """Trigger SDK generation. Returns a structured instruction payload that
    the calling LLM should execute by loading the Builder Agent.

    This tool cannot generate code autonomously — it assembles the context and
    instructions that the LLM should follow to produce the SDK.

    Args:
        languages: Target languages (default: from config).
        incremental: If true, only regenerate changed symbols.
        output_dir: Override the output directory.
    """
    root = _find_project_root()
    config = _load_config(root)
    langs = languages or config.get("sdkLanguages", ["typescript", "python", "csharp"])

    # Pre-flight: validate registry first
    reg = _read_file(root / "Registry.md")
    if not reg:
        return json.dumps({
            "status": "BLOCKED",
            "reason": "Registry.md not found. Run adik_analyse_codebase first.",
        })

    symbols = _get_all_symbols(root)
    if not symbols:
        return json.dumps({
            "status": "BLOCKED",
            "reason": "Registry.md is empty. Run adik_analyse_codebase first.",
        })

    return json.dumps({
        "status": "READY",
        "action": "build_sdk",
        "instruction": (
            "Load agents/builder.agent.md and execute its full protocol. "
            "The registry is populated and ready."
        ),
        "context": {
            "registryPath": "Registry.md",
            "languages": langs,
            "incremental": incremental,
            "outputDir": output_dir,
            "projectType": config.get("projectType", "auto"),
            "symbolCount": len(symbols),
            "tier2Languages": config.get("tier2Languages", []),
        },
        "agentFile": "agents/builder.agent.md",
        "skillFiles": [
            "skills/registry-validator.skill.md",
            "skills/sdk-builder.skill.md",
            "skills/sdk-consumer.skill.md",
        ] + (["skills/sdk-builder-tier2.skill.md"] if config.get("tier2Languages") else []),
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
            "Scan the target directory, discover all public symbols, and populate Registry.md."
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
            ["skills/vectorize.skill.md"] if env.get("vectorMode") == "active" else []
        ),
    }, indent=2)


@mcp.tool()
def adik_scaffold_boilerplate(
    language: str = "typescript",
    framework: str = "",
    symbols: list[str] | None = None,
) -> str:
    """Trigger boilerplate generation. Returns a structured instruction payload
    that the calling LLM should execute by loading the SDK Consumer Skill.

    Args:
        language: Target language (typescript, python, or csharp).
        framework: Framework hint (e.g. react, nestjs, fastapi, aspnet).
        symbols: Optional list of symbol IDs to generate for.
    """
    root = _find_project_root()
    config = _load_config(root)
    env = _load_env(root)

    reg = _read_file(root / "Registry.md")
    if not reg:
        return json.dumps({
            "status": "BLOCKED",
            "reason": "Registry.md not found. Run adik_analyse_codebase first.",
        })

    framework_hints = [framework] if framework else env.get("frameworkHints", [])

    return json.dumps({
        "status": "READY",
        "action": "scaffold_boilerplate",
        "instruction": (
            "Load skills/sdk-consumer.skill.md and execute its generation protocol "
            f"for {language}. Generate examples, DI wiring, retry wrappers, and "
            "serialization helpers."
        ),
        "context": {
            "language": language,
            "frameworkHints": framework_hints,
            "symbols": symbols or "all",
            "outputDir": config.get("outputDir", "./sdk"),
        },
        "skillFiles": ["skills/sdk-consumer.skill.md"],
    }, indent=2)


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
            "The vectorize skill (skills/vectorize.skill.md) defines the protocol."
        ),
        "query": query,
        "scope": scope,
        "topK": top_k,
    })


# ---------------------------------------------------------------------------
# Resources — expose key files as MCP resources
# ---------------------------------------------------------------------------

@mcp.resource("adik://registry")
def resource_registry() -> str:
    """The full Registry.md contents."""
    root = _find_project_root()
    return _read_file(root / "Registry.md") or "Registry.md not found."


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
        mcp.run(transport="streamable-http", host="127.0.0.1", port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
