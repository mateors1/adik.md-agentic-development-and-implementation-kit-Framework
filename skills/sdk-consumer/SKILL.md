---
name: sdk-consumer
description: Generate library-specific implementation skills, references, and examples matching newly generated SDK code.
---

# SDK Consumer Skill — `skills/sdk-consumer/SKILL.md`

> **Role:** Producer-side implementation-kit generation
> **Type:** Skill
> **Invoked by:** `agents/builder.agent.md`
> **Reads from:** `contracts/registry.json` (or normalized legacy Registry), generated SDK packages in `sdk/<language>/`

---

## Purpose

The SDK Consumer Skill generates ready-to-use integration boilerplate that helps developers adopt the generated SDK with zero friction. Where the SDK Builder Skill produces the SDK *library itself*, this skill produces the *consumer-side* code: examples, service stubs, adapter classes, serialization helpers, and dependency injection wiring — everything a developer needs to drop the SDK into an existing project.

Generate a native implementation skill alongside these assets. Validate its guidance
against the emitted SDK and report only checks actually run.

> **⚠️ EXECUTION MANDATE:** When invoked, this skill must **write actual source code files**
> to disk — real example scripts, real DI wiring code, real retry wrappers. Each file must
> contain complete, runnable source code, not placeholders or summaries.

---

## Inputs

| Input | Type | Required | Description |
|---|---|---|---|
| `registry` | path | Yes | Path to `contracts/registry.json` (or normalized legacy Registry) |
| `language` | enum | Yes | `typescript` \| `python` \| `csharp` |
| `projectType` | enum | Yes | `api` \| `service` \| `library` |
| `outputDir` | path | Yes | Root output path (e.g. `generated/my-adik`) |
| `frameworkHints` | string[] | No | Supported consumer frameworks; use `consumerFrameworks` or framework-neutral recipes |

### Producer and consumer frameworks

`consumerFrameworks` in producer configuration lists supported consumer environments.
Explicit invocation hints override it. Producer `adik.env.json.frameworkHints` describes
how the library is built and MUST NOT choose the consumer application's framework.
When no consumer framework is declared, generate framework-neutral recipes. At consumption
time, the generated implementation skill inspects the application's manifests and composition
root, then selects a supported recipe. State unsupported environments explicitly.

---

## Outputs

### TypeScript

```
sdk/typescript/
├── examples/
│   ├── basic-usage.ts              ← minimal end-to-end usage example
│   ├── error-handling.ts           ← demonstrates error handling patterns
│   └── advanced/
│       └── dependency-injection.ts ← DI wiring example (NestJS / InversifyJS)
└── boilerplate/
    ├── client-factory.ts           ← factory function for creating configured client instances
    ├── retry-wrapper.ts            ← retry + exponential backoff wrapper
    └── serialization-helpers.ts    ← JSON serialization / deserialization utilities
```

### Python

```
sdk/python/
├── examples/
│   ├── basic_usage.py              ← minimal end-to-end usage example
│   ├── error_handling.py           ← demonstrates error handling patterns
│   └── advanced/
│       └── dependency_injection.py ← DI wiring example (FastAPI / dependency-injector)
└── boilerplate/
    ├── client_factory.py           ← factory function for creating configured client instances
    ├── retry_wrapper.py            ← retry + exponential backoff wrapper
    └── serialization_helpers.py    ← Pydantic / dataclass serialization utilities
```

### C\#

```
sdk/csharp/
├── Examples/
│   ├── BasicUsage.cs               ← minimal end-to-end usage example
│   ├── ErrorHandling.cs            ← demonstrates error handling patterns
│   └── Advanced/
│       └── DependencyInjection.cs  ← IServiceCollection extension method wiring
└── Boilerplate/
    ├── ClientFactory.cs            ← factory class for creating configured client instances
    ├── RetryHandler.cs             ← DelegatingHandler with retry + backoff
    └── SerializationHelpers.cs     ← System.Text.Json serialization utilities
```

---

## Generation Rules

### Example Generation

For each endpoint or exported function in the Registry, this skill generates an example call showing:

- How to instantiate the client with a base URL / connection string and authentication.
- How to call the method with representative parameter values.
- How to handle success and error responses.

```typescript
// Example: basic-usage.ts (auto-generated)
import { MyServiceClient } from '@myorg/my-service-sdk';

const client = new MyServiceClient({
  baseUrl: 'https://api.example.com',
  apiKey: process.env.API_KEY,
});

// getUserById
const user = await client.getUserById({ id: '123' });
console.log(user.name);
```

