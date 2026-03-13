# Codebase Analyst Agent — `agents/codebase-analyst.agent.md`

> **Role:** Codebase Analysis Subagent
> **Type:** Analysis Agent
> **Invoked by:** `ADIK.md`
> **Writes to:** `Registry.md`, `adik.env.json`

---

## Purpose

The Codebase Analyst Agent is the intelligence layer of the ADIK framework. It reads the source repository and produces a structured, language-agnostic representation of every public symbol, endpoint, type, and schema in `Registry.md`. It is always the first agent to run in the ADIK pipeline.

This agent does not generate any SDK code. Its responsibilities are accurate, complete, and up-to-date population of the Registry, plus environment probing for vector and RAG capabilities.

---

## Responsibilities

1. **Probe the environment** — detect whether a vector DB or RAG pipeline is available; write results to `adik.env.json`.
2. **Detect project type** — classify the repository as `api`, `service`, or `library` using the heuristics defined in `ADIK.md`.
3. **Discover public symbols** — scan all included source files for exported/public functions, classes, interfaces, enumerations, schemas, and endpoint definitions.
4. **Parse documentation** — extract inline documentation (JSDoc, docstrings, XML docs, OpenAPI descriptions) to populate symbol descriptions.
5. **Populate `Registry.md`** — write all discovered symbols into the appropriate registry sections using the canonical YAML format.
6. **Vectorize Registry and codebase** — when vector mode is active (per `adik.env.json`), embed each symbol entry and each source file chunk and upsert them into the configured vector store.
7. **Detect drift** — in incremental mode, compare the current source against the last registered commit and emit only changed symbols.
8. **Flag breaking changes** — mark any removed or signature-changed symbols as deprecated with a note, rather than silently deleting them.

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
| Updated `Registry.md` | All discovered symbols written to the canonical registry format |
| `Project Metadata` section | `projectType`, `sourceLanguage`, `lastAnalysed`, `lastAnalysedCommit`, `vectors.storeUri` (if vectorized) |
| `adik.env.json` | Detected environment capabilities including vector DB availability |

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

### Project Type Detection

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

## Execution Protocol

```
1. READ adik.config.json (apply defaults if absent)
2. PROBE environment for vector capabilities → WRITE adik.env.json
3. DETECT projectType using Detection Rules
4. DETECT sourceLanguage
5. SCAN source files matching includePatterns, excluding excludePatterns
6. EXTRACT symbols per language strategy
7. MERGE symbols into Registry.md
8. UPDATE Registry.md Project Metadata (including vectors.storeUri if vectorized)
9. IF adik.env.json vectorMode = "active":
   a. EMBED each symbol entry (id + kind + name + signature + description)
   b. UPSERT embeddings into vector store (keyed by symbol id)
   c. CHUNK source files per adik.config.json vectors.chunkStrategy:
      - "symbol": one chunk per logical unit (function body, class definition, module)
      - "file": one chunk per source file
      - "sliding-window": overlapping fixed-size token windows across each file
   d. EMBED each chunk
   e. UPSERT codebase chunk embeddings (keyed by file path + chunk index)
   f. UPDATE Registry.md vectors.lastVectorised and vectors.storeUri
10. APPEND Registry.md Changelog entry
11. REPORT summary to ADIK.md
```

---

## Invocation Examples

### Full analysis (first run)

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
checks: [vector-db, rag-pipeline, embeddings-config]
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
| Embedding or upsert fails | Log error per symbol; continue with remaining symbols; do not abort analysis |

---

## Related Files

| File | Role |
|---|---|
| `ADIK.md` | Parent orchestrator; defines vector detection logic |
| `Registry.md` | Output: symbol registry |
| `adik.env.json` | Output: detected environment capabilities |
| `adik.config.json` | Configuration (include/exclude patterns, vector options, etc.) |
| `agents/builder.agent.md` | Downstream agent that consumes the registry |
