# Cheat Sheet — Consuming a Generated SDK

> **Audience:** Developers integrating an ADIK-generated SDK into their application.
> **Full guide:** [Quickstart Guide](quickstart-guide.md) | **Building side:** [Cheat Sheet — Building](cheatsheet-building.md)

---

## 1. What You Get

After the ADIK pipeline runs, the `sdk/` folder contains publish-ready packages:

```
sdk/
├── typescript/          # npm-ready package
│   ├── src/             # Client classes, models, enums
│   ├── examples/        # Ready-to-run usage examples
│   ├── boilerplate/     # Retry wrapper, serialization helpers, DI wiring
│   ├── package.json
│   └── tsconfig.json
├── python/              # pip-ready package
│   ├── src/             # Client module, models, enums
│   ├── examples/        # Ready-to-run usage examples
│   ├── boilerplate/     # Retry wrapper, serialization helpers, DI wiring
│   ├── setup.py / pyproject.toml
│   └── requirements.txt
├── csharp/              # NuGet-ready package
│   ├── src/             # Client, models, enums
│   ├── Examples/        # Ready-to-run usage examples
│   ├── Boilerplate/     # Retry handler, serialization helpers, DI wiring
│   └── *.csproj
├── BUILD_REPORT.md
└── VALIDATION_REPORT.md
```

Tier-2 languages (Go, Java, Kotlin) follow the same pattern when enabled.

---

## 2. Install

### TypeScript / JavaScript

```bash
# From a local path
npm install ../path-to-project/sdk/typescript

# Or publish first, then install as a normal package
cd sdk/typescript && npm publish --access public
npm install @myorg/my-service-sdk
```

### Python

```bash
# From a local path
pip install ../path-to-project/sdk/python

# Or publish first
cd sdk/python && pip install build && python -m build && twine upload dist/*
pip install my-service-sdk
```

### C\#

```bash
# Add local project reference
dotnet add reference ../path-to-project/sdk/csharp/MyService.Sdk.csproj

# Or pack and push to NuGet
cd sdk/csharp && dotnet pack -c Release
dotnet nuget push bin/Release/*.nupkg --source https://api.nuget.org/v3/index.json
```

---

## 3. Create a Client

### TypeScript

```typescript
import { MyServiceClient } from '@myorg/my-service-sdk';

const client = new MyServiceClient({
  baseUrl: 'https://api.example.com',
  apiKey: process.env.API_KEY,
});
```

### Python

```python
from my_service_sdk import MyServiceClient

client = MyServiceClient(
    base_url="https://api.example.com",
    api_key=os.environ["API_KEY"],
)
```

### C\#

```csharp
using MyService.Sdk;

var client = new MyServiceClient(new MyServiceClientOptions
{
    BaseUrl = "https://api.example.com",
    ApiKey = Environment.GetEnvironmentVariable("API_KEY"),
});
```

> **Tip:** Use the `client-factory` boilerplate file for a pre-configured factory with defaults.

---

## 4. Make Calls

```typescript
// TypeScript
const user = await client.getUserById({ id: '123' });
console.log(user.name);

const result = await client.createOrder({
  productId: 'abc',
  quantity: 2,
});
```

```python
# Python
user = client.get_user_by_id(id="123")
print(user.name)

result = client.create_order(product_id="abc", quantity=2)
```

```csharp
// C#
var user = await client.GetUserByIdAsync("123");
Console.WriteLine(user.Name);

var result = await client.CreateOrderAsync(new CreateOrderRequest
{
    ProductId = "abc",
    Quantity = 2,
});
```

> **Tip:** Check `sdk/<language>/examples/basic-usage.*` for a complete working example.

---

## 5. Handle Errors

Every generated SDK follows a consistent error pattern:

```typescript
// TypeScript
try {
  const user = await client.getUserById({ id: '123' });
} catch (err) {
  if (err instanceof ApiError) {
    console.error(`API Error ${err.statusCode}: ${err.message}`);
  }
}
```

```python
# Python
try:
    user = client.get_user_by_id(id="123")
except ApiError as e:
    print(f"API Error {e.status_code}: {e.message}")
```