### Serialization Helper Generation

For each Registry class that contains complex nested types or date fields, this skill generates:

- A `serialize(instance) → string` helper.
- A `deserialize(json) → T` helper.
- TypeScript: uses `JSON.parse` / `JSON.stringify` with custom revivers for dates.
- Python: uses `dataclasses.asdict` / `dacite.from_dict` or `pydantic.BaseModel`.
- C#: uses `System.Text.Json.JsonSerializer` with `JsonSerializerOptions`.

### Adapter / Wrapper Generation

When `frameworkHints` are provided, this skill generates framework-specific wrappers:

| Framework Hint | Generated Artifact |
|---|---|
| `react` | `useMyServiceClient` React hook |
| `nestjs` | `MyServiceModule` and `MyServiceProvider` |
| `fastapi` | `Depends(get_client)` dependency |
| `aspnet` | `IServiceCollection.AddMyServiceClient()` extension |
| `angular` | `MyServiceClientModule` and `MyServiceClientService` |

### Retry Wrapper Generation

For SDKs with retryable operations, generate a retry wrapper with configurable:

- Maximum retry count (default: 3).
- Backoff strategy: `linear` | `exponential` | `none`.
- Retry condition: retry only operations the library contract declares safe to repeat; document idempotency keys for mutations. Network failure alone does not establish safe retry.

---

## Serialization Rules

### Date Handling

Follow the producer wire contract. When it specifies ISO-8601 timestamps, use the
appropriate native representation:

- TypeScript: `Date`
- Python: `datetime.datetime`
- C#: `DateTimeOffset`

### Null / Optional Handling

Preserve the producer distinction between explicit null and absent fields. Apply
these omission recipes only when the contract declares them equivalent:

- TypeScript: `undefined` fields are omitted from serialized JSON.
- Python: `None` fields are omitted using `dataclasses.asdict` with a custom filter.
- C#: Nullable reference types use `JsonIgnore(Condition = WhenWritingNull)`.

### Enum Handling

Serialize enums exactly as declared in the producer wire contract, including numeric
values where required. Do not infer wire representation from a language default.

---

## Quality Requirements

- All examples must compile and run against the generated SDK without modification.
- All serialization helpers must round-trip without data loss for all types in the Registry.
- All DI wiring must be idiomatic for the target framework.
- All retry wrappers must include a configurable timeout.
- Comments in generated code must explain *why*, not *what*, to be useful for developers reading the boilerplate.

---

## Related Files

| File | Role |
|---|---|
| `contracts/registry.json` (or normalized legacy Registry) | Source of truth consumed by this skill |
| `agents/builder.agent.md` | Invoker of this skill |
| `skills/sdk-builder/SKILL.md` | Sibling skill generating the SDK packages |
| `ADIK.orchestrator.md` | Root orchestrator |

## Generate the consumer implementation skill

For every completed adik, also write `skills/implement-<library>/SKILL.md` inside
its output bundle. Use YAML frontmatter with `name`, a specific single-line
`description`, and `metadata.sdk-version` equal to the bundle version. Generate this skill
from the actual SDK exports, verified examples, and producer contracts.

The generated procedure MUST:

1. Identify the requested capability and load its recipe and symbol IDs.
2. Check the bundled SDK version. Copy package sources to a temporary build directory
   outside the sealed bundle before installing locally; preserve the bundle inventory.
3. Inspect only the consumer manifests, conventions, composition root, and relevant
   call sites needed for the requested integration.
4. Configure authentication, environment, initialization, and resource lifecycle
   according to the SDK. Read secret values from the consumer's existing mechanism.
5. Implement the user's requested application changes using the actual SDK exports.
6. Run the documented integration checks and report results and unresolved requirements.

Include capability references, framework-neutral or declared framework recipes,
runnable examples, errors and recovery, and known limitations. Link each recipe to
registry symbol IDs. Do not infer the consumer architecture from the producer stack.
The consumer may edit application source as authorized by the user's implementation
request; the producer's source-preservation rule applies to library generation.

Declare all skill paths, languages, symbol IDs, references, and examples in
`adik.manifest.json`. SDK code and these agentic elements share one bundle version.
Use the completed-adik format in `docs/specification/bundle-contract.md` when working
in this repository, or the bundled `schemas/adik-manifest.schema.json` after bootstrap.
