#!/usr/bin/env python3
"""Seal, validate, pack, register, and remove a completed adik. Generation belongs to the host agent."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp"))
from adik_contracts import (ContractError, digest, payload_files, read_json,
                            relative_path, skill_metadata, validate_bundle)

CLIENTS = {"codex": (".agents/skills", "AGENTS.md"),
           "claude": (".claude/skills", "CLAUDE.md"),
           "copilot": (".github/skills", ".github/copilot-instructions.md")}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def seal(root: Path) -> dict:
    manifest = validate_bundle(root, verify_hashes=False)
    manifest["files"] = payload_files(root)
    write_json(root / "adik.manifest.json", manifest)
    return validate_bundle(root)


def pack(root: Path, output: Path) -> None:
    manifest = validate_bundle(root)
    if output.resolve().is_relative_to(root.resolve()):
        raise ContractError("Archive output must be outside the bundle")
    if output.exists():
        raise ContractError(f"Archive already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Fixed timestamps and sorted paths make identical sealed inputs reproducible.
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(["adik.manifest.json", *manifest["files"]]):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, relative_path(root, name).read_bytes())


def install(root: Path, target: Path, client: str) -> dict:
    manifest = validate_bundle(root)
    bid = manifest["id"]
    bundle_name = f".adik/{bid}"
    bundle_path = relative_path(target, bundle_name)
    receipt_path = relative_path(target, f".adik/.receipts/{bid}.json")
    if receipt_path.exists():
        receipt = read_json(receipt_path)
        if receipt.get("id") == bid and receipt.get("manifestHash") == digest(root / "adik.manifest.json") and receipt.get("client") == client:
            _check_receipt(target, receipt)
            return receipt
        raise ContractError("A different version or client is installed; remove the previous registration first")
    if bundle_path.exists():
        raise ContractError(f"Refusing to overwrite unowned bundle: {bundle_name}")
    skill_dir, context_name = CLIENTS[client]
    context_path = relative_path(target, context_name)
    context = context_path.read_text(encoding="utf-8") if context_path.exists() else ""
    start, end = f"<!-- ADIK:{bid}:START -->", f"<!-- ADIK:{bid}:END -->"
    if start in context or end in context:
        raise ContractError("Existing registration has no ownership receipt")
    adapters = {}
    pointers = []
    for skill in manifest["implementationSkills"]:
        meta = skill_metadata(relative_path(root, skill["path"]))
        adapter_name = f"{bid}-{meta['name']}"
        if len(adapter_name) > 64:
            raise ContractError("Bundle id plus skill name must fit the 64-character discovery limit")
        name = f"{skill_dir}/{adapter_name}/SKILL.md"
        path = relative_path(target, name)
        if path.parent.exists():
            raise ContractError(f"Refusing to overwrite existing skill directory: {path.parent}")
        canonical = f"{bundle_name}/{skill['path']}"
        link = Path(os.path.relpath(target / canonical, path.parent)).as_posix()
        adapters[name] = (f"---\nname: {adapter_name}\ndescription: {json.dumps(meta['description'])}\n---\n\n"
                          f"Read [{meta['name']}]({link}) and follow its implementation procedure.\n"
                          "Resolve that document's references from its own directory.\n"
                          "The bundled SDK and contracts describe the producer library. Inspect the consumer application only for integration.\n")
        pointers.append(f"- Implement {bid}: [{adapter_name}]({Path(os.path.relpath(path, context_path.parent)).as_posix()})")
    block = "\n".join([start, f"## {bid} adik {manifest['version']}",
                         "SDK code and matching implementation skills are installed together.", *pointers, end])
    planned_context = context.rstrip("\n") + ("\n\n" if context else "") + block + "\n"
    # Preflight all conflicts before creating files. Receipt records individual owned files.
    target.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for name in ["adik.manifest.json", *manifest["files"]]:
            destination = relative_path(target, f"{bundle_name}/{name}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(relative_path(root, name), destination)
            created.append(destination)
        for name, text in adapters.items():
            destination = relative_path(target, name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text, encoding="utf-8")
            created.append(destination)
        receipt = {"id": bid, "client": client, "version": manifest["version"],
                   "manifestHash": digest(root / "adik.manifest.json"),
                   "files": {p.relative_to(target).as_posix(): digest(p) for p in created},
                   "context": context_name, "block": block}
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(planned_context, encoding="utf-8")
        write_json(receipt_path, receipt)
        return receipt
    except OSError:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        if context_path.exists():
            context_path.write_text(context, encoding="utf-8")
        raise


def _check_receipt(target: Path, receipt: dict) -> None:
    bid, client = receipt.get("id", ""), receipt.get("client", "")
    if not isinstance(bid, str) or not isinstance(client, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", bid) or client not in CLIENTS:
        raise ContractError("Invalid installation receipt")
    skill_dir, context_name = CLIENTS[client]
    if receipt.get("context") != context_name:
        raise ContractError("Unexpected context path in receipt")
    files = receipt.get("files")
    if not isinstance(files, dict) or not files:
        raise ContractError("Receipt has no owned files")
    for name, expected in files.items():
        is_bundle = name.startswith(f".adik/{bid}/")
        is_adapter = re.fullmatch(re.escape(skill_dir) + "/" + re.escape(bid) + r"-[a-z0-9-]+/SKILL\.md", name)
        if not is_bundle and not is_adapter:
            raise ContractError(f"Receipt claims an unrelated path: {name}")
        path = relative_path(target, name)
        if not path.is_file() or digest(path) != expected:
            raise ContractError(f"Owned file was modified or removed; preserve and review it first: {name}")
    context_path = relative_path(target, context_name)
    context = context_path.read_text(encoding="utf-8") if context_path.exists() else ""
    block = receipt.get("block", "")
    if not isinstance(block, str) or not block.startswith(f"<!-- ADIK:{bid}:START -->") or not block.endswith(f"<!-- ADIK:{bid}:END -->") or context.count(block) != 1:
        raise ContractError("Owned context block was modified or removed; preserve and review it first")


def remove(target: Path, bid: str, dry_run: bool = False) -> list[str]:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", bid):
        raise ContractError("Invalid bundle id")
    receipt_path = relative_path(target, f".adik/.receipts/{bid}.json")
    receipt = read_json(receipt_path)
    if receipt.get("id") != bid:
        raise ContractError("Receipt id does not match requested bundle")
    _check_receipt(target, receipt)
    paths = list(receipt["files"])
    if dry_run:
        return paths
    # Delete only named files. Additional host files in these directories survive.
    context_path = relative_path(target, receipt["context"])
    context = context_path.read_text(encoding="utf-8")
    context_path.write_text(context.replace(receipt["block"], "", 1), encoding="utf-8")
    for name in paths:
        path = relative_path(target, name)
        path.unlink()
        parent = path.parent
        while parent != target:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    receipt_path.unlink()
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("seal", "validate", "pack", "install"):
        command = sub.add_parser(action)
        command.add_argument("--bundle", required=True, type=Path)
        if action == "pack":
            command.add_argument("--output", required=True, type=Path)
        if action == "install":
            command.add_argument("--target", required=True, type=Path)
            command.add_argument("--client", choices=CLIENTS, required=True)
    command = sub.add_parser("remove")
    command.add_argument("--target", required=True, type=Path)
    command.add_argument("--id", required=True)
    command.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.action == "remove":
            print(json.dumps(remove(args.target.resolve(), args.id, args.dry_run), indent=2))
        else:
            root = args.bundle.resolve()
            if args.action == "seal":
                seal(root)
            elif args.action == "validate":
                validate_bundle(root)
            elif args.action == "pack":
                pack(root, args.output)
            else:
                install(root, args.target.resolve(), args.client)
            print(f"ADIK {args.action}: PASS")
        return 0
    except (ContractError, OSError, ValueError) as exc:
        print(f"ADIK {args.action}: FAIL — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
