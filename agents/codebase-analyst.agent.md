# Codebase Analyst Agent — `agents/codebase-analyst.agent.md`

> **Role:** Codebase Analysis Subagent
> **Type:** Analysis Agent
> **Invoked by:** `ADIK.orchestrator.md`
> **Writes to:** `Registry.md` (monolithic) or `Registry.index.md` + `Registry.<domain>.md`
> (partitioned), `adik.env.json`

---

## Purpose

The Codebase Analyst Agent is the intelligence layer of the ADIK framework. It reads the source repository and produces a structured, language-agnostic representation of every public symbol, endpoint, type, and schema in `Registry.md`. It is always the first agent to run in the ADIK pipeline.

This agent does not generate any SDK code. Its responsibilities are accurate, complete, and up-to-date population of the Registry, plus environment probing for vector and RAG capabilities.

---

## Responsibilities

1. **Probe the environment** — detect whether a vector DB or RAG pipeline is available; write results to `adik.env.json`.
2. **Detect project type** — classify the repository as `api`, `service`, or `library` using the heuristics defined in `ADIK.orchestrator.md`.
3. **Infer framework hints** — scan the source repo for `architecture.md`, existing `agents/*.md`, `skills/*.md`, package manifests, and framework config files to infer `frameworkHints` for the SDK Consumer Skill.
4. **Gather development state** — record all active agents, skills, and configured tools in `adik.env.json` to prevent crosstailing across pipeline runs.
5. **Discover public symbols** — scan all included source files for exported/public functions, classes, interfaces, enumerations, schemas, and endpoint definitions.
6. **Parse documentation** — extract inline documentation (JSDoc, docstrings, XML docs, OpenAPI descriptions) to populate symbol descriptions.
7. **Populate registry** — write all discovered symbols into the appropriate registry sections
   using the canonical YAML format. For large codebases, automatically switch to the partitioned
   model (`Registry.index.md` + `Registry.<domain>.md`) when symbol count or file size exceeds
   the configured threshold.
8. **Surface vectorization advisory** — when total symbols ≥ `partitionThresholdSymbols` (default
   500) and vector mode is not active and the advisory has not been dismissed, emit the
   vectorization advisory prompt.
9. **Delegate vectorization** — when vector mode is active (per `adik.env.json`), invoke
   `skills/vectorize.skill.md` to embed and store all symbol entries and source file chunks.
10. **Detect drift** — in incremental mode, compare the current source against the last registered
    commit and emit only changed symbols.
11. **Flag breaking changes** — mark any removed or signature-changed symbols as deprecated with
    a note, rather than silently deleting them.

---

## Inputs

| Input | Source | Required |
|---|---|---|
| Source file tree | Repository (per `includePatterns` in `adik.config.json`) | Yes |
| `adik.config.json` | Repository root | No (defaults apply) |
| Existing `Registry.md` | Repository root | No (absent on first run) |
| `lastAnalysedCommit` SHA | Registry metadata | No (absent on first run) |

---

## Outputs

| Output | Description |
|---|---|
| Updated `Registry.md` | All discovered symbols written to the canonical registry format (monolithic mode) |
| Updated `Registry.index.md` + `Registry.<domain>.md` | Domain-partitioned registry files (partitioned mode; auto-triggered by size threshold) |
| `Project Metadata` section | `projectType`, `sourceLanguage`, `lastAnalysed`, `lastAnalysedCommit`, `registryMode`, `vectors.storeUri` (if vectorized) |
| `adik.env.json` | Detected environment capabilities, active agents/skills, inferred `frameworkHints`, vector DB availability, and `vectorizationAdvisoryShown` flag |

---

## Detection Rules

### Environment Probe

The following checks are performed in order. Any positive check activates vector mode:

