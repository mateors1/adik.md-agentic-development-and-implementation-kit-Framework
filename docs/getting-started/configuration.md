# ADIK Configuration Reference

> **File:** `adik.config.json` (optional — placed in the target repository root)
> **Used by:** `ADIK.orchestrator.md`, `agents/codebase-analyst.agent.md`, `agents/builder.agent.md`

If this file is absent, all defaults apply. Every field is optional.

```jsonc
{
  "projectType": "auto",            // "auto" | "api" | "service" | "library"
  "sdkLanguages": ["typescript", "python", "csharp"],   // tier-1 (always available)
  "tier2Languages": [],             // opt-in: [] | ["go"] | ["java"] | ["kotlin"] | any combination
  "tier2Options": {
    "go": {
      "modulePath": "",             // e.g. "github.com/acme/myapi-sdk-go"
      "goVersion": "1.21"
    },
    "java": {
      "groupId": "",                // e.g. "com.acme"
      "artifactId": "",             // e.g. "myapi-sdk"
      "javaVersion": "17",
      "buildTool": "maven"          // "maven" | "gradle"
    },
    "kotlin": {
      "groupId": "",
      "artifactId": "",
      "javaVersion": "17",
      "buildTool": "gradle"
    }
  },
  "outputDir": "./sdk",
  "registryPath": "./Registry.md",
  "registryMode": "auto",           // "auto" | "monolithic" | "partitioned"
  "partitionStrategy": "auto",      // "auto" | "manual" | "file" (controls domain assignment)
  "partitionMappings": {},           // used when partitionStrategy = "manual"; maps domain → glob patterns
  "partitionThresholdSymbols": 500, // trigger partitioned mode above this symbol count
  "partitionThresholdBytes": 204800, // or above this file size (200 KB)
  "vectorizationAdvisoryDismissed": false,  // set true to suppress advisory
  "mcpPort": 3100,
  "syncOnCommit": true,             // re-run analysis on every commit
  "nonInteractive": false,          // true = headless mode (no startup prompt)
  "startupMode": "blanket",         // "blanket" | "guided" (used in non-interactive mode)
  "includePatterns": ["src/**/*"],
  "excludePatterns": ["**/*.test.*", "**/*.spec.*"],
  "vectors": {
    "bundled": false,               // true if embeddings are distributed with this adik
    "autoDetect": true,             // probe environment for vector DB / RAG capabilities
    "preferVectors": true,          // use vector search over document parsing when available
    "storeUri": "",                 // explicit vector store URI (overrides auto-detection)
    "embeddingModel": "auto",       // "auto" | explicit model name
    "chunkStrategy": "symbol"       // "symbol" | "file" | "sliding-window"
  }
}
```

---

## Field Reference

### Core

| Field | Type | Default | Description |
|---|---|---|---|
| `projectType` | string | `"auto"` | Force project classification. `"auto"` lets the Codebase Analyst detect it. |
| `sdkLanguages` | string[] | `["typescript", "python", "csharp"]` | Tier-1 languages to generate. |
| `tier2Languages` | string[] | `[]` | Opt-in tier-2 languages (`"go"`, `"java"`, `"kotlin"`). |
| `outputDir` | string | `"./sdk"` | Root directory for generated SDK packages. |

### Registry

| Field | Type | Default | Description |
|---|---|---|---|
| `registryPath` | string | `"./Registry.md"` | Path to the monolithic registry file. |
| `registryMode` | string | `"auto"` | `"auto"` switches to partitioned above thresholds. |
| `partitionStrategy` | string | `"auto"` | How symbols are assigned to domain partitions. |
| `partitionMappings` | object | `{}` | Manual domain → glob mappings (when strategy is `"manual"`). |
| `partitionThresholdSymbols` | number | `500` | Symbol count that triggers partitioning. |
| `partitionThresholdBytes` | number | `204800` | File size (bytes) that triggers partitioning. |

### Behaviour

| Field | Type | Default | Description |
|---|---|---|---|
| `syncOnCommit` | boolean | `true` | Re-run analysis pipeline on every commit. |
| `nonInteractive` | boolean | `false` | Skip startup prompt (CI/CD mode). |
| `startupMode` | string | `"blanket"` | Default mode when non-interactive. |
| `includePatterns` | string[] | `["src/**/*"]` | Glob patterns for source files to scan. |
| `excludePatterns` | string[] | `["**/*.test.*", "**/*.spec.*"]` | Glob patterns to exclude from scanning. |

### Vectors

| Field | Type | Default | Description |
|---|---|---|---|
| `vectors.bundled` | boolean | `false` | Whether pre-computed embeddings ship with this adik. |
| `vectors.autoDetect` | boolean | `true` | Probe environment for vector DB availability. |
| `vectors.preferVectors` | boolean | `true` | Prefer semantic search over document parsing. |
| `vectors.storeUri` | string | `""` | Explicit vector store URI (overrides auto-detection). |
| `vectors.embeddingModel` | string | `"auto"` | Embedding model for vectorization. |
| `vectors.chunkStrategy` | string | `"symbol"` | Chunking strategy: `"symbol"`, `"file"`, or `"sliding-window"`. |

### Tier-2 Options

Each tier-2 language can be configured with language-specific options under `tier2Options`:

**Go:** `modulePath` (Go module path), `goVersion` (minimum Go version).

**Java:** `groupId`, `artifactId`, `javaVersion`, `buildTool` (`"maven"` or `"gradle"`).

**Kotlin:** `groupId`, `artifactId`, `javaVersion`, `buildTool` (typically `"gradle"`).

---

## Minimal Examples

**Default (no config needed):**
```jsonc
// No adik.config.json — all defaults apply
// Generates TypeScript, Python, C# SDKs in ./sdk/
```

**TypeScript + Python only:**
```json
{
  "sdkLanguages": ["typescript", "python"]
}
```

**With Go tier-2:**
```json
{
  "sdkLanguages": ["typescript", "python"],
  "tier2Languages": ["go"],
  "tier2Options": {
    "go": { "modulePath": "github.com/myorg/myapi-sdk-go" }
  }
}
```

**CI/CD headless:**
```json
{
  "nonInteractive": true,
  "startupMode": "blanket",
  "syncOnCommit": true
}
```

**Spec Kit integration (scan `.specify/` contract artifacts):**
```json
{
  "includePatterns": [
    "src/**/*",
    ".specify/specs/*/contracts/api-spec.json"
  ],
  "partitionStrategy": "manual",
  "partitionMappings": {
    "create-taskify": ".specify/specs/001-create-taskify/**/*",
    "user-profiles": ".specify/specs/002-user-profiles/**/*"
  }
}
```

> **Tip:** When using [GitHub Spec Kit](https://github.com/github/spec-kit), point `includePatterns` at the `.specify/specs/*/contracts/` directory so the Codebase Analyst can read `api-spec.json` as a first-class OpenAPI source. Use `partitionStrategy: "manual"` with `partitionMappings` to align Registry partitions to Spec Kit's feature-branch naming convention (`001-feature-name`). See [ADIK & Spec Kit Integration Guide](../ecosystem/integration-guide.md) for the full workflow.
