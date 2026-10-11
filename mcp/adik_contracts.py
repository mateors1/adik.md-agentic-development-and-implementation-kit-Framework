"""ADIK registry and completed-bundle contracts. No agent execution is performed."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath

SECTIONS = {
    "ENDPOINTS": "endpoint", "CLASSES": "class", "INTERFACES": "interface",
    "SCHEMAS": "schema", "ENUMS": "enum", "FUNCTIONS": "function", "ERRORS": "type",
}
KINDS = set(SECTIONS.values()) | {"type"}
LANGUAGES = {
    "python": (".py",), "typescript": (".ts", ".tsx"), "csharp": (".cs",),
    "go": (".go",), "java": (".java",), "kotlin": (".kt",),
}


class ContractError(ValueError):
    """Invalid registry, bundle, or owned path."""


def relative_path(root: Path, name: str) -> Path:
    """Resolve a portable relative path, rejecting traversal and symlinks."""
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ContractError(f"Invalid relative path: {name!r}")
    parts = PurePosixPath(name).parts
    if PurePosixPath(name).is_absolute() or any(p in ("..", ".") for p in name.split("/")):
        raise ContractError(f"Path must stay inside its bundle: {name}")
    if not parts or "" in name.split("/"):
        raise ContractError(f"Invalid relative path: {name}")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ContractError(f"Symlink is not an owned artifact: {name}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ContractError(f"Path escapes root: {name}")
    return path


def read_json(path: Path) -> dict:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(result, dict):
        raise ContractError(f"Expected a JSON object in {path}")
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _yaml(text: str):
    try:
        import yaml
    except ImportError as exc:
        raise ContractError("Legacy Markdown requires PyYAML; install requirements-adik.txt.") from exc
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ContractError(f"Invalid YAML: {exc}") from exc


def markdown_metadata(content: str) -> dict:
    match = re.search(r"```ya?ml\s*\n(.*?)```", content, re.S)
    result = _yaml(match.group(1)) if match else None
    if not isinstance(result, dict):
        raise ContractError("Registry must contain YAML project metadata.")
    return result


def resolve_registry(root: Path) -> Path:
    config_path = root / "adik.config.json"
    config = read_json(config_path) if config_path.exists() else {}
    if config.get("registryPath"):
        return relative_path(root, config["registryPath"])
    manifest_path = root / "adik.manifest.json"
    if manifest_path.exists():
        return relative_path(root, read_json(manifest_path).get("registry", ""))
    if (root / "contracts/registry.json").is_file():
        return relative_path(root, "contracts/registry.json")
    index = root / "Registry.index.md"
    if config.get("registryMode") == "partitioned":
        return relative_path(root, "Registry.index.md")
    if index.exists() and config.get("registryMode") != "monolithic":
        meta = markdown_metadata(index.read_text(encoding="utf-8"))
        if meta.get("registryMode") == "partitioned":
            return relative_path(root, "Registry.index.md")
    return relative_path(root, "Registry.md")


def _markdown_registry(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    metadata = markdown_metadata(content)
    symbols = []
    for section, kind in SECTIONS.items():
        start, end = f"<!-- ADIK:{section}:START -->", f"<!-- ADIK:{section}:END -->"
        if content.count(start) != 1 or content.count(end) != 1 or content.find(end) < content.find(start):
            raise ContractError(f"{path.name}: exactly one ordered marker pair required for {section}.")
        block = content.split(start, 1)[1].split(end, 1)[0]
        yaml_blocks = re.findall(r"```ya?ml\s*\n(.*?)```", block, re.S)
        if yaml_blocks:
            for item in yaml_blocks:
                data = _yaml(item)
                if isinstance(data, dict):
                    data = data.get("symbols", [data])
                if not isinstance(data, list) or any(not isinstance(s, dict) for s in data):
                    raise ContractError(f"{section}: expected YAML symbol objects.")
                symbols.extend(data)
        else:
            rows = [line.strip() for line in block.splitlines() if line.strip().startswith("|")]
            if rows:
                headers = [v.strip().lower() for v in rows[0].strip("|").split("|")]
                for row in rows[1:]:
                    if re.fullmatch(r"[|:\s-]+", row):
                        continue
                    cells = [v.strip() for v in row.strip("|").split("|")]
                    if len(cells) != len(headers):
                        raise ContractError(f"{section}: malformed legacy table row.")
                    symbol = dict(zip(headers, cells))
                    symbol.setdefault("kind", kind)
                    symbols.append(symbol)
    return {"schemaVersion": 2, "metadata": metadata, "symbols": symbols}


def load_registry(root: Path) -> dict:
    path = resolve_registry(root)
    if not path.is_file():
        raise ContractError(f"Registry not found: {path}")
    if path.suffix == ".json":
        return read_json(path)
    content = path.read_text(encoding="utf-8")
    meta = markdown_metadata(content)
    if path.name != "Registry.index.md":
        return _markdown_registry(path)
    if meta.get("registryMode") != "partitioned":
        raise ContractError("Registry.index.md is a template, not an active partitioned registry.")
    start, end = "<!-- ADIK:PARTITIONS:START -->", "<!-- ADIK:PARTITIONS:END -->"
    if content.count(start) != 1 or content.count(end) != 1 or content.index(end) < content.index(start):
        raise ContractError("Invalid partition markers.")
    block = content.split(start, 1)[1].split(end, 1)[0]
    files = []
    for line in block.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1].endswith(".md"):
            files.append(cells[1])
    if not files or len(files) != len(set(files)):
        raise ContractError("Partition index must list unique registry files.")
    symbols = []
    for name in files:
        if not re.fullmatch(r"Registry\.[a-z0-9-]+\.md", name) or name == "Registry.index.md":
            raise ContractError(f"Invalid registry partition: {name}")
        child = _markdown_registry(relative_path(root, name))
        for key in ("name", "version", "lastAnalysedCommit"):
            if child["metadata"].get(key) != meta.get(key):
                raise ContractError(f"Partition {name} has inconsistent {key}.")
        symbols.extend(child["symbols"])
    return {"schemaVersion": 2, "metadata": meta, "symbols": symbols}


def validate_registry(data: dict, require_symbols: bool = True) -> list[str]:
    errors = []
    if data.get("schemaVersion") != 2:
        errors.append("registry.schemaVersion must be 2")
    meta = data.get("metadata")
    if not isinstance(meta, dict):
        return errors + ["registry.metadata must be an object"]
    for field in ("name", "version", "projectType", "sourceLanguage", "lastAnalysed", "lastAnalysedCommit"):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            errors.append(f"metadata.{field} must be a nonempty string")
    if meta.get("projectType") not in ("api", "service", "library"):
        errors.append("metadata.projectType must be api, service, or library")
    symbols = data.get("symbols")
    if not isinstance(symbols, list):
        return errors + ["registry.symbols must be an array"]
    if require_symbols and not symbols:
        errors.append("registry must contain at least one symbol")
    seen = set()
    for index, symbol in enumerate(symbols):
        if not isinstance(symbol, dict):
            errors.append(f"symbols[{index}] must be an object")
            continue
        for field in ("id", "kind", "name", "namespace", "signature"):
            if not isinstance(symbol.get(field), str) or not symbol[field].strip():
                errors.append(f"symbols[{index}].{field} must be a nonempty string")
        sid = symbol.get("id")
        if isinstance(sid, str):
            if sid in seen:
                errors.append(f"Duplicate symbol ID: {sid}")
            seen.add(sid)
        if not isinstance(symbol.get("kind"), str) or symbol["kind"] not in KINDS:
            errors.append(f"Invalid kind for symbol {sid}")
    return errors


def registry_report(root: Path, strict: bool = False) -> dict:
    try:
        data = load_registry(root)
        errors = validate_registry(data)
        symbols = data.get("symbols")
        symbols = symbols if isinstance(symbols, list) else []
        warnings = [f"Missing description: {s.get('id', '?')}" for s in symbols
                    if isinstance(s, dict) and not s.get("description")]
    except (ContractError, OSError) as exc:
        return {"status": "FAIL", "errors": [str(exc)], "warnings": [], "symbolCount": 0}
    if strict:
        errors.extend(warnings)
        warnings = []
    return {"status": "FAIL" if errors else "WARN" if warnings else "PASS",
            "errors": errors, "warnings": warnings, "symbolCount": len(symbols)}


def payload_files(root: Path) -> dict[str, str]:
    files = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        relative_path(root, name)
        if path.is_file() and name != "adik.manifest.json":
            if any(p in (".git", "__pycache__", "node_modules") for p in path.parts):
                raise ContractError(f"Remove build/runtime debris from bundle: {name}")
            files[name] = digest(path)
    return files


def skill_metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ContractError(f"Missing SKILL.md frontmatter: {path}")
    fields = _yaml(match.group(1))
    if not isinstance(fields, dict):
        raise ContractError(f"Skill frontmatter must be an object: {path}")
    name = fields.get("name", "")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64 or name != path.parent.name:
        raise ContractError(f"Skill name must match its directory: {path}")
    desc = fields.get("description", "")
    if not isinstance(desc, str) or not desc.strip() or len(desc) > 1024:
        raise ContractError(f"Use a nonempty description (max 1024 characters): {path}")
    metadata = fields.get("metadata", {})
    if not isinstance(metadata, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()):
        raise ContractError(f"Skill metadata must map strings to strings: {path}")
    return fields


def validate_bundle(root: Path, verify_hashes: bool = True) -> dict:
    """Check artifact presence and declared relationships, never run package code."""
    manifest = read_json(relative_path(root, "adik.manifest.json"))
    if manifest.get("schemaVersion") != 2:
        raise ContractError("adik.manifest.json schemaVersion must be 2")
    bid = manifest.get("id", "")
    if not isinstance(bid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", bid) or len(bid) > 48:
        raise ContractError("Bundle id must be lowercase kebab-case, max 48 characters")
    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        raise ContractError("Bundle version must be a semantic version")
    source = manifest.get("source", {})
    if not isinstance(source, dict) or not isinstance(source.get("revision"), str) or not source["revision"].strip():
        raise ContractError("source.revision is required")
    registry = read_json(relative_path(root, manifest.get("registry", "")))
    errors = validate_registry(registry)
    if errors:
        raise ContractError("; ".join(errors))
    if registry["metadata"]["lastAnalysedCommit"] != source["revision"]:
        raise ContractError("Registry source revision differs from bundle source revision")
    symbol_ids = {s["id"] for s in registry["symbols"]}
    sdks = manifest.get("sdks")
    skills = manifest.get("implementationSkills")
    if not isinstance(sdks, list) or not sdks or not isinstance(skills, list) or not skills:
        raise ContractError("A completed adik requires SDK code AND implementation skills")
    languages = set()
    for sdk in sdks:
        if not isinstance(sdk, dict):
            raise ContractError("SDK entries must be objects")
        lang = sdk.get("language")
        if not isinstance(lang, str) or lang not in LANGUAGES or lang in languages:
            raise ContractError(f"Unsupported or repeated SDK language: {lang}")
        languages.add(lang)
        if sdk.get("version") != version:
            raise ContractError(f"SDK {lang} must share bundle version {version}")
        sdk_root = relative_path(root, sdk.get("path", ""))
        if not sdk_root.is_dir() or not sdk_root.relative_to(root).as_posix().startswith("sdk/"):
            raise ContractError(f"SDK {lang} must live under sdk/")
        for field in ("packageManifest", "entryPoint"):
            p = relative_path(root, sdk.get(field, ""))
            if not p.is_file() or not p.is_relative_to(sdk_root) or not p.read_bytes().strip():
                raise ContractError(f"Missing {lang} {field} inside SDK directory")
        entry = relative_path(root, sdk["entryPoint"])
        if entry.suffix not in LANGUAGES[lang] or not entry.read_bytes().strip():
            raise ContractError(f"SDK {lang} needs a nonempty source entry point")
    covered = set()
    names = set()
    for skill in skills:
        if not isinstance(skill, dict):
            raise ContractError("Implementation skill entries must be objects")
        path = relative_path(root, skill.get("path", ""))
        if path.name != "SKILL.md" or len(path.relative_to(root).parts) != 3 or not skill["path"].startswith("skills/"):
            raise ContractError("Implementation skill path must be skills/<name>/SKILL.md")
        metadata = skill_metadata(path)
        if metadata["name"] in names:
            raise ContractError("Repeated implementation skill name")
        names.add(metadata["name"])
        if metadata.get("metadata", {}).get("sdk-version") != version:
            raise ContractError(f"Skill {metadata['name']} sdk-version must be {version}")
        for field in ("sdkLanguages", "symbolIds", "references", "examples"):
            values = skill.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(v, str) for v in values):
                raise ContractError(f"Skill {field} must be a nonempty string array")
        if not set(skill["sdkLanguages"]) <= languages or not set(skill["symbolIds"]) <= symbol_ids:
            raise ContractError("Skill references missing SDK languages or registry symbols")
        covered.update(skill["sdkLanguages"])
        for name in skill["references"] + skill["examples"]:
            p = relative_path(root, name)
            if not p.is_file() or not p.read_bytes().strip():
                raise ContractError(f"Missing or empty implementation artifact: {name}")
    if covered != languages:
        raise ContractError("Every SDK language needs an implementation skill")
    actual = payload_files(root)
    if verify_hashes and manifest.get("files") != actual:
        raise ContractError("Bundle inventory or SHA-256 hashes differ; validate and seal the producer output")
    return manifest
