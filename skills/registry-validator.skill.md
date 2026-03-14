# registry-validator.skill.md — ADIK Registry Validation Skill

> **Role:** Registry Schema Validator
> **Invoked by:** `agents/builder.agent.md` (before every SDK generation run)
> **Reads from:** `Registry.md` (or partitioned `Registry.*.md` files via `Registry.index.md`)
> **Writes to:** `sdk/VALIDATION_REPORT.md`
> **Purpose:** Validates the structural integrity and semantic correctness of all Registry entries
> before handing them to the SDK Builder Skill. This skill exists to catch hallucinated or
> malformed type mappings produced by the Codebase Analyst Agent before they propagate into
> generated SDK code.

---

## Why This Skill Exists

The Registry is authored by an LLM agent (the Codebase Analyst). LLMs can hallucinate type
mappings, produce inconsistent signatures, or emit structurally invalid YAML. Without a
deterministic validation gate, broken entries flow silently into the SDK Builder and produce
code that compiles but behaves incorrectly at runtime.

This skill acts as that gate: **no SDK generation may begin until this skill reports zero
blocking violations.**

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `registry` | path | Yes | Path to `Registry.md` or `Registry.index.md` |
| `strict` | boolean | No | Default `false`. When `true`, warnings are promoted to errors |
| `outputDir` | path | No | Default `./sdk`. Where `VALIDATION_REPORT.md` is written |

---

## Outputs

- `sdk/VALIDATION_REPORT.md` — human-readable report of all violations, warnings, and passes
- Exit status: `PASS` (0 violations), `WARN` (warnings only), `FAIL` (1+ blocking violations)

---

## Validation Rules

### Level 1 — Structural Integrity (blocking)

These checks verify that the Registry file is parseable and that required fields are present.

```
RULE S-001: Markers present
  ASSERT every section contains matching ADIK:<SECTION>:START and ADIK:<SECTION>:END markers.
  VIOLATION if a START marker has no corresponding END marker or vice versa.

RULE S-002: Required metadata fields
  ASSERT Project Metadata block contains non-empty values for:
    name, version, projectType, sourceLanguage, lastAnalysed, lastAnalysedCommit
  VIOLATION for each missing or empty required field.

RULE S-003: Symbol required fields
  FOR EACH symbol entry:
    ASSERT the following fields are present and non-empty: id, kind, name, namespace, signature
    VIOLATION for each missing field; include symbol id or name in violation message.

RULE S-004: Unique symbol IDs
  ASSERT no two entries share the same `id` value.
  VIOLATION on any duplicate; list all conflicting IDs.

RULE S-005: Valid `kind` values
  ASSERT each symbol `kind` is one of:
    function | class | interface | enum | schema | endpoint | type
  VIOLATION for any other value.

RULE S-006: Valid `projectType`
  ASSERT projectType ∈ {api, service, library}
  VIOLATION if set to "auto" (must be resolved before validation).
```

### Level 2 — Type Consistency (blocking)

These checks detect hallucinated or unmappable type references.

```
RULE T-001: Known primitive types
  FOR EACH parameter and return type:
    ASSERT type is one of the known primitives:
      string | number | integer | boolean | null | void | any | object | array |
      Record<K,V> | Map<K,V> | Set<T> | Promise<T> | Observable<T> | Buffer | Date | UUID
    OR is a reference to a symbol `id` defined elsewhere in the Registry.
    WARNING (strict: VIOLATION) for any type that is neither a primitive nor a known symbol ID.

RULE T-002: No raw `dict` or `object` without type parameter
  WARNING (strict: VIOLATION) if a parameter or return type is exactly "dict" or "Object"
  with no generic type argument.
  Message: "Ambiguous type '{type}' in symbol '{id}' — use a typed interface or specify
  generic parameters."

RULE T-003: Cross-partition type references
  IF registryMode = "partitioned":
    FOR EACH symbol type reference that is not a primitive:
      ASSERT the referenced symbol ID exists in some partition listed in Registry.index.md.
      VIOLATION for any dangling reference.

RULE T-004: Endpoint HTTP method validity
  FOR EACH symbol with kind = "endpoint":
    ASSERT a `method` tag is present with value ∈ {GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS}
    WARNING for missing method tag; VIOLATION if method value is invalid.

RULE T-005: Deprecated symbols referenced
  WARNING if a non-deprecated symbol's signature references the `id` of a deprecated symbol.
  Message: "Symbol '{id}' references deprecated symbol '{dep_id}'."
```

