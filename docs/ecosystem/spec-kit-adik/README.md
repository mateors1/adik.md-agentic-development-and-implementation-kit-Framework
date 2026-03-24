# ADIK SDK Generator — Spec Kit Extension

**Generate multi-language, self-maintaining SDK packages from your Spec Kit implementation.**

After `/speckit.implement` produces working source code, the ADIK extension adds four commands
that complete the lifecycle — from implemented application to publish-ready SDKs in TypeScript,
Python, C#, and optionally Go, Java, and Kotlin.

---

## Installation

### Prerequisites

1. **ADIK deployed in your repository** — run `python3 scripts/adik-deploy.py --target .` from the
   ADIK source repo, or follow the [ADIK Quickstart Guide](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/docs/getting-started/quickstart-guide.md)
2. **Python 3.11+** — required for ADIK scripts
3. **Spec Kit initialized** — `specify init . --ai <your-agent>`

### Install the Extension

```bash
specify extension add adik-sdk-generator
```

Or manually: copy the contents of this directory into `.specify/extensions/adik-sdk-generator/`.

---

## Quick Start

After running the standard Spec Kit workflow:

```
/speckit.constitution    → establish project principles
/speckit.specify         → define requirements
/speckit.clarify         → resolve ambiguities
/speckit.plan            → create technical plan (produces contracts/api-spec.json)
/speckit.tasks           → break down into tasks
/speckit.implement       → build the application
```

Continue with the ADIK extension:

```
/speckit.adik.registry   → scan source + api-spec.json → populate Registry.md
/speckit.adik.sdk        → validate Registry → generate SDK packages
/speckit.adik.boilerplate → detect framework → generate DI wiring, examples, retry logic
/speckit.adik.status     → check if SDKs are in sync with source
```

---

## Commands

| Command | Phase | What It Does |
|---|---|---|
| `/speckit.adik.registry` | Post-implement | Invokes ADIK Codebase Analyst to scan source code and `.specify/specs/*/contracts/api-spec.json`; populates `Registry.md` with all public symbols |
| `/speckit.adik.sdk` | Post-registry | Validates Registry (3-level gate), generates SDK packages for configured languages, runs post-generation type-checking |
| `/speckit.adik.boilerplate` | Post-SDK | Detects target framework, generates DI wiring, retry wrappers, usage examples, and self-embeds into AI context |
| `/speckit.adik.status` | Any time | Reports Registry freshness, SDK sync status, build history, and recommended actions |

---

## Configuration

Create or update `adik.config.json` in your project root:

```json
{
  "includePatterns": [
    "src/**/*",
    ".specify/specs/*/contracts/api-spec.json"
  ],
  "sdkLanguages": ["typescript", "python", "csharp"],
  "tier2Languages": [],
  "outputDir": "./sdk"
}
```

See the [ADIK Configuration Reference](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/docs/getting-started/configuration.md) for all options.

---

## The Full Pipeline

```
Spec Kit                                ADIK Extension
────────                                ──────────────
/speckit.constitution
/speckit.specify
/speckit.clarify
/speckit.plan          → api-spec.json
/speckit.tasks                              │
/speckit.implement     → source code        │
                              │             │
                              ▼             ▼
                       /speckit.adik.registry   → Registry.md
                              │
                              ▼
                       /speckit.adik.sdk         → sdk/typescript/, sdk/python/, sdk/csharp/
                              │
                              ▼
                       /speckit.adik.boilerplate → DI wiring, examples, retry wrappers
                              │
                              ▼
                       /speckit.adik.status      → sync report
```

---

## What ADIK Adds to Your Spec Kit Project

| Capability | Without ADIK | With ADIK |
|---|---|---|
| SDK packages | Manual creation | Auto-generated in 6 languages |
| SDK maintenance | Manual updates on every change | Self-maintaining on every commit |
| Integration boilerplate | Developer writes from scratch | Framework-detected DI wiring, retry logic, examples |
| AI awareness | AI knows the app code | AI also knows the SDK and how to use it |
| Validation | `/speckit.analyze` (optional) | Mandatory 3-level gate (14 rules) before generation |
| Audit trail | None | Append-only NDJSON `adik.audit.log` |

---

## Links

- **ADIK Repository:** [github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework)
- **ADIK Website:** [adik.md](https://adik.md)
- **Full Analysis:** [ADIK & Spec Kit Specification Analysis](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/docs/ecosystem/spec-kit.md)
- **Spec Kit:** [github.com/github/spec-kit](https://github.com/github/spec-kit)

---

## License

Apache 2.0 — see [LICENSE](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/blob/main/LICENSE).
