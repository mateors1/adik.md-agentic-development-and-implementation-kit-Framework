# Architecture — How ADIK Works

> **Part of:** [ADIK — Agentic Development and Implementation Kit](../README.md)

---

## System Overview

ADIK is a multi-agent system coordinated by a single orchestrator. The diagram below shows the full flow from source code to published SDK packages.

```mermaid
flowchart TB
    subgraph Source["Source Repository"]
        SRC["Source Code<br/>(TS / Python / C# / Go / Java)"]
        CFG["adik.config.json<br/>(optional)"]
    end

    subgraph Orchestrator["ADIK.orchestrator.md — Operational Orchestrator (inside the adik)"]
        direction TB
        STARTUP["Startup Protocol<br/>Blanket │ Guided │ Headless"]
        DETECT["Project-Type Detection<br/>& Framework Inference"]
    end

    subgraph Agents["Agents"]
        CA["Codebase Analyst Agent<br/>agents/codebase-analyst.agent.md"]
        BA["Builder Agent<br/>agents/builder.agent.md"]
    end

    subgraph Registry["Symbol Registry"]
        REG["Registry.md<br/>(monolithic)"]
        RIDX["Registry.index.md<br/>(partitioned index)"]
        RPART["Registry.&lt;domain&gt;.md<br/>(domain partitions)"]
    end

    subgraph Skills["Skills"]
        RV["Registry Validator<br/>skills/registry-validator.skill.md"]
        SB1["SDK Builder (Tier-1)<br/>skills/sdk-builder.skill.md"]
        SB2["SDK Builder (Tier-2)<br/>skills/sdk-builder-tier2.skill.md"]
        SC["SDK Consumer<br/>skills/sdk-consumer.skill.md"]
        VEC["Vectorize<br/>skills/vectorize.skill.md"]
    end

    subgraph Output["Generated SDK"]
        TS["sdk/typescript/"]
        PY["sdk/python/"]
        CS["sdk/csharp/"]
        GO["sdk/go/ (opt-in)"]
        JV["sdk/java/ (opt-in)"]
        KT["sdk/kotlin/ (opt-in)"]
        RPT["sdk/BUILD_REPORT.md"]
    end

    subgraph Infra["Infrastructure"]
        MCP["MCP Server<br/>mcp/adik-mcp-server.md"]
        DEP["Deploy<br/>scripts/adik-deploy.py<br/>(source repo only)"]
        EMB["Self-Embedding<br/>scripts/adik-embed.py"]
        EJT["Eject<br/>scripts/adik-eject.py"]
    end

    SRC --> CA
    CFG --> STARTUP
    STARTUP --> DETECT --> CA
    CA --> REG
    CA --> RIDX --> RPART
    CA -.->|"vectorMode active"| VEC
    REG --> BA
    RIDX --> BA
    BA --> RV
    RV -->|PASS| SB1
    RV -->|PASS| SB2
    SB1 --> TS & PY & CS
    SB2 -.->|"opt-in"| GO & JV & KT
    BA --> SC --> TS & PY & CS
    BA --> RPT
    BA --> EMB
    MCP -.->|"remote trigger"| BA
    MCP -.->|"remote trigger"| CA
```

---

## Two Orchestrators

ADIK has a factory orchestrator and a specialized orchestrator that ships in every adik:

| Orchestrator | File | Audience | Deployed? |
|---|---|---|---|
| **Factory** | `ADIKbuilder.md` | ADIK framework maintainers (this source repo) | No |
| **Standard Definition** | `ADIK.md` | Everyone — defines ADIK terminology, contracts, and principles | Yes |
| **Operational Orchestrator** | `ADIK.orchestrator.md` | SDK consumers in target repositories (inside every adik) | Yes |

`ADIKbuilder.md` is the factory — it produces specialized adiks (self-sustaining agentic SDK bundles). `ADIK.md` is the standard definition — it defines what ADIK is. `ADIK.orchestrator.md` is the brain inside every adik — it drives the actual SDK generation, implementation, and maintenance pipeline.

---

## Agent → Skill Delegation Model

ADIK follows a strict **orchestrator → agent → skill** delegation hierarchy:

```mermaid
flowchart LR
    ADIK["ADIK.orchestrator.md<br/>(orchestrator)"]
    CA["Codebase Analyst<br/>(agent)"]
    BA["Builder<br/>(agent)"]
    RV["Registry Validator<br/>(skill)"]
    SB["SDK Builder<br/>(skill)"]
    SB2["SDK Builder Tier-2<br/>(skill)"]
    SC["SDK Consumer<br/>(skill)"]
    VEC["Vectorize<br/>(skill)"]
    EMB["adik-embed.py<br/>(script)"]

    ADIK --> CA
    ADIK --> BA
    CA --> VEC
    BA --> RV
    BA --> SB
    BA --> SB2
    BA --> SC
    BA --> EMB
```

**Agents** make decisions (what to analyse, which languages to build, how to handle errors).
**Skills** execute a single well-defined task (generate Go code, validate the registry, embed vectors).
**Scripts** are deterministic utilities (self-embedding, ejection, deployment) that agents invoke but never reimplement.

---

## Data Flow

```
Source Code
    │
    ▼
┌──────────────────────┐
│  Codebase Analyst    │  Scans source, detects symbols, infers frameworks
│  Agent               │  Writes: Registry.md (or partitioned registries)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Registry Validator  │  Three-level gate: Structural → Type → Semantic
│  Skill               │  Writes: sdk/VALIDATION_REPORT.md
└──────────┬───────────┘
           │ PASS
           ▼
┌──────────────────────┐
│  Builder Agent       │  Coordinates SDK generation across all languages
│                      │  Invokes: SDK Builder → SDK Consumer → Self-Embed
└──────────┬───────────┘
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
   TS/   Py/   C#/     ← Tier-1 (always)
   Go/   Java/ Kotlin/  ← Tier-2 (opt-in)
```

---

## Registry Model

The Registry is the single source of truth. Every symbol in the SDK must first be declared in the Registry.

### Monolithic Mode (default)

A single `Registry.md` file containing all symbols. Works well for projects with < 500 symbols.

### Partitioned Mode (auto-triggered)

When symbol count ≥ 500, the Codebase Analyst automatically partitions:

```
Registry.index.md          ← Master index with partition table
Registry.auth.md           ← Auth domain symbols
Registry.payments.md       ← Payments domain symbols
Registry.users.md          ← Users domain symbols
```

Agents load only the partitions they need, keeping context windows manageable.

---

## Optional Features

All features below are additive. The core pipeline (Analyst → Validator → Builder) works with zero configuration.

| Feature | Trigger | Component |
|---|---|---|
| **Tier-2 languages** | `tier2Languages` in `adik.config.json` | `skills/sdk-builder-tier2.skill.md` |
| **Vector search** | Vector DB detected in environment | `skills/vectorize.skill.md` |
| **MCP server** | Manual setup | `mcp/adik-mcp-server.md` |
| **Framework hints** | Auto-inferred from package manifests | `skills/sdk-consumer.skill.md` |
| **Headless/CI mode** | `ADIK_NON_INTERACTIVE=true` | `ADIK.orchestrator.md` startup protocol |
| **Self-embedding** | Automatic post-build | `scripts/adik-embed.py` |

---

## Related Reading

| Document | Purpose |
|---|---|
| [README](../README.md) | Overview and quick start |
| [Manifesto](manifesto.md) | Philosophy and principles |
| [Build Your Own ADIK](examples/ADIKBuilderExample.md) | Step-by-step construction guide |
| [Red-Team Audit v2](red-team-audit-v2.md) | Security audit and risk matrix |
