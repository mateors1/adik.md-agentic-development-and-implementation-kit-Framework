# sdk-builder-tier2.skill.md — ADIK Tier-2 SDK Builder Skill

> **Role:** Tier-2 SDK Code Generation (Go and Java/Kotlin)
> **Invoked by:** `agents/builder.agent.md`
> **Reads from:** `Registry.md` (or partitioned registries via `Registry.index.md`)
> **Opt-in:** This skill is **disabled by default**. It is only invoked when the target language
> is explicitly listed in `adik.config.json` under `tier2Languages`.
> **Purpose:** Generates publish-ready Go modules and Java (or Kotlin) packages from the ADIK
> Registry. Mirrors the contract of `skills/sdk-builder.skill.md` for Tier-1 languages.

---

## Opt-In Configuration

```jsonc
// adik.config.json
{
  "sdkLanguages": ["typescript", "python", "csharp"],   // Tier-1 (always available)
  "tier2Languages": ["go", "java"],                     // Tier-2 (opt-in; both optional)
  "tier2Options": {
    "go": {
      "modulePath": "github.com/<org>/<repo>-sdk-go",  // Go module path
      "goVersion": "1.21"
    },
    "java": {
      "groupId": "com.<org>",
      "artifactId": "<repo>-sdk",
      "javaVersion": "17",
      "buildTool": "maven"                              // "maven" | "gradle"
    },
    "kotlin": {
      "groupId": "com.<org>",
      "artifactId": "<repo>-sdk-kotlin",
      "javaVersion": "17",
      "buildTool": "gradle"
    }
  }
}
```

> **Note:** `"java"` and `"kotlin"` are separate entries in `tier2Languages`. Selecting `"java"`
> generates idiomatic Java; selecting `"kotlin"` generates idiomatic Kotlin (coroutines, data
> classes). Both target JVM and can coexist.

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `registry` | path | Yes | Path to `Registry.md` or `Registry.index.md` |
| `language` | string | Yes | `go` \| `java` \| `kotlin` |
| `projectType` | string | Yes | `api` \| `service` \| `library` |
| `outputDir` | path | No | Default `./sdk` |
| `packageName` | string | No | Override the inferred package/module name |
| `packageVersion` | string | No | Override the inferred version |
| `options` | object | No | Language-specific options from `tier2Options` |

---

## Output File Structures

### Go

```
sdk/go/
├── go.mod                        ← module declaration
├── go.sum
├── README.md
├── client/
│   └── client.go                 ← typed HTTP/RPC client
├── models/
│   └── <snake_case>.go           ← one file per struct/type
├── enums/
│   └── <snake_case>.go
└── errors/
    └── errors.go
```

### Java (Maven)

```
sdk/java/
├── pom.xml
├── README.md
└── src/main/java/<groupId>/<artifactId>/
    ├── <PackageName>Client.java
    ├── models/
    │   └── <ClassName>.java      ← POJOs / records (Java 16+)
    ├── enums/
    │   └── <EnumName>.java
    └── exceptions/
        └── <ErrorName>.java
```

### Java (Gradle)

```
sdk/java/
├── build.gradle
├── settings.gradle
├── README.md
└── src/main/java/<groupId>/<artifactId>/
    ├── <PackageName>Client.java
    ├── models/
    │   └── <ClassName>.java
    ├── enums/
    │   └── <EnumName>.java
    └── exceptions/
        └── <ErrorName>.java
```

### Kotlin

```
sdk/kotlin/
├── build.gradle.kts
├── settings.gradle.kts
├── README.md
└── src/main/kotlin/<groupId>/<artifactId>/
    ├── <PackageName>Client.kt    ← suspend fun / coroutines
    ├── models/
    │   └── <ClassName>.kt        ← data class
    ├── enums/
    │   └── <EnumName>.kt
    └── exceptions/
        └── <ErrorName>.kt
```

---

## Naming Conventions

| Registry Kind | Go | Java | Kotlin |
|---|---|---|---|
| Class | PascalCase struct | PascalCase class/record | PascalCase data class |
| Interface | PascalCase interface | IPascalCase interface | IPascalCase interface |
| Enum | PascalCase const block | PascalCase enum | PascalCase enum class |
| Function/Method | camelCase | camelCase | camelCase (suspend if async) |
| Property | camelCase | camelCase | camelCase val/var |
| File name | snake_case.go | PascalCase.java | PascalCase.kt |
| Package | lowercase no underscore | com.org.pkg | com.org.pkg |

---

## Type Mapping

