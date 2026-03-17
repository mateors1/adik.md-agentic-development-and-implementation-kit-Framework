# ADIK Quickstart Guide — Deploy Your First adik

> **Audience:** Developers evaluating ADIK for the first time.
> **Time to complete:** ~15 minutes.
> **Prerequisites:** Python 3.8+, an agentic coding environment (GitHub Copilot, Claude, Cursor, or any MCP-compatible client).

---

## What You're About to Do

You will:
1. **Read** what ADIK is (2 min)
2. **Deploy** the adik bundle into one of your existing projects (3 min)
3. **Run the pipeline** — analyze your codebase, generate an SDK (10 min)
4. **See the output** — SDK packages, integration boilerplate, and self-embedded context

At the end, your project will have a working agentic SDK that regenerates itself.

---

## Step 0 — Understand the Concept

**ADIK** = Agentic Development and Implementation Kit. It's a framework standard.

An **adik** (lowercase) = the deliverable. It's a self-sustaining agentic SDK — a bundle of AI agents, skills, and templates that:
- Reads your source code
- Builds a type registry (`Registry.md`)
- Generates publish-ready SDK packages (TypeScript, Python, C#, and optionally Go/Java/Kotlin)
- Produces integration boilerplate (DI wiring, retry logic, examples)
- Embeds itself into your AI tools so Copilot/Claude/Cursor understand it

**Key difference from traditional code generation:** the adik carries its own agents. It doesn't just produce SDK packages once — it maintains them on every commit.

> **Read more:** Open `ADIK.md` in this repo — it's the accessible front door. Takes 5 minutes.

---

## Step 1 — Clone This Repo

```bash
git clone https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework.git
cd adik.md-agentic-development-and-implementation-kit-Framework
```

### Orientation — What's in Here

| File | What it is | Should I read it? |
|---|---|---|
| `ADIK.md` | Standard definition — what ADIK is, terminology, contracts | ✅ Start here |
| `ADIK.orchestrator.md` | Operational orchestrator — the machinery that runs inside your project | Skim it |
| `ADIKbuilder.md` | Factory orchestrator — how the framework itself is built (you don't need this) | Skip for now |
| `agents/` | The AI agents (codebase analyst, builder) | Skim if curious |
| `skills/` | The skills agents delegate to (SDK generation, validation, etc.) | Skim if curious |
| `scripts/` | Deploy, embed, eject scripts | You'll use `adik-deploy.py` |
| `Registry.md` | Empty template — gets populated with your project's types | Will be auto-filled |
| `docs/` | Architecture, manifesto, examples, formal spec | Read later |
| `README.md` | Overview + quick start | ✅ Good starting point |

---

## Step 2 — Choose a Target Project

Pick an existing project you want to generate an SDK for. Best candidates:

| Project Type | Example | Works Well? |
|---|---|---|
| REST API (any language) | Express, NestJS, FastAPI, ASP.NET | ✅ Excellent |
| gRPC service | Go, Java, C# gRPC | ✅ Excellent |
| Library with public API | npm package, PyPI package | ✅ Good |
| Internal microservice | Any backend service | ✅ Good |
| Frontend-only app | React/Vue/Angular SPA | ⚠️ Limited (no API surface) |

**Requirements for your target project:**
- Has source code with public types/functions/endpoints
- Is in a language ADIK can analyze (TypeScript, Python, C#, Go, Java)
- Has at least a handful of exported types or API endpoints

---

## Step 3 — Deploy the adik

From the ADIK source repo root:

```bash
# Dry-run first — see what would be deployed
python3 scripts/adik-deploy.py --source . --target /path/to/your/project --dry-run

# If it looks good, deploy for real
python3 scripts/adik-deploy.py --source . --target /path/to/your/project --embed
```

**What `--embed` does:** After copying the adik files, it runs `adik-embed.py` to inject ADIK context into your project's AI tool configuration files (`.github/copilot-instructions.md`, `CLAUDE.md`, `agents.md`). This means your AI assistant will immediately understand that ADIK is active.

**What gets copied (14 files):**
```
your-project/
├── ADIK.md                    ← Standard definition
├── ADIK.orchestrator.md       ← Operational orchestrator (this drives everything)
├── Registry.md                ← Empty — will be populated
├── Registry.index.md          ← Template for large projects
├── agents/
│   ├── builder.agent.md
│   └── codebase-analyst.agent.md
├── skills/
│   ├── sdk-builder.skill.md
│   ├── sdk-builder-tier2.skill.md
│   ├── sdk-consumer.skill.md
│   ├── registry-validator.skill.md
│   └── vectorize.skill.md
├── scripts/
│   ├── adik-embed.py
│   └── adik-eject.py
└── mcp/
    └── adik-mcp-server.md
```

**What does NOT get copied:** `ADIKbuilder.md`, `docs/`, `README.md`, `.github/`, `CHANGELOG.md` — those are source-repo-only files.

---

## Step 4 — Run the Pipeline

Open your target project in your agentic coding environment (Copilot Chat, Claude, Cursor, etc.) and give it this prompt:

### Option A: Blanket Mode (Recommended for First Try)

```
Load ADIK.orchestrator.md and run the full pipeline:
1. Probe the environment (step 0)
2. Analyze the codebase and populate Registry.md (step 1)
3. Validate the registry (step 2)
4. Generate SDKs in TypeScript, Python, and C# (step 3)
Use blanket mode — apply your best judgment for all decisions.
```

### Option B: Guided Mode (If You Want Control)

```
Load ADIK.orchestrator.md and start in guided mode.
I want SDKs in TypeScript and Python only. 
Exclude test files and internal utilities.
Only include public API endpoints.
```

### What Happens Next

The AI agent will:

1. **Probe your environment** — detect frameworks, vector DB availability, project type
2. **Scan your source code** — identify all public types, endpoints, functions
3. **Populate `Registry.md`** — write every symbol into the registry
4. **Validate** — run structural, type, and semantic checks
5. **Generate SDKs** — emit complete packages in `sdk/typescript/`, `sdk/python/`, `sdk/csharp/`
6. **Generate boilerplate** — DI wiring, examples, retry wrappers per detected framework
7. **Self-embed** — update your AI tool context files

---

## Step 5 — Inspect the Output

After the pipeline completes, look at:

| Path | What's there |
|---|---|
| `Registry.md` | Your project's complete type registry — every public symbol |
| `sdk/typescript/` | Full TypeScript SDK package (ready to `npm publish`) |
| `sdk/python/` | Full Python SDK package (ready to `pip install`) |
| `sdk/csharp/` | Full C# SDK package (ready to `dotnet pack`) |
| `sdk/BUILD_REPORT.md` | Summary of everything generated |
| `sdk/VALIDATION_REPORT.md` | Registry validation results |
| `adik.env.json` | Detected environment, framework hints, project type |

### Verify It Worked

- Open `Registry.md` — does it contain your project's types?
- Open any `sdk/<lang>/` — does it have a README, type definitions, client code?
- Open `.github/copilot-instructions.md` — does it mention ADIK?

---

## Step 6 — Optional Configuration

If defaults aren't right, create `adik.config.json` in your project root:

```jsonc
{
  // What languages to generate SDKs for
  "sdkLanguages": ["typescript", "python"],     // tier-1 only

  // Add tier-2 if you need Go/Java/Kotlin
  "tier2Languages": ["go"],

  // Control what source files to scan
  "includePatterns": ["src/**/*"],
  "excludePatterns": ["**/*.test.*", "**/*.spec.*"],

  // Output directory
  "outputDir": "./sdk",

  // Auto-detect project type or specify
  "projectType": "auto"    // "api" | "service" | "library"
}
```

Then re-run the pipeline. The agents will pick up the new config automatically.

---

## Step 7 — Eject (If Needed)

Changed your mind? One command removes everything:

```bash
# See what would be removed
python3 scripts/adik-eject.py --target . --dry-run

# Actually eject (keeps generated sdk/)
python3 scripts/adik-eject.py --target . --confirm

# Also remove generated SDKs
python3 scripts/adik-eject.py --target . --confirm --remove-sdk
```

Source code is **never** touched. Only ADIK-owned files and the `<!-- ADIK:START -->` / `<!-- ADIK:END -->` blocks in context files are removed.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| "Registry.md is empty after analysis" | Make sure your source files have exported/public types. Check `includePatterns` in config. |
| "Validation FAIL" | Read `sdk/VALIDATION_REPORT.md` — it explains what's wrong. Usually a type reference to something not in the registry. |
| "No SDKs generated" | Validation must pass first. Fix registry issues, then re-run the builder. |
| "AI agent doesn't know about ADIK" | Run `python3 scripts/adik-embed.py --action upsert --target .` to re-embed context. |
| "Want to change languages" | Edit `adik.config.json` and re-run the pipeline. |
| "Project is too large / too many types" | ADIK auto-partitions registries above 500 symbols. If that's not enough, set `"registryMode": "partitioned"` in config. |

---

## What's Next

- **Continuous sync:** Every time you commit changes to your source code, re-run steps 1-3. Only changed symbols trigger regeneration.
- **MCP Server:** If your agentic environment supports MCP, load `mcp/adik-mcp-server.md` for tool-based access to the pipeline.
- **Tier-2 languages:** Add `"tier2Languages": ["go", "java", "kotlin"]` to `adik.config.json` for additional SDK output.
- **Feedback:** File issues at the [ADIK repo](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework/issues) or talk to Mateo directly.

---

## Key Files to Read (Priority Order)

1. **`ADIK.md`** — What the standard is (5 min)
2. **`ADIK.orchestrator.md`** — How the pipeline works (10 min, skim the workflow section)
3. **`Registry.md`** (after first run) — Your project's type registry
4. **`agents/codebase-analyst.agent.md`** — How source analysis works (optional)
5. **`agents/builder.agent.md`** — How SDK generation works (optional)

---

> **Sponsor ADIK:** If this saves you time, consider [sponsoring](https://github.com/sponsors/mateors1) ❤️
