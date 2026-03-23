#!/usr/bin/env python3
"""
adik-deploy.py — ADIK Bundle Assembly and Deployment Script

Assembles the adik bundle from the ADIK source repository and deploys it to a
target directory or repository. This is the operational tool invoked by
ADIKbuilder.md to produce a deployable adik.

The script:
  1. Validates that all required bundle files exist in the source repo.
  2. Copies only the bundle files to the target (never ADIKbuilder.md or docs/).
  3. Optionally runs adik-embed.py in the target to set up context files.
  4. Reports what was deployed.

Usage:
    # Deploy adik bundle to a target directory
    python3 scripts/adik-deploy.py --source . --target /path/to/target-repo

    # Deploy and run self-embedding in the target
    python3 scripts/adik-deploy.py --source . --target /path/to/target-repo --embed

    # Dry-run: show what would be deployed without writing anything
    python3 scripts/adik-deploy.py --source . --target /path/to/target-repo --dry-run

    # Deploy to a new distribution repository (bundle-only, no embedding)
    python3 scripts/adik-deploy.py --source . --target /path/to/dist-repo --dist

Environment variables:
    ADIK_DEPLOY_EMBED=true    Equivalent to --embed (run self-embedding after deploy)
    ADIK_DEPLOY_FORCE=true    Overwrite existing adik files in target without prompting
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Bundle manifest — files and directories included in every adik
# ---------------------------------------------------------------------------

BUNDLE_FILES = [
    "ADIK.md",
    "ADIK.orchestrator.md",
    "Registry.md",
    "Registry.index.md",
]

BUNDLE_DIRS = [
    "agents",
    "skills",
    "scripts",
    "mcp",
]

# Files that are NEVER deployed (source-repo only)
EXCLUDED_FILES = [
    "ADIKbuilder.md",
    "CLAUDE.md",
    "agents.md",
    "CHANGELOG.md",
    "ROADMAP.md",
    "README.md",
    "README.pypi.md",
    "LICENSE",
    "adik-lint.py",
    "mkdocs.yml",
    "requirements-docs.txt",
    "pyproject.toml",
    "measure_bundle.py",
]

EXCLUDED_DIRS = [
    "docs",
    ".github",
    ".git",
    "__pycache__",
    "node_modules",
    "vectors",
    "dist",
    "build",
]

# Files within bundle directories that should NOT be deployed
EXCLUDED_FROM_SCRIPTS = [
    "adik-deploy.py",  # factory-side only; not part of the adik
]

# ADIK-owned paths that are not considered target project source.
ADIK_OWNED_DIRS = {
    "agents",
    "skills",
    "scripts",
    "mcp",
    "sdk",
    ".github",
    "__pycache__",
    ".git",
    "node_modules",
    "vectors",
}

ADIK_OWNED_FILES = set(BUNDLE_FILES) | {
    "ADIKbuilder.md",
    "agents.md",
    "CLAUDE.md",
    "adik.env.json",
    "adik.audit.log",
    "adik.config.json",
}

SOURCE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".cs", ".go", ".java", ".kt", ".kts",
}

SOURCE_MANIFESTS = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Cargo.toml",
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_source(source: Path) -> Tuple[bool, List[str]]:
    """Validate that all required bundle files exist in the source repo."""
    errors = []

    for f in BUNDLE_FILES:
        if not (source / f).is_file():
            errors.append(f"Missing required file: {f}")

    for d in BUNDLE_DIRS:
        if not (source / d).is_dir():
            errors.append(f"Missing required directory: {d}/")

    # Check key files within directories
    key_files = [
        "agents/builder.agent.md",
        "agents/codebase-analyst.agent.md",
        "skills/sdk-builder.skill.md",
        "skills/sdk-consumer.skill.md",
        "skills/registry-validator.skill.md",
        "skills/vectorize.skill.md",
        "scripts/adik-embed.py",
        "scripts/adik-eject.py",
        "mcp/adik-mcp-server.md",
        "mcp/adik_mcp_server.py",
    ]
    for f in key_files:
        if not (source / f).is_file():
            errors.append(f"Missing key bundle file: {f}")

    return len(errors) == 0, errors


def check_target_conflicts(target: Path) -> List[str]:
    """Check if target already has adik files (potential overwrite)."""
    conflicts = []
    for f in BUNDLE_FILES:
        if (target / f).is_file():
            conflicts.append(f)
    for d in BUNDLE_DIRS:
        if (target / d).is_dir():
            conflicts.append(f"{d}/")
    return conflicts


def has_user_source_files(target: Path) -> bool:
    """
    Detect whether the target appears to contain user project source code.

    This excludes ADIK-owned files and directories so we can warn when users
    deploy into an empty folder and expect SDK code generation immediately.
    """
    if not target.exists() or not target.is_dir():
        return False

    for root, dirs, files in os.walk(str(target)):
        root_path = Path(root)
        rel_parts = root_path.relative_to(target).parts

        if any(part in ADIK_OWNED_DIRS for part in rel_parts):
            dirs[:] = []
            continue

        dirs[:] = [sub for sub in dirs if sub not in ADIK_OWNED_DIRS and not sub.startswith('.')]

        for fname in files:
            if fname in ADIK_OWNED_FILES:
                continue

            suffix = Path(fname).suffix.lower()
            if suffix in SOURCE_EXTENSIONS or fname in SOURCE_MANIFESTS:
                return True

    return False


# ---------------------------------------------------------------------------
# Deployment
# ---------------------------------------------------------------------------

def deploy_bundle(source: Path, target: Path, dry_run: bool = False,
                  is_dist: bool = False) -> List[str]:
    """
    Copy the adik bundle from source to target.

    Args:
        source:   Path to the ADIK source repository root.
        target:   Path to the target directory.
        dry_run:  If True, report what would be copied without writing.
        is_dist:  If True, deploying to a distribution repo (skip adik-deploy.py
                  from scripts/).

    Returns:
        List of deployed file paths (relative to target).
    """
    deployed = []

    # Copy individual bundle files
    for f in BUNDLE_FILES:
        src = source / f
        dst = target / f
        if src.is_file():
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
            deployed.append(f)

    # Copy bundle directories
    for d in BUNDLE_DIRS:
        src_dir = source / d
        dst_dir = target / d
        if src_dir.is_dir():
            for root, dirs, files in os.walk(str(src_dir)):
                root_path = Path(root)
                rel_root = root_path.relative_to(source)

                # Skip excluded subdirectories
                dirs[:] = [
                    sub for sub in dirs
                    if sub not in ("__pycache__", ".git", "node_modules")
                    and not sub.endswith(".egg-info")
                ]

                for fname in files:
                    # Skip factory-only files
                    if fname in EXCLUDED_FROM_SCRIPTS:
                        continue

                    rel_file = rel_root / fname
                    src_file = source / rel_file
                    dst_file = target / rel_file

                    if not dry_run:
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(src_file), str(dst_file))
                    deployed.append(str(rel_file))

    return deployed


def run_embed(target: Path) -> bool:
    """Run adik-embed.py in the target to set up context files."""
    embed_script = target / "scripts" / "adik-embed.py"
    if not embed_script.is_file():
        print("  ⚠  adik-embed.py not found in target — skipping embedding")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(embed_script), "--action", "upsert", "--target", str(target)],
            capture_output=True, text=True, cwd=str(target)
        )
        if result.returncode == 0:
            print("  ✓  Self-embedding completed successfully")
            return True
        else:
            print(f"  ✗  Self-embedding failed (exit {result.returncode})")
            if result.stderr:
                print(f"     {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  ✗  Self-embedding error: {e}")
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Assemble and deploy an adik bundle from the ADIK source repository."
    )
    parser.add_argument(
        "--source", type=str, default=".",
        help="Path to the ADIK source repository root (default: current directory)"
    )
    parser.add_argument(
        "--target", type=str, required=True,
        help="Path to the target directory where the adik will be deployed"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be deployed without writing anything"
    )
    parser.add_argument(
        "--embed", action="store_true",
        help="Run adik-embed.py in the target after deployment"
    )
    parser.add_argument(
        "--dist", action="store_true",
        help="Deploy as a distribution bundle (excludes factory-only files)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing adik files in target without prompting"
    )

    args = parser.parse_args()

    # Env var overrides
    if os.environ.get("ADIK_DEPLOY_EMBED", "").lower() == "true":
        args.embed = True
    if os.environ.get("ADIK_DEPLOY_FORCE", "").lower() == "true":
        args.force = True

    source = Path(args.source).resolve()
    target = Path(args.target).resolve()

    print(f"ADIK Bundle Deployment")
    print(f"  Source: {source}")
    print(f"  Target: {target}")
    if args.dry_run:
        print(f"  Mode:   DRY RUN (no files will be written)")
    print()

    # --- Step 1: Validate source ---
    valid, errors = validate_source(source)
    if not valid:
        print("✗ Source validation failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print(f"✓ Source validated — all {len(BUNDLE_FILES)} files and {len(BUNDLE_DIRS)} directories present")

    # --- Step 2: Check target conflicts ---
    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    conflicts = check_target_conflicts(target)
    if conflicts and not args.force and not args.dry_run:
        print(f"\n⚠  Target already contains {len(conflicts)} adik file(s):")
        for c in conflicts[:10]:
            print(f"   - {c}")
        if len(conflicts) > 10:
            print(f"   ... and {len(conflicts) - 10} more")
        print()

        # Check for interactive terminal
        if sys.stdin.isatty():
            answer = input("Overwrite existing files? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                print("Aborted.")
                sys.exit(0)
        else:
            print("Use --force to overwrite in non-interactive mode.")
            sys.exit(1)

    # --- Step 3: Deploy ---
    deployed = deploy_bundle(source, target, dry_run=args.dry_run, is_dist=args.dist)

    if args.dry_run:
        print(f"\nWould deploy {len(deployed)} files:")
    else:
        print(f"\n✓ Deployed {len(deployed)} files:")

    for f in sorted(deployed):
        prefix = "  → " if not args.dry_run else "    "
        print(f"{prefix}{f}")

    # --- Step 4: Optional embedding ---
    if args.embed and not args.dry_run:
        print()
        run_embed(target)

    # --- Step 5: Summary ---
    print()
    if args.dry_run:
        print("Dry run complete. No files were written.")
    else:
        print(f"✓ adik bundle deployed to {target}")
        if not args.embed:
            print("  Tip: run with --embed to also set up context files (.github/copilot-instructions.md, CLAUDE.md, agents.md)")
        if not has_user_source_files(target):
            print("  ⚠  No user source files were detected in the target project.")
            print("     ADIK deployment only installs framework artifacts.")
            print("     SDK code is generated after running ADIK.orchestrator.md against an existing codebase.")
        print()
        print("Next steps:")
        print("  1. Open the target repository in your agentic environment")
        print("  2. Load ADIK.orchestrator.md — it will guide you through first-run setup")
        print("  3. The orchestrator will auto-detect your project and begin SDK generation")


if __name__ == "__main__":
    main()