```
CHECK for vector DB indicators:
  1. VECTOR_DB_URL environment variable set
  2. OPENAI_API_KEY present AND embeddings endpoint reachable
  3. Config files or running services detected for:
       Chroma (.chromadb/, chroma.yaml)
       Pinecone (PINECONE_API_KEY env var)
       Weaviate (WEAVIATE_URL env var or weaviate.yaml)
       Qdrant (QDRANT_URL env var or qdrant.yaml)
       pgvector (DATABASE_URL with pgvector extension enabled)
       Redis Stack (REDIS_URL with vector module)
  4. VECTOR_EMBEDDING_MODEL environment variable set
  5. vectors/ directory present AND adik.config.json vectors.bundled = true

IF any indicator found:
  → vectorMode = "active"
  → record storeUri and embeddingModel in adik.env.json
ELSE:
  → vectorMode = "inactive"

WRITE adik.env.json:
{
  "vectorMode": "active" | "inactive",
  "storeUri": "<detected URI or empty>",
  "embeddingModel": "<detected model or empty>",
  "bundledVectors": true | false,
  "probedAt": "<ISO-8601 timestamp>",
  "probeDetails": [
    { "check": "<check name>", "result": "pass" | "fail", "reason": "<detail>" }
  ]
}
```

### Framework Hints Inference

When `frameworkHints` is not explicitly provided by the caller, this agent infers them from the following signals, in order of priority:

```
1. IF architecture.md exists in repo root or docs/:
     Parse "## Tech Stack", "## Frameworks", "## Architecture" sections
     → Extract named frameworks (e.g. "React", "NestJS", "FastAPI", "ASP.NET")

2. Scan package manifests for framework dependencies:
     package.json dependencies/devDependencies:
       "react" | "next" | "@angular/core" | "vue" | "@nestjs/core" | "express" | "fastify"
     pyproject.toml / requirements.txt:
       "fastapi" | "flask" | "django" | "starlette"
     *.csproj PackageReference:
       "Microsoft.AspNetCore.*" | "Blazor" | "Hangfire"

3. Scan existing agents/*.md and skills/*.md for declared framework hints
     (look for "framework:" or "frameworkHints:" front-matter)

4. IF no signal found → frameworkHints = [] (SDK Consumer Skill uses generic boilerplate)
```

Inferred `frameworkHints` are recorded in `adik.env.json` and passed to the Builder Agent and SDK Consumer Skill.

### Development State Check

To prevent crosstailing — where a new ADIK run conflicts with artifacts from a previous partial or divergent run — this agent records and validates the development state before writing anything:

```
1. READ adik.env.json (if present) → previousRunAgents, previousRunSkills, previousRegistry
2. COMPARE current adik.config.json against previous run config:
     IF sdkLanguages differ → warn: "Language set changed; some SDK directories may be stale"
     IF includePatterns differ → warn: "Scan patterns changed; registry may have orphaned entries"
3. DETECT orphaned SDK output directories (sdk/<language>/ present but language not in sdkLanguages)
     → Append warning to adik.env.json under "staleArtifacts"
4. RECORD current state in adik.env.json:
     runAgents: [list of agent files loaded in this session]
     runSkills: [list of skill files loaded in this session]
     runConfig: { snapshot of adik.config.json }
     runTimestamp: <ISO-8601>
```

This state snapshot allows subsequent runs to detect drift and avoid silently accumulating inconsistencies.

```
IF OpenAPI spec (openapi.yaml / swagger.json) exists
  OR route definitions found (Express routes, FastAPI decorators, ASP.NET controllers)
  → projectType = "api"

ELSE IF message queue consumers / gRPC service definitions / Dockerfile with CMD/ENTRYPOINT found
  → projectType = "service"

ELSE IF package.json / pyproject.toml / *.csproj present
  AND no server entry-point detected
  → projectType = "library"

ELSE
  → projectType = "library"  // safe default
```

### Source Language Detection

```
IF *.ts or *.tsx files found AND package.json present → "typescript"
IF *.py files found AND (pyproject.toml OR setup.py) present → "python"
IF *.cs files found AND *.csproj present → "csharp"
IF *.go files found AND go.mod present → "go"
IF *.java files found AND (pom.xml OR build.gradle) present → "java"
// Additional languages may be detected; only sdkLanguages determines what gets generated
```

---

## Symbol Discovery Strategy

### TypeScript / JavaScript

- Parse `export` statements and `export default` declarations.
- Collect all exported interfaces, types, enums, classes, and functions.
- Extract JSDoc comments for descriptions and parameter types.
- For API projects: detect route definitions in Express, Fastify, Hono, NestJS, or similar.

### Python

- Parse `__all__` lists if present; otherwise collect all top-level public symbols (no leading underscore).
- Collect class definitions, function definitions, and type aliases.
- Extract docstrings for descriptions.
- For API projects: detect FastAPI, Flask, or Django route decorators.

