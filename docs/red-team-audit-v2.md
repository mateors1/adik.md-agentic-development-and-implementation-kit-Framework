# ADIK Red-Team Audit v2 — Post-Implementation Review

> **Audit date:** 2026-03-14
> **Framework version:** 2.0.0
> **Audited by:** Internal Red Team (AI-assisted)
> **Scope:** Full review of ADIK.md, ADIKbuilder.md, all agents, skills, scripts, CI/CD workflow,
> and registry model after v2.0 feature implementation.

---

## Executive Summary

ADIK v2.0 addresses the five critical vulnerabilities identified in the v1.1 red-team report and
introduces registry partitioning, deterministic self-embedding, headless CI/CD mode, an eject
protocol, schema validation, and tier-2 language support. This document re-audits the framework
through a red-team lens, identifies residual risks, and flags new attack surfaces introduced by
v2.0 changes.

Overall risk posture: **Improved from HIGH to MEDIUM-LOW.** Most blocking vulnerabilities from
v1.1 are now resolved. Several new medium-severity risks are introduced by the expanded feature
surface and require attention in v2.1.

---

## Resolved Vulnerabilities from v1.1

### ✅ V-01 — Registry Context Window Bottleneck (RESOLVED)

**Original risk:** A monolithic `Registry.md` with thousands of symbols would exceed agent context
limits on large codebases.

**Mitigation implemented:**
- `Registry.index.md` introduces a partitioned model (`Registry.<domain>.md` files).
- The Codebase Analyst Agent is updated to write domain-scoped partitions and maintain the index.
- Agents are instructed to load only relevant partitions rather than the full registry.
- A vectorization advisory is surfaced automatically when total symbol count ≥ 500.

**Residual risk (LOW):** Agents that do not honour the "load only relevant partitions" rule may
still load excessive context. This is a prompt-compliance risk that depends on the LLM model in
use. Mitigation: the Builder Agent and SDK Builder Skill now receive explicit per-partition
invocations rather than a single full-registry load.

---

### ✅ V-02 — Interactive Startup Prompt Blocks CI/CD (RESOLVED)

**Original risk:** The startup prompt (A/Blanket vs B/Guided) would cause indefinite blocking
in CI pipelines where no TTY is present.

**Mitigation implemented:**
- `ADIK_NON_INTERACTIVE=true` environment variable bypasses the startup prompt.
- `ADIK_STARTUP_MODE=blanket|guided` sets the default mode non-interactively.
- The CI/CD self-deploy workflow (`adik-self-deploy.yml`) sets both variables.
- `adik.env.json` persists the startup mode for subsequent runs.

**Residual risk (LOW):** If an agent model ignores the environment variable hint and still emits
an interactive prompt, the pipeline will hang. Teams should validate headless behaviour on their
specific model before enabling `syncOnCommit: true`.

---

### ✅ V-03 — Hallucination in Markdown Typings (RESOLVED)

**Original risk:** No schema validation on Registry.md entries; hallucinated type mappings
propagate silently into generated SDK code.

**Mitigation implemented:**
- `skills/registry-validator.skill.md` defines a three-level validation gate (Structural
  Integrity, Type Consistency, Semantic Plausibility).
- The Builder Agent now invokes the validator before every SDK generation run.
- Blocking violations halt generation and write a `sdk/VALIDATION_REPORT.md`.
- Rule T-002 specifically targets `dict`/`Object` hallucinations.

**Residual risk (MEDIUM):** The validator is itself an LLM skill — it cannot mathematically
prove type correctness. Rule T-001 catches unknown types, but a plausible-but-wrong type
(e.g., `UserDTO` that exists but has wrong fields) will pass validation. Recommend: supplement
with a post-generation unit-test step where the generated SDK is compiled/type-checked.

---

### ✅ V-04 — Self-Embedding Append Spiral (RESOLVED)

**Original risk:** LLM-driven appends to `CLAUDE.md` and other context files could produce
duplicate blocks over time or across model versions.

**Mitigation implemented:**
- All three context files now use `<!-- ADIK:START -->` / `<!-- ADIK:END -->` guard markers.
- `scripts/adik-embed.py` provides a deterministic Python script for insert/replace/remove/check.
- The script uses exact string matching (not LLM regex) to find and replace the block.
- ADIK.md directs agents to invoke this script rather than performing text replacement directly.

**Residual risk (LOW):** If an agent edits context files directly (bypassing the script), the
risk of duplication returns. Teams using the MCP server for remote orchestration should ensure
the `adik_embed` tool routes through `adik-embed.py`.

---

### ✅ V-05 — No Uninstall / Rollback Protocol (RESOLVED)

**Original risk:** No documented way to remove ADIK from a codebase.

