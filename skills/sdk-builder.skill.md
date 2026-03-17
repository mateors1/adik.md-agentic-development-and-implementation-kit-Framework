# SDK Builder Skill — `skills/sdk-builder.skill.md`

> **Role:** SDK Code Generation
> **Type:** Skill
> **Invoked by:** `agents/builder.agent.md`
> **Reads from:** `Registry.md`

---

## Purpose

The SDK Builder Skill generates publish-ready SDK packages for a given target language from the symbols declared in `Registry.md`. It is invoked once per target language and produces a self-contained package directory that can be published to npm, PyPI, or NuGet independently.

This skill understands the differences between an **API SDK** (HTTP client with typed request/response models), a **Service SDK** (event-driven or RPC client), and a **Library SDK** (direct re-export of types and a thin wrapper), and applies the appropriate generation template for each.

---

## Inputs

| Input | Type | Description |
|---|---|---|
| `registry` | path | Path to `Registry.md` |
| `language` | enum | `typescript` \| `python` \| `csharp` |
| `projectType` | enum | `api` \| `service` \| `library` |
| `outputDir` | path | Root output path (e.g. `./sdk`) |
| `packageName` | string | Optional override for the package name |
| `packageVersion` | string | Optional override (default: mirrors source project version) |

---

## Outputs

### TypeScript

```
sdk/typescript/
├── package.json
├── tsconfig.json
├── README.md
├── src/
│   ├── index.ts              ← barrel export
│   ├── client.ts             ← typed HTTP / RPC client (api/service) or re-export (library)
│   ├── models/
│   │   ├── <ClassName>.ts    ← one file per class in Registry
│   │   └── index.ts
│   ├── types/
│   │   ├── <TypeName>.ts     ← interfaces, type aliases, enums
│   │   └── index.ts
│   └── errors/
│       ├── <ErrorName>.ts    ← error classes from Registry error catalogue
│       └── index.ts
└── dist/                     ← populated after `npm run build`
```

### Python

```
sdk/python/
├── pyproject.toml
├── README.md
├── <package_name>/
│   ├── __init__.py           ← public API surface
│   ├── client.py             ← typed HTTP / RPC client
│   ├── models/
│   │   ├── __init__.py
│   │   └── <class_name>.py   ← dataclass per registry class
│   ├── types.py              ← enums, type aliases
│   └── errors.py             ← exception classes from registry error catalogue
└── tests/
    └── test_models.py        ← basic round-trip serialization tests
```

### C\#

```
sdk/csharp/
├── <PackageName>.csproj
├── README.md
├── Client/
│   └── <PackageName>Client.cs   ← typed HttpClient wrapper
├── Models/
│   └── <ClassName>.cs            ← one file per class in Registry
├── Enums/
│   └── <EnumName>.cs             ← enumerations
├── Exceptions/
│   └── <ErrorName>.cs            ← exception classes
└── <PackageName>.sln
```

---

## Generation Rules

### Naming Conventions

| Registry Kind | TypeScript | Python | C# |
|---|---|---|---|
| Class | `PascalCase` | `PascalCase` | `PascalCase` |
| Interface | `IPascalCase` | `Protocol` / ABC | `IPascalCase` |
| Enum | `PascalCase` | `PascalCase(Enum)` | `PascalCase` |
| Function/Method | `camelCase` | `snake_case` | `PascalCase` |
| Property | `camelCase` | `snake_case` | `PascalCase` |
| File name | `kebab-case.ts` | `snake_case.py` | `PascalCase.cs` |

### Type Mapping

| Registry Type | TypeScript | Python | C# |
|---|---|---|---|
| `string` | `string` | `str` | `string` |
| `number` | `number` | `float` | `double` |
| `integer` | `number` | `int` | `int` |
| `boolean` | `boolean` | `bool` | `bool` |
| `date` | `Date` | `datetime` | `DateTimeOffset` |
| `array<T>` | `T[]` | `list[T]` | `List<T>` |
| `map<K,V>` | `Record<K,V>` | `dict[K, V]` | `Dictionary<K,V>` |
| `optional<T>` | `T \| undefined` | `T \| None` | `T?` |
| `any` | `unknown` | `Any` | `object` |

### SDK Template Selection

```
IF projectType == "api":
  → Generate typed HTTP client with one method per endpoint in Registry
  → Each method accepts a strongly-typed request model and returns a typed response model
  → Include request/response serialization and error unwrapping

ELSE IF projectType == "service":
  → Generate typed event emitter / RPC client
  → One method per service operation in Registry
  → Include connection management and retry logic stubs

ELSE IF projectType == "library":
  → Re-export all Registry types and wrap exported functions in a thin facade
  → No HTTP client; focus on type fidelity and convenience helpers
```

---

## Per-Language Generation Steps

### TypeScript

1. Read all `ADIK:CLASSES`, `ADIK:INTERFACES`, `ADIK:ENUMS`, `ADIK:SCHEMAS`, and `ADIK:ENDPOINTS` sections.
2. Generate `models/<ClassName>.ts` for each class, with full JSDoc.
3. Generate `types/<TypeName>.ts` for each interface, type alias, and enum.
4. Generate `errors/<ErrorName>.ts` for each error catalogue entry.
5. Generate `client.ts` with one typed async method per endpoint (API/service) or re-export (library).
6. Generate `src/index.ts` barrel exporting all public symbols.
7. Emit `package.json` with correct `name`, `version`, `main`, `types`, and `exports` fields.
8. Emit `tsconfig.json` configured for `ESNext` output and declaration files.

### Python

1. Read all registry sections.
2. Generate `models/<class_name>.py` as a `@dataclass` with type-annotated fields.
3. Generate `types.py` containing all enums (inheriting `enum.Enum`) and type aliases.
4. Generate `errors.py` containing custom exception classes.
5. Generate `client.py` with `httpx`-based async client (API/service) or thin wrapper (library).
6. Generate `__init__.py` with `__all__` exporting the public API surface.
7. Emit `pyproject.toml` with correct metadata and dependencies.

### C\#

1. Read all registry sections.
2. Generate `Models/<ClassName>.cs` as a `record` or `class` with properties and `System.Text.Json` attributes.
3. Generate `Enums/<EnumName>.cs` for each enumeration.
4. Generate `Exceptions/<ErrorName>.cs` for each error catalogue entry.
5. Generate `Client/<PackageName>Client.cs` wrapping `HttpClient` with typed methods (API/service) or direct wrapper (library).
6. Emit `<PackageName>.csproj` with correct `PackageId`, `Version`, `TargetFramework`, and dependencies.

---

## Quality Requirements

- All generated files must pass the standard linter/formatter for the target language (ESLint + Prettier, Black + mypy, dotnet format).
- All generated classes must include serialization support (JSON by default).
- All generated clients must include a configurable base URL / connection string.
- Deprecated registry symbols must be annotated with the language-appropriate deprecation marker (`@deprecated`, `warnings.deprecated`, `[Obsolete]`).
- Every generated package README must include a quick-start usage example.

---

## Related Files

| File | Role |
|---|---|
| `Registry.md` | Source of truth consumed by this skill |
| `agents/builder.agent.md` | Invoker of this skill |
| `skills/sdk-consumer.skill.md` | Sibling skill generating consumption boilerplate |
| `ADIK.orchestrator.md` | Root orchestrator |
