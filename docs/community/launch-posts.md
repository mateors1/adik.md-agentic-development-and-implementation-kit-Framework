# ADIK Launch — Social Media Posts

## LinkedIn Post

---

**I just open-sourced ADIK — a framework where AI agents generate your SDKs, help developers implement them, and maintain themselves.**

For the past few months, I've been building something that I think changes how teams build and consume SDKs.

**The problem:** Every team with a public API maintains SDKs by hand. TypeScript, Python, C#, Go — each one is a separate codebase that drifts out of sync with the source. And even when the SDK ships, developers still spend hours figuring out how to wire it into their project — DI setup, retry logic, serialization, auth config. SDK maintenance is a tax at both ends: the team that builds *and* the team that consumes.

**The solution:** ADIK produces **adiks** — self-sustaining agentic SDKs. An adik isn't just a package. It's a complete bundle: cooperating AI agents that read your source code, build a language-agnostic symbol registry, generate publish-ready SDK packages, produce framework-idiomatic integration boilerplate, and self-embed into your AI tools. The adik carries its own maintenance pipeline — on every commit, the agents re-analyze, re-validate, and re-generate. The SDK stays in sync automatically.

What makes ADIK different from code generators:

🤖 **Fully agentic** — not templates. AI agents analyze your codebase, infer frameworks, detect breaking changes, and generate idiomatic code.

📋 **One Registry, six languages** — a single source of truth generates TypeScript, Python, C#, Go, Java, and Kotlin SDKs. DRY by design.

🔧 **Generation + Implementation** — An adik doesn't just hand you a package. It generates ready-to-use examples, DI wiring (NestJS, FastAPI, ASP.NET), retry wrappers, and serialization helpers. Developers can adopt the SDK in minutes, not hours.

♻️ **Self-sustaining** — The adik carries its own agents and pipeline. On every commit, it re-analyzes, re-validates, and re-generates. No manual SDK maintenance ever again.

🧠 **AI-aware SDKs** — An adik self-embeds into whatever AI tools your team uses (Copilot, Claude, Cursor). Any assistant in the repo automatically understands the SDK and can help implement it.

🔌 **MCP Server** — exposes the full pipeline as tools. Your coding agent can regenerate SDKs, query the registry, or scaffold new integrations — all remotely.

🛡️ **Red-team audited** — every vulnerability identified pre-release has been resolved. Includes a mandatory validation gate, post-generation type-checking, and an append-only audit trail.

🚀 **Zero lock-in** — dual-licensed (CC BY 4.0 + Apache 2.0). Clean eject with one command. ADIK never touches your source code.

The full v1.0.0 specification, reference implementation, three end-to-end showcases, and a "Build Your Own ADIK" guide are all available now:

🔗 GitHub: https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework
🌐 Website: https://adik.md

If you maintain or consume SDKs for any API, service, or library — I'd love your feedback. Star the repo, open an issue, or just try deploying an adik into a project.

#OpenSource #AI #SDK #DevTools #AgenticAI #DeveloperExperience #APIDesign

---

## Reddit Post — r/programming

---

**Title:** I built an open-source framework that produces self-sustaining agentic SDKs — ADIK v1.0.0

**Body:**

I've been working on ADIK (Agentic Development and Implementation Kit) — an open standard that produces **adiks**: self-sustaining agentic SDKs.

**The pitch:** You deploy an adik into your repo. Cooperating AI agents analyze your codebase, build a language-agnostic symbol registry, validate it, and generate publish-ready SDK packages in TypeScript, Python, C#, and optionally Go/Java/Kotlin. But here's the key: the adik **carries its own agents and pipeline** — so on every commit, it re-analyzes, re-validates, and re-generates. It also produces framework-specific integration code and self-embeds into your AI tools so any assistant knows the SDK.

**How it works:**
1. Codebase Analyst Agent scans your source → populates `Registry.md`
2. Registry Validator runs a three-level quality gate
3. Builder Agent generates SDK packages per language
4. SDK Consumer Skill generates examples, DI wiring, retry wrappers, and boilerplate for the target framework (NestJS, FastAPI, ASP.NET, etc.)
5. Post-generation type-checking (`tsc`, `mypy`, `dotnet build`, etc.)
6. Self-embeds into your editor context (Copilot, Claude, Cursor) so any AI assistant understands the SDK
7. MCP server lets your coding agent regenerate SDKs or scaffold integrations on demand

**What makes it interesting:**
- The entire framework is Markdown files. No runtime dependencies. LLMs read the specs directly.
- **Self-sustaining.** The adik ships with its own agents and pipeline. Delete a source endpoint, re-run, and the SDK updates. No manual maintenance.
- **Not just generation — implementation.** The SDK Consumer Skill detects your framework and generates idiomatic integration patterns (DI wiring for NestJS, dependency injection for FastAPI, `IServiceCollection` extensions for ASP.NET).
- **AI-aware outputs.** After generation, any AI assistant in the repo automatically knows the SDK exists and how to use it — via deterministic self-embedding.
- Works with any agentic environment (GitHub Copilot, Claude Code, Cursor, any MCP client)
- Red-team security audit included — all identified vulnerabilities resolved before release
- Clean eject: `python3 scripts/adik-eject.py --target . --confirm` removes everything, source code untouched
- Dual license: CC BY 4.0 (spec) + Apache 2.0 (code)

