---
name: speckit.adik.registry
description: "Scan source code and Spec Kit contracts to populate the ADIK symbol registry"
---

$ARGUMENTS

Read the template at `.specify/extensions/adik-sdk-generator/templates/speckit.adik.registry.md` and follow its instructions exactly. This command invokes the ADIK Codebase Analyst Agent to scan the project source code and any `.specify/specs/*/contracts/api-spec.json` files, then populates `Registry.md` with every discovered public symbol.