```csharp
// C#
try
{
    var user = await client.GetUserByIdAsync("123");
}
catch (ApiException ex)
{
    Console.Error.WriteLine($"API Error {ex.StatusCode}: {ex.Message}");
}
```

> **Tip:** See `sdk/<language>/examples/error-handling.*` for the full error-handling example.

---

## 6. Use Boilerplate Helpers

The SDK Consumer Skill generates ready-to-use helpers in `sdk/<language>/boilerplate/`:

| File | What It Does |
|------|-------------|
| `client-factory.*` | Pre-configured factory with env-var defaults |
| `retry-wrapper.*` | Retry with exponential backoff (configurable max retries, strategy) |
| `serialization-helpers.*` | Round-trip JSON ↔ model conversion, date handling |

### Retry Wrapper

```typescript
// TypeScript — wrap any client call with automatic retries
import { withRetry } from './boilerplate/retry-wrapper';

const user = await withRetry(() => client.getUserById({ id: '123' }), {
  maxRetries: 3,
  backoff: 'exponential',
});
```

```python
# Python
from boilerplate.retry_wrapper import with_retry

user = with_retry(lambda: client.get_user_by_id(id="123"), max_retries=3)
```

---

## 7. Framework Integration (DI Wiring)

When framework hints are detected, ADIK generates idiomatic dependency injection wiring.

### NestJS

```typescript
import { MyServiceModule } from './boilerplate/dependency-injection';

@Module({ imports: [MyServiceModule.register({ apiKey: process.env.API_KEY })] })
export class AppModule {}
```

### FastAPI

```python
from boilerplate.dependency_injection import get_client

@app.get("/users/{user_id}")
async def get_user(user_id: str, client = Depends(get_client)):
    return client.get_user_by_id(id=user_id)
```

### ASP.NET

```csharp
// Program.cs / Startup.cs
builder.Services.AddMyServiceClient(options =>
{
    options.BaseUrl = "https://api.example.com";
    options.ApiKey = builder.Configuration["ApiKey"];
});
```

> **No framework detected?** Generic boilerplate is generated. You can re-run with explicit hints by setting `frameworkHints` in `adik.config.json`.

---

## 8. Serialization

All generated SDKs handle serialization automatically:

| Concern | Behavior |
|---------|----------|
| **Dates** | ISO-8601 strings ↔ native date types (`Date`, `datetime`, `DateTimeOffset`) |
| **Nulls** | Omitted from serialized JSON (TypeScript: `undefined` stripped; Python: `None` filtered; C#: `WhenWritingNull`) |
| **Enums** | Serialized as string names, not numeric values |

Use the `serialization-helpers.*` boilerplate for manual round-trip scenarios.

---

## 9. Keeping the SDK Updated

When the source project changes, re-run the ADIK pipeline:

```
@agent codebase-analyst task: diff-and-update since: <last-sha>
@agent builder task: build-sdk registry: Registry.md
```

Only changed symbols are regenerated. Your consumer code stays compatible — breaking changes are flagged in `sdk/BUILD_REPORT.md`.

---

## Quick Reference

| Need | Where to Look |
|------|---------------|
| Full working example | `sdk/<lang>/examples/basic-usage.*` |
| Error handling patterns | `sdk/<lang>/examples/error-handling.*` |
| DI wiring for your framework | `sdk/<lang>/examples/advanced/dependency-injection.*` or `boilerplate/` |
| Client factory with defaults | `sdk/<lang>/boilerplate/client-factory.*` |
| Retry wrapper | `sdk/<lang>/boilerplate/retry-wrapper.*` |
| What symbols exist | `Registry.md` |
| Build summary | `sdk/BUILD_REPORT.md` |
| Validation results | `sdk/VALIDATION_REPORT.md` |
| SDK generation config | `adik.config.json` |

---

## Key Files

| File | Role |
|------|------|
| `Registry.md` | Single source of truth for all SDK symbols |
| `sdk/BUILD_REPORT.md` | What was generated and what changed |
| `sdk/VALIDATION_REPORT.md` | Registry validation results |
| `adik.config.json` | SDK configuration (languages, framework hints) |
| `adik.env.json` | Auto-detected environment and framework state |