### C#

- Parse `public` class, interface, enum, and method declarations.
- Extract XML documentation comments.
- For API projects: detect ASP.NET Core controller actions and route attributes.

### OpenAPI / Swagger

- If a spec file exists, parse it directly as the authoritative source for endpoint and schema definitions.
- Map each path + method combination to a registry Endpoint entry.
- Map each `components/schemas` entry to a registry Schema entry.

---

## Registry Write Protocol

1. Read the existing `Registry.md` to avoid duplicate entries.
2. For each discovered symbol:
   - If a matching `id` already exists: update the entry if the signature or description has changed.
   - If no matching `id` exists: append a new entry.
   - If an existing `id` no longer has a source counterpart: set `deprecated: true` and add a deprecation note.
3. Update `Project Metadata` with the current timestamp and HEAD commit SHA.
4. Append a Changelog entry.

---

## Registry Partitioning Protocol

When the total discovered symbol count ≥ `partitionThresholdSymbols` (default: 500) **or** the
combined Registry file size ≥ `partitionThresholdBytes` (default: 200 KB), the agent MUST switch
to partitioned mode.

### Partition Strategy

The `partitionStrategy` option in `adik.config.json` controls how symbols are assigned to domain
partitions. Three strategies are available:

| Strategy | Description | Best For |
|---|---|---|
| `"auto"` (default) | Infer domains from the first segment of the symbol's namespace hierarchy | Projects with well-structured namespace hierarchies |
| `"manual"` | Use explicit `partitionMappings` in `adik.config.json` to assign namespaces to partition names | Polyglot or flat-namespace projects requiring precise control |
| `"file"` | One partition per top-level source directory (relative to `includePatterns` root) | Monorepo layouts or projects with directory-based domain boundaries |

```jsonc
// adik.config.json — partition strategy examples
{
  "partitionStrategy": "auto",          // default; infer from namespaces

  // — OR —
  "partitionStrategy": "manual",
  "partitionMappings": {
    "payments":   ["payments.*", "billing.*", "invoices.*"],
    "users":      ["users.*", "auth.*", "identity.*"],
    "shared":     ["common.*", "utils.*"]
  },

  // — OR —
  "partitionStrategy": "file",          // one partition per top-level src dir
}
```

When `partitionStrategy` is `"auto"` and all symbols fall into a single partition (common in
flat-namespace Python projects with a single `src/` root), the agent falls back to `"file"`
strategy automatically and logs an advisory. Teams can suppress this by setting
`partitionStrategy: "manual"` with explicit mappings.

### Domain Assignment Rules

```
1. DETERMINE domain assignment for each symbol:

   IF partitionStrategy = "auto":
     - Group by the first segment of the symbol's namespace
     - Symbols used by multiple domains → assign to "shared" domain
     - Example: "payments.transfers.Transfer" → domain "payments"
     - FALLBACK: if all symbols resolve to one domain, switch to "file" strategy

   IF partitionStrategy = "manual":
     - Match each symbol's fully qualified name against partitionMappings glob patterns
     - Unmatched symbols → assign to "shared" domain
     - Example: "billing.Invoice" matches "billing.*" → domain "payments"

   IF partitionStrategy = "file":
     - Use the top-level directory of the symbol's source file (relative to includePatterns root)
     - Example: src/payments/transfer.ts → domain "payments"
     - Files at the root level → assign to "shared" domain

2. WRITE one Registry.<domain>.md file per domain
   - Each file uses the same ADIK marker format as Registry.md
   - Each file has its own Project Metadata and Changelog sections

3. WRITE Registry.index.md
   - Update the Partition Table with: domain, filename, symbol count, timestamp
   - Set registryMode = "partitioned" in index metadata
   - Record the partitionStrategy used in index metadata

4. CHECK vectorization advisory:
   IF totalSymbols >= config.partitionThresholdSymbols
   AND adik.env.json.vectorMode != "active"
   AND config.vectorizationAdvisoryDismissed != true
   AND adik.env.json.vectorizationAdvisoryShown != true:
     EMIT the vectorization advisory prompt (see Registry.index.md)
     SET adik.env.json.vectorizationAdvisoryShown = true

   Note: `vectorizationAdvisoryShown` is a runtime flag in adik.env.json (reset when
   adik.env.json is regenerated). `vectorizationAdvisoryDismissed` is a persistent opt-out
   in adik.config.json (survives regeneration). Use `vectorizationAdvisoryDismissed: true`
   in adik.config.json to permanently suppress the advisory.
```