### Level 3 — Semantic Plausibility (warnings)

These checks flag entries that are structurally valid but likely the result of hallucination or
poor inference.

```
RULE P-001: Empty description
  WARNING for any symbol with an empty or single-word description.
  Message: "Symbol '{id}' has an uninformative description."

RULE P-002: Signature length
  WARNING if a function/method signature has zero parameters and returns void with no
  description suggesting it is intentional (e.g., a lifecycle hook or event emitter).

RULE P-003: Namespace consistency
  WARNING if symbols from the same source file (same namespace prefix) are assigned to
  different top-level namespace segments — possible sign of mis-classification.

RULE P-004: Changelog freshness
  WARNING if `lastAnalysed` is older than 30 days and the Changelog has no entry within
  that window.
```

---

## Execution Protocol

```
1. LOAD registry
   IF registry = "Registry.index.md" OR registryMode = "partitioned":
     FOR EACH partition in Partition Table:
       LOAD Registry.<domain>.md
   ELSE:
     LOAD Registry.md

2. RUN Level 1 — Structural Integrity rules (S-001 through S-006)
   IF any VIOLATION: set exitStatus = "FAIL"; continue collecting all violations

3. RUN Level 2 — Type Consistency rules (T-001 through T-005)
   IF any VIOLATION: set exitStatus = "FAIL"
   IF any WARNING and strict = true: set exitStatus = "FAIL"

4. RUN Level 3 — Semantic Plausibility rules (P-001 through P-004)
   Accumulate warnings; do NOT change exitStatus

5. WRITE sdk/VALIDATION_REPORT.md:
   - Header: timestamp, commit SHA, registry path, exitStatus
   - Section: Blocking Violations (grouped by rule)
   - Section: Warnings (grouped by rule)
   - Section: Summary (counts per level)
   - Footer: "ADIK Registry Validator — registry-validator.skill.md"

6. RETURN exitStatus to invoking agent
   "PASS"  → Builder Agent proceeds to SDK generation
   "WARN"  → Builder Agent proceeds with warning note in BUILD_REPORT.md
   "FAIL"  → Builder Agent ABORTS; logs path to VALIDATION_REPORT.md;
             instructs user to re-run codebase-analyst or fix Registry manually
```

---

## Validation Report Format

```markdown
# ADIK Registry Validation Report

**Timestamp:** 2025-01-15T10:30:00Z
**Commit SHA:** abc1234
**Registry:** Registry.md
**Exit Status:** FAIL

---

## Blocking Violations

### S-003 — Symbol required fields
- Symbol `fn:getUserById`: missing field `namespace`
- Symbol `cls:PaymentProcessor`: missing field `signature`

### T-002 — No raw `dict` or `object` without type parameter
- Symbol `fn:processWebhook` parameter `payload`: ambiguous type `dict` — use a typed
  interface or specify generic parameters.

---

## Warnings

### P-001 — Empty description
- Symbol `fn:init`: description is "Init."

---

## Summary

| Level | Rule | Violations | Warnings |
|---|---|---|---|
| Structural | S-003 | 2 | 0 |
| Type | T-002 | 1 | 0 |
| Plausibility | P-001 | 0 | 1 |
| **Total** | | **3** | **1** |

---

*ADIK Registry Validator — registry-validator.skill.md*
```

---

## Error Handling

| Condition | Action |
|---|---|
| Registry file not found | FAIL with violation "Registry file not found at `{path}`" |
| Registry.index.md missing when partitioned | FAIL with violation "Registry.index.md not found but registryMode is 'partitioned'" |
| Partition file listed in index but missing on disk | FAIL with violation for each missing partition |
| YAML parse error within a section | FAIL with violation including line number and parse error message |
| Output directory not writable | Log warning; print report to stdout instead |

---

## Invocation Example

```
# Run before SDK generation (standard invocation by Builder Agent)
@skill registry-validator
registry: Registry.md
outputDir: ./sdk

# Strict mode — promote all warnings to errors
@skill registry-validator
registry: Registry.index.md
strict: true
outputDir: ./sdk

# Partitioned registry
@skill registry-validator
registry: Registry.index.md
outputDir: ./sdk
```
