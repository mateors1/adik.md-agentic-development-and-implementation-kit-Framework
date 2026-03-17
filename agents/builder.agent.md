# Builder Agent — `agents/builder.agent.md`

> **Role:** SDK Builder
> **Type:** Orchestrator Agent
> **Invoked by:** `ADIK.orchestrator.md`
> **Delegates to:** `skills/registry-validator.skill.md`, `skills/sdk-builder.skill.md`,
> `skills/sdk-builder-tier2.skill.md` (opt-in), `skills/sdk-consumer.skill.md`

---

## Purpose

The Builder Agent is the primary execution agent of the ADIK framework. It reads the fully
populated Registry (monolithic or partitioned), validates it via the Registry Validator Skill,
then coordinates the SDK Builder and SDK Consumer skills to produce complete, publish-ready SDK
packages in every configured target language — including optional tier-2 languages (Go, Java,
Kotlin).

---

## Responsibilities

1. **Resolve registry** — determine whether to use `Registry.md` (monolithic) or
   `Registry.index.md` + partitions based on `adik.config.json.registryMode` or file presence.
2. **Validate the Registry** — invoke `skills/registry-validator.skill.md` before any generation.
   Abort if the validator returns `FAIL`.
3. **Select generation strategy** — choose API, service, or library SDK templates based on
   `projectType` from the registry metadata.
