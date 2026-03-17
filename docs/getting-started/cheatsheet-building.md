# Cheat Sheet — Building an adik

> **Audience:** Developers deploying ADIK into a project to generate SDKs.
> **Full guide:** [Quickstart Guide](quickstart-guide.md) | **Config:** [Configuration Reference](configuration.md)

---

## 1. Deploy

```bash
# Dry-run (see what would be copied)
python3 scripts/adik-deploy.py --source <adik-source> --target <your-project> --dry-run

# Deploy + embed into AI tools
python3 scripts/adik-deploy.py --source <adik-source> --target <your-project> --embed

# Force-overwrite existing adik
python3 scripts/adik-deploy.py --source <adik-source> --target <your-project> --embed --force
```

> **Requires source code.** If the target folder is empty, ADIK deploys only artifacts — no SDK is generated until source code exists.

---

## 2. Run the Full Pipeline

Open the target project in your agentic environment and prompt:

```
Load ADIK.orchestrator.md and run the full pipeline.
Use blanket mode.
```

Or step by step:

| Step | Agent / Skill | Prompt |
|------|--------------|--------|
| **0** | Codebase Analyst | `@agent codebase-analyst task: probe-environment` |
| **1** | Codebase Analyst | `@agent codebase-analyst task: analyse-and-register target: ./src` |
| **2** | Registry Validator | `@skill registry-validator registry: Registry.md` |
| **3** | Builder | `@agent builder task: build-sdk registry: Registry.md languages: [typescript, python, csharp]` |
| **4** | Self-Embed | `python3 scripts/adik-embed.py --action upsert --target .` |

---

## 3. Output

```
your-project/
├── Registry.md                     # Populated symbol registry
├── adik.env.json                   # Detected env, framework hints
├── adik.audit.log                  # Build trail (NDJSON)
└── sdk/
    ├── typescript/                  # npm-ready package
    ├── python/                      # pip-ready package
    ├── csharp/                      # NuGet-ready package
    ├── BUILD_REPORT.md              # Generation summary
    └── VALIDATION_REPORT.md         # Registry validation results
```

---

## 4. Configure (Optional)

Create `adik.config.json` in the project root:

```jsonc
{
  "sdkLanguages": ["typescript", "python"],  // tier-1
  "tier2Languages": ["go"],                  // opt-in tier-2
  "includePatterns": ["src/**/*"],
  "excludePatterns": ["**/*.test.*"],
  "outputDir": "./sdk",
  "projectType": "auto"                      // "api" | "service" | "library"
}
```

Re-run the pipeline after changing config.

---

## 5. Incremental Updates

After code changes, re-run analysis + build:

```
@agent codebase-analyst task: diff-and-update since: <last-sha>
@agent builder task: build-sdk registry: Registry.md
```

Only changed symbols trigger regeneration.

---

## 6. Tier-2 Languages

Add to `adik.config.json`:

```jsonc
{
  "tier2Languages": ["go", "java", "kotlin"],
  "tier2Options": {
    "go":     { "modulePath": "github.com/acme/sdk-go" },
    "java":   { "groupId": "com.acme", "artifactId": "sdk", "buildTool": "maven" },
    "kotlin": { "groupId": "com.acme", "artifactId": "sdk-kt", "buildTool": "gradle" }
  }
}
```

---

## 7. Self-Embedding

```bash
# Insert/update ADIK blocks in AI tool config files
python3 scripts/adik-embed.py --action upsert --target .

# Verify blocks are in place
python3 scripts/adik-embed.py --action check --target .
```

Writes to: `.github/copilot-instructions.md`, `CLAUDE.md`, `agents.md`

---

## 8. Eject

```bash
python3 scripts/adik-eject.py --target . --dry-run       # preview
python3 scripts/adik-eject.py --target . --confirm        # eject (keeps sdk/)
python3 scripts/adik-eject.py --target . --confirm --remove-sdk  # eject all
```

Source code is never touched.

---

## 9. MCP Server (Optional)

Expose ADIK as tools for external agents:

| Tool | Description |
|------|-------------|
| `adik_analyse_codebase` | Run codebase analysis |
| `adik_build_sdk` | Trigger SDK generation |
| `adik_get_registry` | Retrieve the full registry |
| `adik_get_symbol` | Look up a single symbol |
| `adik_scaffold_boilerplate` | Generate consumption boilerplate |
| `adik_get_build_report` | Get the last build report |
| `adik_vector_search` | Semantic symbol search (when vectors active) |

Default port: `3100`. Config: `"mcpPort": 3100` in `adik.config.json`.

---

## Quick Troubleshooting

| Symptom | Fix |
|---------|-----|
| Empty `Registry.md` after analysis | Check `includePatterns` — are your source files covered? |
| Validation FAIL | Read `sdk/VALIDATION_REPORT.md` — usually a missing type reference |
| No SDKs generated | Validation must pass first |
| Only artifacts, no SDK code | The agent set up the framework but didn't write the SDK. Re-prompt: *"Read Registry.md. For each language, create the actual source code files in sdk/<language>/ following skills/sdk-builder.skill.md."* |
| `sdk/` directories exist but are empty | Same as above — the pipeline stopped before code generation. Use the explicit prompt. |
| Target folder has no source code | ADIK generates SDKs *from* existing code — add your project code first |
| AI doesn't know about ADIK | `python3 scripts/adik-embed.py --action upsert --target .` |
| Stale SDK directories | Check `adik.env.json.staleArtifacts` — delete manually |

---

## Key Files

| File | Role |
|------|------|
| `ADIK.md` | Standard definition (what ADIK is) |
| `ADIK.orchestrator.md` | Operational brain — drives the pipeline |
| `Registry.md` | Single source of truth for all symbols |
| `adik.config.json` | Your configuration (optional) |
| `adik.env.json` | Auto-detected environment state |