**Links:**
- GitHub: https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework
- Standard specification: in `docs/specification/standard.md`
- Three full showcases: Payments API (NestJS), Task Manager (FastAPI), Chat Service (TypeScript)
- Website: https://adik.md

This is v1.0.0 — the first public release. I'd genuinely appreciate feedback on the approach, the spec, the agent design, or anything else. Happy to answer questions.

---

## Reddit Post — r/artificial (or r/MachineLearning)

---

**Title:** ADIK: An open standard that produces self-sustaining agentic SDKs — AI agents that read code, generate packages, and maintain themselves

**Body:**

Sharing ADIK (Agentic Development and Implementation Kit), an open-source framework I've been building that produces **adiks** — self-sustaining agentic SDKs that use multi-agent orchestration to handle the full SDK lifecycle.

The interesting AI/agent design choices:

- **Factory → specialized adik model** — `ADIKbuilder.md` is the factory that produces project-specific adiks. Each adik is a self-sustaining bundle: it includes the agents that analyze the codebase, generate the SDK, AND maintain it on every commit. The SDK doesn't just arrive — it arrives with its own maintenance pipeline.

- **Markdown-native agents** — every agent and skill is a Markdown specification that LLMs consume directly. No parsing layer, no runtime. The prompt *is* the program.

- **Generation + Implementation pipeline** — most code generators stop at producing the package. ADIK includes an SDK Consumer Skill that detects the target framework (NestJS, FastAPI, ASP.NET, etc.) and generates idiomatic integration patterns: DI wiring, retry logic, serialization helpers, factory classes, and end-to-end examples. The SDK arrives ready to use, not just ready to compile.

- **Self-embedding** — when deployed, ADIK injects its own context into `.github/copilot-instructions.md`, `CLAUDE.md`, and `agents.md` so any AI assistant working in the repo automatically knows the SDK exists and can help developers implement it. Deterministic, guard-marker-based, idempotent.

- **Registry as intermediate representation** — instead of going source → SDK directly, there's a language-agnostic symbol registry (`Registry.md`) that serves as the single source of truth. All 6 target languages generate from this shared representation.

- **LLM validation + compiler verification** — the Registry Validator is an LLM skill (can catch semantic issues) backed by actual compiler type-checking (`tsc`, `mypy`, `dotnet build`, `go build`) for ground truth. Belt and suspenders.

- **MCP server** — exposes all ADIK capabilities as MCP tools, so any MCP-compatible client can drive the pipeline remotely. Developers can ask their coding agent to regenerate the SDK, query the registry, or scaffold a new integration.

The framework has been red-team audited internally, with an audit trail (`adik.audit.log`) for compliance use cases.

GitHub: https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework
Website: https://adik.md

Would be curious to hear thoughts on the agentic architecture — particularly the generation-to-implementation pipeline and whether intermediate registries are the right abstraction for multi-language generation.

---

## Reddit Post — r/ChatGPT / r/ClaudeAI

---

**Title:** I built a framework that produces self-sustaining agentic SDKs — AI agents that generate, implement, and maintain your SDK packages

**Body:**

**ADIK** (Agentic Development and Implementation Kit) is an open-source standard I've been building that produces **adiks** — self-sustaining agentic SDKs.

Think of it like this: you have an API or library. You want SDKs in TypeScript, Python, C#, Go, Java, Kotlin. Instead of writing them by hand, you deploy an adik into your repo. An adik is a complete bundle of cooperating AI agents that:

1. **Analyze** your codebase and figure out what to expose
2. **Build** a structured registry of every public symbol
3. **Validate** the registry for correctness
4. **Generate** complete, publish-ready SDK packages
5. **Implement** ready-to-use integration code — examples, DI wiring, retry logic, serialization helpers — tailored to your framework (NestJS, FastAPI, ASP.NET, etc.)
6. **Self-embed** into your AI tools so any assistant (Claude, Copilot, Cursor) automatically understands the SDK and can help developers use it
7. **Type-check** the output with real compilers
8. **Log** everything in an audit trail

It works with **Claude**, **GitHub Copilot**, **Cursor**, or any MCP-compatible AI tool. The whole framework is just Markdown files — your AI reads them and knows what to do.

The game-changer: an adik is **self-sustaining** — it carries its own agents and pipeline. On every commit, it re-analyzes your code and regenerates the SDKs automatically. No manual maintenance. And the **SDK Consumer Skill** detects what framework you're using and generates idiomatic boilerplate so developers can drop the SDK in and start building immediately. Plus, because the adik self-embeds into your AI assistant's context, you can literally ask Claude or Copilot "how do I use this SDK?" and it knows — without any setup.