**Mitigation implemented:**
- `scripts/adik-eject.py` provides a safe, dry-run-first eject operation.
- `ADIK_EJECT=true` enables non-interactive eject for CI/CD.
- `ADIK_EJECT_SDK=true` optionally removes the generated `sdk/` directory.
- Source code is never touched by the eject script.

**Residual risk (LOW):** The eject script removes `scripts/` itself, which means it self-deletes
when the eject includes the `scripts/` directory. Teams should copy the script to a safe location
before running a full eject if they want to verify or re-run it after the fact.

---

## New Vulnerabilities and Risks Introduced in v2.0

### 🔴 N-01 — CI/CD Token Scope Over-Privilege (HIGH)

**Description:** The `adik-self-deploy.yml` workflow requires `ADIK_DEPLOY_TOKEN` with `repo`
scope to create and push to repositories. A broad `repo` scope grants full read/write access
to all repositories in the actor's account — a significant blast radius if the token is
compromised.

**Recommended fix:**
- Use a GitHub App token (fine-grained) instead of a PAT. Grant only `contents:write` and
  `metadata:read` on the specific target repository.
- Rotate `ADIK_DEPLOY_TOKEN` regularly.
- Restrict the workflow trigger to protected branches via `branches: [main]` filter.
- Add a required review (environment protection rule) for manual `workflow_dispatch` deploys.

**Priority:** Fix in v2.1 before enabling the workflow in production.

---

### 🟡 N-02 — Partition Domain Inference Ambiguity (MEDIUM)

**Description:** The partitioning strategy assigns symbols to domains based on the top-level
namespace segment. In polyglot or flat-namespace projects (e.g., Python packages with a single
`src/` root), all symbols may land in one partition, negating the benefit of partitioning and
still triggering the vectorization advisory unnecessarily.

**Recommended fix:**
- Add a `partitionStrategy` option to `adik.config.json`:
  - `"auto"` (default) — infer from namespace hierarchy
  - `"manual"` — explicit mapping of namespaces to partition names in `partitionMappings`
  - `"file"` — one partition per top-level source directory
- Document the strategy in `Registry.index.md`.

---

### 🟡 N-03 — Tier-2 Language Type Mapping Coverage Gaps (MEDIUM)

**Description:** The Go, Java, and Kotlin type mappings in `sdk-builder-tier2.skill.md` cover
common primitives but omit several edge cases:
- Go: no mapping for `Observable<T>` (not idiomatic; should map to `chan T` with a note)
- Java: `Promise<T>` mapped to `CompletableFuture<T>` — correct for Java 8+, but not for
  reactive stacks (Project Reactor: `Mono<T>`, `Flux<T>`)
- Kotlin: `Set<T>` from Registry maps to `Set<T>` without specifying mutability
  (`MutableSet<T>` vs immutable `Set<T>`)

**Recommended fix:**
- Add a `reactiveProfile` option for Java: `"completable-future"` | `"reactor"` | `"rxjava"`
- Document known gaps in `sdk-builder-tier2.skill.md` under a "Known Limitations" section.

---

### 🟡 N-04 — Validator is an LLM Skill — Cannot Replace Compilation (MEDIUM)

**Description:** `registry-validator.skill.md` is executed by an LLM agent. The LLM may
misapply validation rules, miss violations, or hallucinate false positives. Teams relying
solely on this skill for quality assurance have a false sense of safety.

**Recommended fix:**
- Add a post-generation compile/type-check step to the Builder Agent's execution protocol:
  - TypeScript: `tsc --noEmit` on the generated `sdk/typescript/`
  - Python: `mypy` on the generated `sdk/python/`
  - C#: `dotnet build` on the generated `sdk/csharp/`
  - Go: `go build ./...` on the generated `sdk/go/`
  - Java/Kotlin: `mvn compile` or `gradle build`
- These are deterministic compilers — they provide ground truth that LLM validation cannot.
- Document this as a recommended post-build step in `agents/builder.agent.md`.

---

### 🟢 N-05 — Eject Script Self-Deletion (LOW)

**Description:** When `scripts/` is included in the eject scope and the user runs the eject
with `--confirm`, the script deletes itself during execution. Python's script execution model
allows this (the script is already loaded into memory), but the script is no longer available
for verification or re-run after the fact.

**Recommended fix:**
- Add a `--keep-scripts` flag that excludes `scripts/` from the deletion scope.
- Document this behaviour in the script's docstring and the eject protocol in `ADIK.md`.

---

### 🟢 N-06 — Registry.index.md Not in Bundle by Default (LOW)

**Description:** `Registry.index.md` is a new v2.0 file that should be part of the deployable
bundle. The `ADIKbuilder.md` bundle list and the CI/CD workflow must explicitly include it.
Currently, the workflow copies it, but `ADIKbuilder.md`'s documented bundle list needs updating.

**Status:** Addressed in v2.0 — `ADIKbuilder.md` updated to include `Registry.index.md` and
`scripts/` in the bundle list.

