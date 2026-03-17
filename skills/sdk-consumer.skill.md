# SDK Consumer Skill — `skills/sdk-consumer.skill.md`

> **Role:** SDK Consumption Boilerplate Generation
> **Type:** Skill
> **Invoked by:** `agents/builder.agent.md`
> **Reads from:** `Registry.md`, generated SDK packages in `sdk/<language>/`

---

## Purpose

The SDK Consumer Skill generates ready-to-use integration boilerplate that helps developers adopt the generated SDK with zero friction. Where the SDK Builder Skill produces the SDK *library itself*, this skill produces the *consumer-side* code: examples, service stubs, adapter classes, serialization helpers, and dependency injection wiring — everything a developer needs to drop the SDK into an existing project.

This skill ensures that the generated SDK is not just correct but immediately usable.

> **⚠️ EXECUTION MANDATE:** When invoked, this skill must **write actual source code files**
> to disk — real example scripts, real DI wiring code, real retry wrappers. Each file must
> contain complete, runnable source code, not placeholders or summaries.

---

## Inputs

| Input | Type | Required | Description |
|---|---|---|---|
| `registry` | path | Yes | Path to `Registry.md` |
| `language` | enum | Yes | `typescript` \| `python` \| `csharp` |
| `projectType` | enum | Yes | `api` \| `service` \| `library` |
| `outputDir` | path | Yes | Root output path (e.g. `./sdk`) |
| `frameworkHints` | string[] | No | Target frameworks — **auto-inferred if not provided** (see below) |

### Framework Hints Auto-Inference

When `frameworkHints` is not explicitly provided, this skill reads `adik.env.json` for hints inferred by the Codebase Analyst Agent. The inference precedence is:

1. **Explicit invocation parameter** — always wins.
2. **`adik.env.json.frameworkHints` non-empty array** — populated by the Codebase Analyst Agent from `architecture.md`, package manifests, and existing agent/skill files.
3. **`adik.env.json` present but `frameworkHints` missing, null, or empty** — treated the same as case 4; fall through to generic boilerplate.
4. **`adik.env.json` not present** — generic, framework-neutral boilerplate is generated.

This means that in the typical workflow, `frameworkHints` never needs to be set manually; ADIK discovers the target framework automatically.

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

All consumer skills generate a retry wrapper stub with configurable:

- Maximum retry count (default: 3).
- Backoff strategy: `linear` | `exponential` | `none`.
- Retry condition: retries on network errors and 5xx responses by default.

---

## Serialization Rules

### Date Handling

All date/time fields are serialized to ISO-8601 strings and deserialized to the language's native date type:

- TypeScript: `Date`
- Python: `datetime.datetime`
- C#: `DateTimeOffset`

### Null / Optional Handling

- TypeScript: `undefined` fields are omitted from serialized JSON.
- Python: `None` fields are omitted using `dataclasses.asdict` with a custom filter.
- C#: Nullable reference types use `JsonIgnore(Condition = WhenWritingNull)`.

### Enum Handling

Enums are serialized as their string name (not numeric value) by default, for maximum interoperability with the source service.

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
| `Registry.md` | Source of truth consumed by this skill |
| `agents/builder.agent.md` | Invoker of this skill |
| `skills/sdk-builder.skill.md` | Sibling skill generating the SDK packages |
| `ADIK.orchestrator.md` | Root orchestrator |
