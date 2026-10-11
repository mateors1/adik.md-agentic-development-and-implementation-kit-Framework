---
name: registry-validator
description: Validate producer registry structure and review source accuracy before generating SDK code or packaging an adik.
---

# Validate the producer registry

Run MCP `adik_validate_registry`, or import `registry_report(root, strict=False)`
from `mcp/adik_contracts.py` in the producer toolkit. Stop generation on FAIL.
Canonical registries follow `schemas/registry.schema.json`; legacy Markdown
requires all seven ordered section marker pairs. An empty template is not a
validated producer registry. Resolve active partitions explicitly.

The shared validator checks required metadata, project type, symbol fields,
symbol IDs, kinds and partition consistency. Missing descriptions produce WARN;
strict mode promotes warnings to failures. It does not prove semantic accuracy.

Review each public capability against producer code and tests: parameter types,
return values, authentication, errors, side effects, retry safety and compatibility.
Record uncertainties rather than manufacturing details. Include source references
and deterministic SDK checks in a producer validation report outside the sealed
bundle, or include the report before sealing.

After SDK and implementation-kit generation, run:

```sh
python3 scripts/adik-bundle.py seal --bundle <output>
python3 scripts/adik-bundle.py validate --bundle <output>
```

Bundle validation checks artifacts, relationships, versions and hashes. Run SDK
builds and behavior tests separately; report their actual results.