**No vendor lock-in.** One command to eject everything. Source code is never modified.

The v1.0.0 spec, three full worked examples, a "build your own" guide, and a security audit are all included.

🔗 https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework
🌐 https://adik.md

First public release — feedback welcome!

---

## Twitter/X Post (Thread)

---

**1/7** 🚀 Introducing ADIK — an open-source standard that produces **adiks**: self-sustaining agentic SDKs.

Your codebase → AI agents → publish-ready SDKs + integration boilerplate in TypeScript, Python, C#, Go, Java, Kotlin.

The adik carries its own agents — it maintains itself. ♻️

🔗 https://adik.md

**2/7** How it works:

1️⃣ Codebase Analyst Agent scans your source
2️⃣ Populates a language-agnostic Registry
3️⃣ Registry Validator runs quality gates
4️⃣ Builder Agent generates SDKs
5️⃣ SDK Consumer Skill generates integration code
6️⃣ Self-embeds into your AI tools
7️⃣ Real compilers type-check everything

**3/7** What makes ADIK different from code generators:

• Fully agentic — AI agents, not templates
• Markdown-native — no runtime, LLMs read specs directly
• Works with Copilot, Claude, Cursor, any MCP client
• Red-team audited before release
• Clean eject: one command, source untouched

**4/7** The key insight: most code generators produce a package and walk away.

An adik is **self-sustaining** — it carries its own agents and pipeline. On every commit, it re-analyzes your code and regenerates. Zero manual SDK maintenance.

Plus the SDK Consumer Skill detects your framework (NestJS, FastAPI, ASP.NET) and generates DI wiring, retry wrappers, serialization helpers.

**5/7** AI-aware SDKs:

After generation, the adik self-embeds into your AI tools. Any assistant in the repo automatically knows the SDK exists and how to use it.

Ask Copilot "how do I authenticate with this SDK?" — it just knows. No config needed.

**6/7** ADIK is dual-licensed:
📝 CC BY 4.0 for the specification
⚙️ Apache 2.0 for the implementation

Zero lock-in. Use it, fork it, build on it.

v1.0.0 includes: full spec, 3 showcases, "Build Your Own" guide, security audit, MCP server.

**7/7** Star the repo, try it on your project, or just read the spec.

GitHub: github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework
Website: adik.md

Feedback and contributions welcome 🙏

#ADIK #OpenSource #AgenticAI #DevTools

---

## Hacker News Post

---

**Title:** Show HN: ADIK – Self-sustaining agentic SDKs: AI agents that generate, implement, and maintain your SDK packages

**URL:** https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework

**Comment:**

Hi HN — I built ADIK (Agentic Development and Implementation Kit), an open standard that produces **adiks** — self-sustaining agentic SDKs.

The core idea: instead of hand-maintaining SDKs in 6 languages, you deploy an adik into your repo. An adik is a complete bundle of cooperating AI agents that analyze your source, build a language-agnostic symbol registry, validate it, generate publish-ready packages in TypeScript, Python, C#, Go, Java, and Kotlin, produce framework-specific integration code, and self-embed into your AI tools. The key: the adik **carries its own agents and pipeline** — on every commit, it re-runs and keeps the SDKs in sync automatically.

Some design decisions that might be interesting to this audience:

1. **Markdown-native** — The entire framework is Markdown files. No parsing layer, no runtime. LLMs read the agent/skill specs directly. The prompt is the program.

2. **Self-sustaining bundle** — An adik ships with its own agents, skills, and pipeline. Deploy it once; it maintains itself on every commit. The SDK consumer doesn't just get packages — they get the factory that produced them.

3. **Registry as IR** — A structured Registry.md serves as the intermediate representation between source analysis and multi-language generation. Auto-partitions at 500+ symbols.

4. **Generation → Implementation pipeline** — The SDK Consumer Skill detects your target framework (NestJS, FastAPI, ASP.NET) and generates idiomatic DI wiring, retry logic, serialization helpers, factory classes, and end-to-end examples. The SDK arrives ready to use, not just ready to compile.

5. **AI-aware outputs** — After generation, `adik-embed.py` injects ADIK context into `.github/copilot-instructions.md`, `CLAUDE.md`, and `agents.md`. Any AI assistant in the repo automatically understands the SDK. Developers can ask "how do I use this?" and the assistant knows — no extra setup.

6. **Compiler backstop** — The LLM-based validator catches semantic issues, but we also run tsc/mypy/dotnet build/go build on the output for ground truth.

7. **MCP server** — Exposes the full pipeline as MCP tools. Any MCP-compatible client can regenerate SDKs, query the registry, or scaffold new integrations remotely.

8. **Zero lock-in** — Clean eject with `python3 scripts/adik-eject.py --target . --confirm`. Source code is never touched. Dual-licensed CC BY 4.0 + Apache 2.0.

Website: https://adik.md

First public release (v1.0.0). Feedback on the approach would be very valuable.