---

### 🟢 N-07 — adik-embed.py Template Injection via adik.config.json (LOW)

**Description:** `scripts/adik-embed.py` reads `adik.config.json` and interpolates values into
template strings using Python `str.format()`. If an attacker controls `adik.config.json` content
(e.g., via a supply-chain attack or a malicious PR), they could inject `{` / `}` characters that
break the template rendering or cause unexpected substitutions.

**Recommended fix:**
- Sanitize string values read from `adik.config.json` before interpolation: escape `{` → `{{`
  and `}` → `}}` in all user-supplied strings.
- Use a templating approach that separates data from template syntax (e.g., `string.Template`
  with `$`-based substitution, or `str.format_map` with a `SafeDict`).

---

## Systemic Observations

### S-01 — LLM-Native Framework Lacks Runtime Guarantees

ADIK is an entirely LLM-driven framework. Every agent and skill is a Markdown specification
executed by a language model. This means:

- **No unit tests** validate agent behaviour.
- **No schema enforcement** at parse time (YAML inside Markdown is not structured data).
- **No replay / determinism** — running the same agent twice on the same codebase may produce
  different Registry entries.

**Recommendation:** Introduce an optional `adik-ci.yml` workflow that:
1. Runs the Codebase Analyst Agent on the source repository.
2. Runs the Registry Validator.
3. Runs the Builder Agent.
4. Compiles/type-checks all generated SDKs.
5. Fails the CI run if any step produces a non-PASS result.

This provides a deterministic integration test harness around the non-deterministic LLM core.

---

### S-02 — No Audit Trail for AI-Generated Code

For regulated industries (FinTech, Healthcare, Defence), AI-generated code must be traceable.
ADIK currently writes `BUILD_REPORT.md` but does not produce a signed or structured audit log.

**Recommendation:** Implement the SBOM/audit trail suggestion from the original red-team report:
- Add `adik.audit.log` (append-only NDJSON) with entries containing:
  `{ timestamp, commitSha, agentVersion, registryHash, sdkLanguages, symbolCount, exitStatus }`
- Optionally sign entries with a key stored in the repository's GitHub Secrets.

---

### S-03 — Self-Deploy Workflow Creates Public Repositories by Default

The `adik-self-deploy.yml` workflow defaults to `visibility: public`. For internal or proprietary
projects, this means the ADIK bundle (which may contain API surface definitions) is publicly
visible.

**Recommendation:** Change the default visibility to `private` and require explicit opt-in for
`public`.

---

## Risk Matrix (v2.0)

| ID | Description | Severity | Status |
|---|---|---|---|
| V-01 | Registry context window bottleneck | HIGH | ✅ Resolved |
| V-02 | Interactive startup blocks CI | HIGH | ✅ Resolved |
| V-03 | Hallucination in Markdown typings | HIGH | ✅ Resolved (partial) |
| V-04 | Self-embedding append spiral | MEDIUM | ✅ Resolved |
| V-05 | No uninstall protocol | MEDIUM | ✅ Resolved |
| N-01 | CI/CD token over-privilege | HIGH | 🔴 Open — fix in v2.1 |
| N-02 | Partition domain inference ambiguity | MEDIUM | 🟡 Open |
| N-03 | Tier-2 type mapping gaps | MEDIUM | 🟡 Open |
| N-04 | Validator not a compiler | MEDIUM | 🟡 Open |
| N-05 | Eject self-deletion | LOW | 🟢 Accepted with note |
| N-06 | Registry.index.md not in bundle | LOW | ✅ Resolved |
| N-07 | Template injection via config | LOW | 🟢 Open — fix in v2.1 |
| S-01 | No runtime guarantees | SYSTEMIC | 🟡 Partially mitigated |
| S-02 | No audit trail | SYSTEMIC | 🟡 Recommended for v2.1 |
| S-03 | Public bundle repo by default | MEDIUM | 🔴 Fix immediately |

---

## Recommended Actions for v2.1

1. **[HIGH]** Switch `adik-self-deploy.yml` to use a fine-grained GitHub App token instead of
   a broad PAT. Change default visibility to `private`.
2. **[HIGH]** Add post-generation compile/type-check step to Builder Agent protocol.
3. **[MEDIUM]** Add `--keep-scripts` flag to `adik-eject.py`.
4. **[MEDIUM]** Sanitize `adik.config.json` values in `adik-embed.py` before template
   interpolation.
5. **[MEDIUM]** Add `partitionStrategy` option to `adik.config.json`.
6. **[MEDIUM]** Document tier-2 type mapping gaps and add reactive profile option for Java.
7. **[LOW]** Implement `adik.audit.log` for SBOM/compliance use cases.
8. **[LOW]** Introduce `adik-ci.yml` optional workflow for deterministic integration testing.
