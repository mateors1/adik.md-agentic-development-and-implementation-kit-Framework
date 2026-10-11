---
name: vectorize
description: Prepare optional semantic retrieval for a producer registry when the developer has configured a vector store.
---

# Vectorize Skill — `skills/vectorize/SKILL.md`

> **Role:** Registry and Codebase Vectorization
> **Type:** Subskill
> **Invoked by:** `agents/codebase-analyst.agent.md`
> **Reads from:** `Registry.md`, source file tree, `adik.env.json`
> **Writes to:** Vector store, `Registry.md` (metadata only)

---

## Purpose

The Vectorize Skill handles all embedding and vector-store interactions for the ADIK framework. It is intentionally isolated from the analysis and build pipelines so that `ADIK.orchestrator.md`, `ADIKbuilder.md`, and the core agents remain lean and free of vector-store specifics.

By keeping vectorization in a dedicated subskill, teams that do not use a vector DB can safely ignore this file without affecting any other part of the framework.

---

## When This Skill Runs

This skill is only invoked when `adik.env.json` reports `vectorMode = "active"`. In all other cases, it is not loaded and has zero impact on context or performance.

```
IF adik.env.json.vectorMode = "active"
  → Invoke this skill after Registry.md is written
ELSE
  → Skip; document mode handles all Registry access
```

---

## Inputs

| Input | Source | Required |
|---|---|---|
| `adik.env.json` | Repository root | Recommended (exit immediately with a warning if absent or if `vectorMode != "active"`) |
| `Registry.md` | Repository root | Yes |
| Source file tree | Repository (per `includePatterns` in `adik.config.json`) | Yes |
| `adik.config.json` | Repository root | No (defaults apply) |

---

## Outputs

| Output | Description |
|---|---|
| Vector store upserts | One embedding per symbol entry; one embedding per source file chunk |
| `Registry.md` metadata update | Sets `vectors.storeUri`, `vectors.lastVectorised`, `vectors.embeddingModel` |

---

## Execution Protocol

```
1. READ adik.env.json → storeUri, embeddingModel, vectorMode
   ASSERT vectorMode = "active"

2. READ Registry.md → extract all symbol entries from ADIK:*:START/END sections

3. EMBED REGISTRY SYMBOLS
   FOR EACH symbol entry in Registry.md:
     a. Build document: "<id> <kind> <name> <signature> <description>"
     b. Embed using embeddingModel
     c. UPSERT into vector store:
          key:     symbol.id
          vector:  <embedding>
          payload: { id, kind, name, namespace, signature, description, deprecated, tags }

4. EMBED CODEBASE
   READ adik.config.json → chunkStrategy (default: "symbol")

   IF chunkStrategy = "symbol":
     FOR EACH source file in includePatterns:
       Parse logical units (functions, classes, methods, modules)
       FOR EACH logical unit:
         EMBED unit source text
         UPSERT into vector store:
           key:     "<filePath>#<unitIndex>"
           vector:  <embedding>
           payload: { filePath, unitIndex, kind, name, language }

   IF chunkStrategy = "file":
     FOR EACH source file in includePatterns:
       EMBED full file text (truncated to model max tokens)
       UPSERT into vector store:
         key:     "<filePath>#0"
         vector:  <embedding>
         payload: { filePath, unitIndex: 0, kind: "file", name: filePath, language }

   IF chunkStrategy = "sliding-window":
     FOR EACH source file in includePatterns:
       SPLIT file into overlapping windows (windowSize: 512 tokens, overlap: 64 tokens)
       FOR EACH window:
         EMBED window text
         UPSERT into vector store:
           key:     "<filePath>#<windowIndex>"
           vector:  <embedding>
           payload: { filePath, windowIndex, kind: "window", name: filePath, language }

5. UPDATE Registry.md Project Metadata (within the metadata YAML block only):
     vectors.storeUri      = storeUri
     vectors.lastVectorised = <ISO-8601 timestamp>
     vectors.embeddingModel = embeddingModel
```

---

## Chunk Strategy Reference

| Strategy | Best For | Chunk Unit |
|---|---|---|
| `symbol` (default) | Most codebases; preserves semantic boundaries | One chunk per function, class, or module |
| `file` | Small repos with large files; fast indexing | One chunk per source file |
| `sliding-window` | Large files with mixed content; thorough coverage | Overlapping fixed-size windows |

---

## Incremental Vectorization

When called in incremental mode (e.g., after a `diff-and-update` task), this skill only re-embeds changed or new symbols and source chunks:

```
1. READ Registry.md Changelog for symbols added/modified since lastVectorised
2. FOR EACH changed symbol:
     Re-embed and UPSERT (overwriting previous embedding keyed by symbol.id)
3. FOR EACH changed source file:
     Re-chunk and UPSERT (overwriting previous embeddings keyed by filePath#index)
4. UPDATE Registry.md vectors.lastVectorised
```

---

## Invocation Examples

### Vectorize after full analysis

```
@skill vectorize
registry: Registry.md
sourceDir: ./src
env: adik.env.json
```

### Incremental vectorization after diff

```
@skill vectorize
registry: Registry.md
sourceDir: ./src
env: adik.env.json
mode: incremental
since: <last-vectorised-timestamp>
```

---

## Error Handling

| Condition | Action |
|---|---|
| `adik.env.json` not found or `vectorMode != "active"` | Exit immediately; log "Vectorize skill skipped (document mode)" |
| Vector store connection fails | Log error with storeUri; do not update `Registry.md`; caller continues without vector data |
| Embedding API fails for a symbol | Log symbol ID and error; skip this symbol; continue with remaining symbols |
| Embedding API rate-limited | Retry with exponential backoff (max 5 retries); if still failing, log and skip |
| `Registry.md` metadata write fails | Log error; vector store may be ahead of metadata — next run will catch up |

---

## Related Files

| File | Role |
|---|---|
| `agents/codebase-analyst.agent.md` | Invoker of this skill |
| `Registry.md` | Source of symbol entries and target for metadata updates |
| `adik.env.json` | Vector store connection details and vectorMode flag |
| `adik.config.json` | `vectors.chunkStrategy`, `vectors.embeddingModel`, `includePatterns` |
| `ADIK.orchestrator.md` | Root orchestrator; defines vector detection policy |