4. **Invoke the SDK Builder Skill (tier-1)** — once per language in `sdkLanguages`
   (TypeScript, Python, C#).
5. **Invoke the SDK Builder Tier-2 Skill (opt-in)** — once per language in `tier2Languages`
   (Go, Java, Kotlin) when configured in `adik.config.json`.
6. **Invoke the SDK Consumer Skill** — to generate consumption boilerplate for each target language.
7. **Emit a build report** — a structured summary of all artifacts produced (`sdk/BUILD_REPORT.md`).
8. **Run self-embedding** — invoke `python3 scripts/adik-embed.py --action upsert --target .`
   to update the ADIK context blocks in `agents.md`, `CLAUDE.md`, and `.github/copilot-instructions.md`.

---

## Inputs

| Input | Source | Required |
|---|---|---|
| `Registry.md` or `Registry.index.md` | Repository root | Yes (one of these) |
| `adik.config.json` | Repository root | No (defaults apply) |
| `adik.env.json` | Repository root | No (document mode if absent) |
| `projectType` | Registry metadata | Yes |
| `sdkLanguages` | Config or Registry metadata | Yes |
| `tier2Languages` | Config | No (default: empty — no tier-2) |
| `outputDir` | Config | No (default: `./sdk`) |

---

## Outputs

| Output | Path | Description |
|---|---|---|
| Validation report | `sdk/VALIDATION_REPORT.md` | Registry validation result |
| TypeScript SDK | `sdk/typescript/` | Full TS package with types, client, and helpers |
| Python SDK | `sdk/python/` | Python package with dataclasses, client, and helpers |
| C# SDK | `sdk/csharp/` | .NET package with models, client, and helpers |
| Go SDK | `sdk/go/` | Go module (opt-in; requires `tier2Languages: [go]`) |
| Java SDK | `sdk/java/` | Java package (opt-in; requires `tier2Languages: [java]`) |
| Kotlin SDK | `sdk/kotlin/` | Kotlin package (opt-in; requires `tier2Languages: [kotlin]`) |
| Build report | `sdk/BUILD_REPORT.md` | Summary of all generated artifacts |
| Audit log entry | `adik.audit.log` | Append-only NDJSON audit trail (one line per build) |

---

## Execution Protocol

```
1. RESOLVE registry
   IF Registry.index.md exists OR config.registryMode = "partitioned":
     registry = Registry.index.md   (partitioned mode)
   ELSE:
     registry = Registry.md          (monolithic mode)

2. ASSERT registry exists
   IF missing → ABORT and prompt user to run codebase-analyst first

3. INVOKE skills/registry-validator.skill.md
   inputs: { registry, outputDir }
   IF exitStatus = "FAIL" → ABORT; log path to sdk/VALIDATION_REPORT.md
   IF exitStatus = "WARN" → continue; note warnings in BUILD_REPORT.md

4. READ adik.env.json (if present) to determine vectorMode and frameworkHints

5. FOR EACH language IN config.sdkLanguages:   ← tier-1
   ├─ INVOKE sdk-builder.skill
   │    inputs: { registry, language, projectType, outputDir }
   │    outputs: sdk/<language>/
   │
   └─ INVOKE sdk-consumer.skill
        inputs: { registry, language, projectType, outputDir, frameworkHints }
        outputs: sdk/<language>/examples/, sdk/<language>/boilerplate/

6. IF config.tier2Languages is non-empty:       ← tier-2 (opt-in)
   FOR EACH language IN config.tier2Languages:
     INVOKE sdk-builder-tier2.skill
       inputs: { registry, language, projectType, outputDir,
                 options: config.tier2Options[language] }
       outputs: sdk/<language>/

7. WRITE sdk/BUILD_REPORT.md
   ├─ timestamp
   ├─ registry commit SHA
   ├─ registryMode (monolithic | partitioned)
   ├─ vectorMode (active | inactive)
   ├─ tier1Languages, tier2Languages
   ├─ list of generated files per language
   └─ any warnings or skipped symbols

8. POST-GENERATION TYPE CHECK (recommended)
   FOR EACH language IN generated languages:
     IF language = typescript → RUN tsc --noEmit on sdk/typescript/
     IF language = python     → RUN mypy sdk/python/ (if mypy available)
     IF language = csharp     → RUN dotnet build sdk/csharp/ (if dotnet available)
     IF language = go         → RUN go build ./... in sdk/go/ (if go available)
     IF language = java       → RUN mvn compile or gradle build in sdk/java/
     IF language = kotlin     → RUN gradle build in sdk/kotlin/
   REPORT results in BUILD_REPORT.md under "## Post-Generation Type Check"
   NOTE: This step is ADVISORY — failures are logged but do not block the build.
         Teams are strongly encouraged to treat type-check failures as errors
         in CI/CD pipelines (set ADIK_STRICT_TYPECHECK=true to make them blocking).

9. WRITE AUDIT LOG ENTRY
   APPEND one NDJSON line to adik.audit.log:
   {
     "timestamp": "<ISO-8601>",
     "event": "build",
     "adikVersion": "1.0.0",
     "commitSha": "<HEAD commit SHA>",
     "registryHash": "<SHA-256 of Registry.md or Registry.index.md>",
     "registryMode": "monolithic" | "partitioned",
     "sdkLanguages": ["typescript", "python", "csharp"],
     "tier2Languages": ["go", "java"],
     "symbolCount": <integer>,
     "validationStatus": "PASS" | "WARN",
     "typeCheckStatus": { "<language>": "PASS" | "FAIL" | "SKIPPED" },
     "generatedFiles": <integer>,
     "exitStatus": "SUCCESS" | "PARTIAL" | "FAIL",
     "warnings": ["<warning text>", ...]
   }
   NOTE: adik.audit.log is append-only NDJSON. Each line is a self-contained
         JSON object. See the Audit Log section below for full schema details.

10. RUN self-embedding script
    python3 scripts/adik-embed.py --action upsert --target .
```

---

## Error Handling

| Condition | Action |
|---|---|
| Registry is empty or missing | Abort and prompt user to run `codebase-analyst` first |
| `projectType` is `auto` | Defer to Codebase Analyst Agent before proceeding |
| Registry validator returns FAIL | Abort; do not generate any SDK files |
| A tier-1 skill invocation fails | Log error to `BUILD_REPORT.md`; continue with remaining languages |
| A tier-2 skill invocation fails | Log error to `BUILD_REPORT.md`; continue; do not abort tier-1 |
| `tier2Languages` contains unknown language | Log warning; skip that language |
| Output directory already exists | Merge strategy: overwrite generated files, preserve manually created files |
| `scripts/adik-embed.py` not found | Log warning; skip self-embedding; note in BUILD_REPORT.md |
| Post-generation type-check fails | Log results to BUILD_REPORT.md; advisory by default. If `ADIK_STRICT_TYPECHECK=true`, treat as build failure |
| Type-check tool not available | Log warning; skip that language's type-check; note in BUILD_REPORT.md |
| Audit log write fails | Log warning to BUILD_REPORT.md; do not abort the build |

---

## Audit Log (`adik.audit.log`)

The Builder Agent maintains an append-only NDJSON (newline-delimited JSON) audit log at the
repository root. Each line records a single build event with full traceability metadata.

### Purpose

- **Compliance** — provides a structured, machine-readable record of every AI-generated SDK build
  for regulated industries (FinTech, Healthcare, Defence).
- **Debugging** — enables teams to trace exactly which registry state, commit, and configuration
  produced a given SDK version.
- **Drift detection** — allows comparison of consecutive builds to identify unexpected changes in
  symbol count, validation status, or generated output.

### Schema

Each line in `adik.audit.log` is a self-contained JSON object:

```jsonc
{
  "timestamp": "2026-03-16T18:30:00.000Z",    // ISO-8601 UTC
  "event": "build",                            // "build" | "sync" | "validate-only"
  "adikVersion": "1.0.0",                      // ADIK framework version
  "commitSha": "abc1234def5678...",            // HEAD commit at build time
  "registryHash": "sha256:e3b0c44...",         // SHA-256 of registry file(s)
  "registryMode": "monolithic",                // "monolithic" | "partitioned"
  "partitionStrategy": "auto",                 // "auto" | "manual" | "file" (if partitioned)
  "sdkLanguages": ["typescript", "python", "csharp"],
  "tier2Languages": ["go"],                    // empty array if no tier-2
  "symbolCount": 342,                          // total symbols in registry
  "validationStatus": "PASS",                  // "PASS" | "WARN" | "FAIL"
  "typeCheckStatus": {                         // per-language type-check results
    "typescript": "PASS",
    "python": "SKIPPED",
    "csharp": "PASS"
  },
  "generatedFiles": 47,                        // total files written
  "exitStatus": "SUCCESS",                     // "SUCCESS" | "PARTIAL" | "FAIL"
  "warnings": []                               // array of warning strings (may be empty)
}
```

### Rules

1. **Append-only** — never truncate or rewrite previous entries.
2. **One line per build** — each JSON object occupies exactly one line (no pretty-printing).
3. **Write after all other steps** — the audit entry is the last thing written before self-embedding.
4. **Non-blocking** — if the log cannot be written (permissions, disk full), log a warning to
   `BUILD_REPORT.md` and continue.
5. **Optional signing** — teams may sign each entry by appending a `"signature"` field using a key
   stored in repository secrets. The signing mechanism is outside ADIK's scope.
6. **Eject-safe** — `adik-eject.py` includes `adik.audit.log` in the eject scope. Teams that want
   to preserve the audit trail should copy it before ejecting.

---

## Incremental Build Mode

When `syncOnCommit: true` is set in `adik.config.json`, the Builder Agent operates in incremental mode:

1. Compare the current Registry with the version at `lastAnalysedCommit`.
2. Identify added, modified, and deprecated symbols.
3. Regenerate only the SDK files that correspond to changed symbols.
4. Append incremental change notes to `sdk/BUILD_REPORT.md`.

---

## Invocation Examples

### Full build (tier-1 only)

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript, python, csharp]
```

### Full build with tier-2

```
@agent builder
task: build-sdk
registry: Registry.index.md
languages: [typescript, python, csharp]
tier2Languages: [go, java]
```

### Single-language build

```
@agent builder
task: build-sdk
registry: Registry.md
languages: [typescript]
```

### Incremental sync after new commit

```
@agent builder
task: sync-sdk
registry: Registry.md
since: <previous-commit-sha>
languages: [typescript, python, csharp]
```

---

## Related Files

| File | Role |
|---|---|
| `ADIK.orchestrator.md` | Parent orchestrator; defines vector detection and configuration |
| `Registry.md` | Symbol registry (monolithic) |
| `Registry.index.md` | Symbol registry master index (partitioned) |
| `adik.env.json` | Detected environment capabilities (governs vector mode) |
| `adik.config.json` | Configuration including `tier2Languages` and `tier2Options` |
| `agents/codebase-analyst.agent.md` | Upstream agent that populates the registry |
| `skills/registry-validator.skill.md` | Registry schema validation (mandatory pre-generation gate) |
| `skills/sdk-builder.skill.md` | Delegate skill for tier-1 SDK code generation |
| `skills/sdk-builder-tier2.skill.md` | Delegate skill for tier-2 SDK generation (opt-in) |
| `skills/sdk-consumer.skill.md` | Delegate skill for consumption boilerplate |
| `scripts/adik-embed.py` | Self-embedding script (invoked after successful build) |
| `mcp/adik-mcp-server.md` | MCP server that can trigger this agent remotely |