| Registry Type | Go | Java | Kotlin |
|---|---|---|---|
| string | string | String | String |
| number | float64 | double | Double |
| integer | int | int / Integer | Int |
| boolean | bool | boolean / Boolean | Boolean |
| null | nil / pointer | null | null / nullable |
| void | — (no return) | void | Unit |
| any | interface{} / any | Object | Any |
| object | map[string]interface{} | Map\<String,Object\> | Map\<String,Any\> |
| array | []T | List\<T\> | List\<T\> |
| Record\<K,V\> | map[K]V | Map\<K,V\> | Map\<K,V\> |
| Map\<K,V\> | map[K]V | Map\<K,V\> | Map\<K,V\> |
| Set\<T\> | map[T]struct{} | Set\<T\> | Set\<T\> |
| Promise\<T\> | chan T / error | CompletableFuture\<T\> | Deferred\<T\> |
| Date | time.Time | java.time.Instant | java.time.Instant |
| UUID | uuid.UUID (google/uuid) | UUID | UUID |
| Buffer | []byte | byte[] | ByteArray |

---

## Go Generation Rules

1. **Structs** — every Registry `class` and `schema` becomes a Go struct with JSON tags derived
   from the property name using `camelCase` → `snake_case` conversion.
2. **Interfaces** — every Registry `interface` becomes a Go `interface` type.
3. **Enumerations** — every Registry `enum` becomes a `const` block with `iota` where values are
   sequential, or explicit string/int constants otherwise.
4. **Client** — `client/client.go` wraps `net/http` with a typed `Do` method for each endpoint.
   Context is always the first parameter.
5. **Errors** — a sentinel error type per Registry `error` entry using `errors.New` or a custom
   struct implementing the `error` interface.
6. **Module path** — read from `tier2Options.go.modulePath`; if absent, default to
   `github.com/<inferredOrg>/<inferredRepo>-sdk-go`.
7. **go.mod** — specifies `go <version>` from `tier2Options.go.goVersion` (default: `1.21`).

---

## Java Generation Rules

1. **Classes / Records** — Registry `class` and `schema` entries become Java `record` (Java 16+)
   by default, falling back to POJO with Lombok `@Data` if `javaVersion < 16`.
2. **Interfaces** — Registry `interface` entries become Java `interface` declarations.
3. **Enumerations** — Registry `enum` entries become Java `enum` types.
4. **Client** — `<Name>Client.java` uses `java.net.http.HttpClient` (Java 11+) with typed
   request/response pairs for each endpoint.
5. **Exceptions** — each Registry `error` entry becomes a checked or unchecked exception class
   (unchecked by default).
6. **Annotations** — `@JsonProperty` from Jackson for JSON field mapping. Include Jackson
   dependency in `pom.xml` / `build.gradle`.
7. **Build descriptor** — generate `pom.xml` (Maven) or `build.gradle` (Gradle) based on
   `tier2Options.java.buildTool`.

---

## Kotlin Generation Rules

1. **Data Classes** — Registry `class` and `schema` entries become Kotlin `data class` with
   `@Serializable` annotation (kotlinx.serialization).
2. **Interfaces** — Registry `interface` entries become Kotlin `interface` declarations.
3. **Enumerations** — Registry `enum` entries become Kotlin `enum class`.
4. **Client** — uses Ktor (`io.ktor:ktor-client-core`) with `suspend` functions for async calls.
5. **Coroutines** — all endpoint calls return `suspend` functions.
6. **Null safety** — nullable types use Kotlin `?` syntax; non-nullable types are strict.
7. **Build descriptor** — always `build.gradle.kts` (Gradle Kotlin DSL).

---

## Execution Protocol

```
1. ASSERT language ∈ {go, java, kotlin}
   IF language not recognized → ABORT with error

2. READ registry (honoring partitioned index if present)

3. VALIDATE registry via registry-validator.skill.md
   IF exitStatus = "FAIL" → ABORT

4. RESOLVE tier2Options for language from adik.config.json

5. FOR EACH symbol in Registry:
   a. Map types using Type Mapping table above
   b. Apply Naming Conventions
   c. Generate language-specific file content

6. WRITE output files to sdk/<language>/

7. WRITE sdk/<language>/README.md with:
   - Package/module identity
   - Install instructions (go get / mvn / gradle)
   - Quick-start example (one endpoint call)
   - Generated from: Registry.md vX.Y at <timestamp>

8. APPEND result to sdk/BUILD_REPORT.md
```

---

## Error Handling

| Condition | Action |
|---|---|
| `tier2Languages` not configured | Skill not invoked (Builder Agent skips tier-2) |
| `language` not in `tier2Languages` | Skip silently |
| Unsupported type mapping | Emit `any` / `Object` / `Any` + WARNING in BUILD_REPORT.md |
| Output directory conflict | Merge: overwrite generated files, preserve manually created files |
| Validation FAIL | Abort; do not write any output for this language |

---

## Invocation Example

```
# Invoked by Builder Agent when tier2Languages includes "go"
@skill sdk-builder-tier2
registry: Registry.md
language: go
projectType: api
outputDir: ./sdk
options:
  modulePath: github.com/acme/payments-sdk-go
  goVersion: "1.22"

# Kotlin
@skill sdk-builder-tier2
registry: Registry.index.md
language: kotlin
projectType: library
outputDir: ./sdk
options:
  groupId: com.acme
  artifactId: payments-sdk-kotlin
  javaVersion: "17"
  buildTool: gradle
```
