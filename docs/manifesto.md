# ADIK Manifesto — The Philosophy of Agentic SDK Generation

> **Part of:** [ADIK — Agentic Development and Implementation Kit](../README.md)
> **See also:** [`ADIK.md`](../ADIK.md) (implementation orchestrator), [`ADIKbuilder.md`](../ADIKbuilder.md) (framework orchestrator)

---

## The Problem

Software teams spend enormous effort writing and maintaining SDKs, client libraries, and consumption boilerplate — work that is mechanical, error-prone, and chronically behind the actual service. Every time an endpoint changes, every generated type drifts. Every time a new developer joins, they spend days unwrapping how to call the API.

The documentation says one thing. The codebase says another. The SDK says a third. Entropy wins.

---

## The Inversion

**ADIK inverts this.** The source of truth is the *codebase*, not a wiki or a hand-maintained SDK.

A team of specialised agents reads your code, understands its structure, and generates complete, publish-ready SDK packages in TypeScript, Python, and C#. When the codebase changes, the SDK changes. When a new developer joins, the boilerplate is already there.

The developer writes code. ADIK writes the SDK.

---

## Four Core Principles

### 1. One Source of Truth

Every type, schema, and endpoint is declared once in `Registry.md` and generated into all languages from that single definition. There is no duplication. There is no drift.

> *If it isn't in the Registry, it doesn't exist in the SDK.*

### 2. Inference Over Configuration

Framework hints, project type, vector capabilities — ADIK discovers these automatically. It reads `architecture.md`, scans package manifests, and inspects existing agent definitions to understand the environment before writing a single line of generated code.

You should only need to configure what ADIK cannot know.

> *Convention is the default. Configuration is the escape hatch.*

### 3. Context Cleanliness

Vectorization, framework-specific logic, and infrastructure concerns live in dedicated subagents and subskills. The orchestrator stays lean and readable in any context window.

A well-designed agentic system should be understandable at a glance. Every file does exactly one thing, and does it completely.

> *Separation of concerns applies to agents, not just code.*

### 4. Graceful Degradation

Every feature is additive. Vector mode, MCP server, framework-specific boilerplate — all optional. The core pipeline works with zero configuration.

You do not need a vector database to benefit from ADIK. You do not need an MCP client. You do not even need a config file. Run the two agents and you have an SDK.

> *The floor is low. The ceiling is high.*

---

## What ADIK Is Not

- **Not a code generator that replaces developers.** ADIK generates boilerplate and SDK wrappers so developers can focus on business logic.
- **Not a documentation tool.** ADIK builds `Registry.md` as a machine-readable artifact, not a prose document.
- **Not a lock-in.** Every generated SDK package is self-contained and can be published independently of ADIK. You can adopt ADIK incrementally and remove it without losing your SDKs.
- **Not a runtime dependency.** ADIK is a development-time tool. Nothing it generates requires ADIK to be present at runtime.

---

## On Agentic Systems

ADIK is itself built as an agentic system — a collection of cooperating agents, each with a clear role and well-defined contracts, coordinated by an orchestrator.

This is not an accident. The same principles that make ADIK useful for SDK generation — single source of truth, separation of concerns, graceful degradation — are the same principles that make any agentic system maintainable and trustworthy.

The framework eats its own cooking.

---

## The Standard

ADIK is designed to be a **publishable standard**, not just a tool. The contracts between orchestrator, agents, skills, and registry are documented precisely enough that anyone can implement a compatible ADIK framework from scratch — see [`docs/examples/ADIKBuilderExample.md`](examples/ADIKBuilderExample.md) for the complete step-by-step guide.

Standardisation matters because it enables:

- **Interoperability** — multiple ADIK-compatible tools can share a Registry format.
- **Community** — teams can share agent definitions, skills, and registry schemas.
- **Trust** — a known, documented standard is easier to audit and reason about than a bespoke automation script.

---

## Related Reading

| Document | Purpose |
|---|---|
| [`README.md`](../README.md) | Overview, quick start, repository layout |
| [`ADIK.md`](../ADIK.md) | Implementation orchestrator — deployed to target repositories |
| [`ADIKbuilder.md`](../ADIKbuilder.md) | Framework orchestrator — governs ADIK's own development |
| [`docs/examples/ADIKBuilderExample.md`](examples/ADIKBuilderExample.md) | Step-by-step guide to building your own ADIK from scratch |
| [`Registry.md`](../Registry.md) | Symbol registry format specification |