**Upgrading from monolithic to partitioned:**
If `Registry.md` already exists and the threshold is now exceeded, the agent:
1. Reads all entries from the existing `Registry.md`.
2. Redistributes them into domain partitions as above.
3. Renames (or archives) the original `Registry.md` to avoid confusion.
4. Creates `Registry.index.md` pointing to all partitions.

---

## Execution Protocol

```
1. READ adik.config.json (apply defaults if absent)
2. PROBE environment for vector capabilities → WRITE adik.env.json (vectorMode, storeUri)
3. PERFORM development state check → WRITE state fields to adik.env.json
4. DETECT projectType using Detection Rules
5. DETECT sourceLanguage
6. INFER frameworkHints → WRITE to adik.env.json
7. SCAN source files matching includePatterns, excluding excludePatterns
8. EXTRACT symbols per language strategy
9. COUNT total discovered symbols

10. DETERMINE registryMode:
    IF config.registryMode = "partitioned"
    OR totalSymbols >= config.partitionThresholdSymbols
    OR estimated registry size >= config.partitionThresholdBytes:
      registryMode = "partitioned"
    ELSE:
      registryMode = "monolithic"

11. IF registryMode = "monolithic":
      MERGE symbols into Registry.md
      UPDATE Registry.md Project Metadata
      APPEND Registry.md Changelog entry
    ELSE (partitioned):
      APPLY Registry Partitioning Protocol (see above)

12. CHECK and emit vectorization advisory if conditions met

13. IF adik.env.json vectorMode = "active":
      INVOKE skills/vectorize.skill.md
        inputs: { registry: <registryPath or index>, sourceDir, env: adik.env.json }

14. REPORT summary (including registryMode, inferred frameworkHints, staleArtifacts warnings)
```

---

## Invocation Examples

### Full analysis (first run, monolithic)

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
output: Registry.md
```

### Full analysis with explicit vector store

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
output: Registry.md
vectorStoreUri: http://localhost:8000
embeddingModel: text-embedding-3-small
```

### Full analysis with forced partitioned output

```
@agent codebase-analyst
task: analyse-and-register
target: ./src
output: Registry.index.md
```

### Incremental update (subsequent runs)

```
@agent codebase-analyst
task: diff-and-update
since: abc1234
output: Registry.md
```

### Environment probe only

```
@agent codebase-analyst
task: probe-environment
checks: [vector-db, rag-pipeline, embeddings-config, framework-hints, dev-state]
output: adik.env.json
```

---

## Error Handling

| Condition | Action |
|---|---|
| No source files found matching `includePatterns` | Warn and exit; do not modify Registry |
| Source language cannot be detected | Default to `unknown`; warn user to set manually in config |
| Registry parse error | Abort write; report parse error; preserve existing Registry |
| Symbol with conflicting `id` | Log conflict; keep most recently analysed version |
| Vector DB probe fails | Log warning including which probes were attempted (VECTOR_DB_URL, OPENAI_API_KEY, config file scan) and the reason for each failure; set vectorMode = "inactive" in adik.env.json; continue in document mode |
| Vectorize skill fails | Log error; continue without vector data; vectorMode remains "active" for next run |
| `architecture.md` is malformed or unreadable | Log warning; fall back to package-manifest-based inference |
| Development state mismatch detected | Log warnings in adik.env.json under `staleArtifacts`; do not abort; user can clean up stale directories manually |

---

## Related Files

| File | Role |
|---|---|
| `ADIK.orchestrator.md` | Parent orchestrator |
| `Registry.md` | Output: symbol registry (monolithic) |
| `Registry.index.md` | Output: master index for partitioned registry |
| `Registry.<domain>.md` | Output: domain-scoped registry partitions |
| `adik.env.json` | Output: detected environment capabilities, inferred frameworkHints, dev-state snapshot |
| `adik.config.json` | Configuration (include/exclude patterns, vector options, partition thresholds, etc.) |
| `agents/builder.agent.md` | Downstream agent that consumes the registry |
| `skills/vectorize.skill.md` | Delegate subskill for all vector embedding and upsert operations |
