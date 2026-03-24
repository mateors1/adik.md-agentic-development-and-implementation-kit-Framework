# ADIK Roadmap

> **Current version:** 1.0.0
> **Website:** [adik.md](https://adik.md)

This roadmap outlines the planned evolution of the ADIK standard. Items are prioritized by
community demand and strategic value.

---

## ✅ v1.0.0 — Foundation (Current Release)

The first public release of the ADIK standard, covering the complete agentic SDK pipeline.

- [x] Two-orchestrator model (`ADIK.md` standard + `ADIK.orchestrator.md` operational + `ADIKbuilder.md` factory)
- [x] Codebase Analyst Agent with environment probe, framework inference, dev-state tracking
- [x] Builder Agent with validation, generation, type-checking, and audit logging
- [x] Tier-1 SDK generation: TypeScript, Python, C#
- [x] Tier-2 SDK generation (opt-in): Go, Java, Kotlin
- [x] Language-agnostic symbol Registry with auto-partitioning
- [x] Configurable partition strategy (auto / manual / file)
- [x] Registry Validator — three-level pre-generation gate
- [x] Deterministic self-embedding (`adik-embed.py`)
- [x] Clean eject protocol (`adik-eject.py`)
- [x] MCP server for remote orchestration
- [x] Headless / CI mode (`ADIK_NON_INTERACTIVE`)
- [x] CI/CD self-deploy workflow
- [x] Integration testing workflow (`adik-ci.yml`)
- [x] Append-only NDJSON audit log (`adik.audit.log`)
- [x] Post-generation type-checking (advisory + strict modes)
- [x] Full documentation: standard spec, architecture, manifesto, showcases, scaffold
- [x] Red-team security audit with all pre-release items resolved
- [x] Dual license: CC BY 4.0 (spec) + Apache 2.0 (implementation)

---

## 🔜 v1.1.0 — Developer Experience + Spec Kit Integration

Focused on making ADIK easier to adopt, reducing friction for first-time users, and establishing
ADIK as the SDK generation layer in the Spec-Driven Development ecosystem.

- [ ] **`spec-kit-adik` extension** — publish ADIK as a Spec Kit community extension with
  `/speckit.adik.registry`, `/speckit.adik.sdk`, `/speckit.adik.boilerplate`, and
  `/speckit.adik.status` slash commands
- [ ] **OpenAPI 3.1 bidirectional sync** — generate Registry from OpenAPI and OpenAPI from Registry;
  bridges ADIK with any OpenAPI-aware toolchain (Spec Kit, Swagger, Postman, etc.)
- [ ] **Spec Kit contract path support** — Codebase Analyst auto-scans
  `.specify/specs/*/contracts/api-spec.json` when present
- [ ] **Feature-branch registry partitions** — `partitionStrategy: "manual"` aligned to Spec Kit's
  `001-feature-name` branch convention, with `specRef` tag traceability
- [ ] **Interactive CLI installer** — `npx create-adik` or `pip install adik-cli` to scaffold
  ADIK into any project with guided prompts
- [ ] **VS Code extension** — syntax highlighting for Registry.md, inline validation, one-click
  SDK regeneration
- [ ] **GitHub Action (marketplace)** — `uses: adik-md/adik-action@v1` for zero-config CI
  integration
- [ ] **Dashboard UI** — web-based view of Registry contents, build history, and SDK status
  (reads `adik.audit.log` and `BUILD_REPORT.md`)
- [ ] **Init templates** — `adik init --template api|service|library` with pre-populated
  `adik.config.json` and sample registry entries
- [ ] **Migration guides** — from OpenAPI Generator, from swagger-codegen, from manual SDKs

---

## 🔮 v1.2.0 — Language Ecosystem Expansion

Broadening ADIK's reach to more source languages and SDK targets.

- [ ] **Tier-1 expansion: Rust SDK output** — Rust struct generation with serde derives
- [ ] **Tier-2 expansion: Swift SDK output** — Swift package with Codable models
- [ ] **Tier-2 expansion: Dart/Flutter SDK output** — Dart package with JSON serialization
- [ ] **Source analysis: Rust** — parse `pub` items from `.rs` files
- [ ] **Source analysis: PHP** — parse public classes/functions from PHP projects
- [ ] **GraphQL schema support** — parse `.graphql` schemas and generate typed SDK clients

---

## 🔮 v1.3.0 — Enterprise & Compliance

Features for teams in regulated industries and large organizations.

- [ ] **Signed audit log** — cryptographic signing of `adik.audit.log` entries using repository
  secrets or external KMS
- [ ] **SBOM generation** — Software Bill of Materials for each generated SDK package
- [ ] **Diff reports** — structured delta reports between consecutive builds showing exactly
  which symbols changed and why
- [ ] **Access control** — role-based permissions for who can trigger SDK regeneration
- [ ] **Multi-repo orchestration** — single ADIK instance managing SDKs across multiple
  dependent repositories
- [ ] **Registry versioning** — semantic versioning of the Registry itself, independent of
  the ADIK framework version
- [ ] **Compliance profiles** — pre-configured audit/validation settings for SOC2, HIPAA, PCI-DSS

---

## 🔮 v2.0.0 — Runtime Intelligence

The next major version — moving beyond static generation into runtime-aware SDK management.

- [ ] **Live SDK validation** — runtime type-checking middleware that validates API responses
  against the Registry
- [ ] **Usage analytics** — optional telemetry showing which SDK methods are actually used by
  consumers
- [ ] **Breaking change detection** — automatic detection and notification when source changes
  would break existing SDK consumers
- [ ] **SDK playground** — interactive browser-based environment to test generated SDK methods
  against a live or mocked API
- [ ] **Multi-agent collaboration** — ADIK agents coordinating across repositories with shared
  Registry state via vector search
- [ ] **Custom agent marketplace** — community-contributed agents and skills for specialized
  use cases

---

## Contributing to the Roadmap

Have a feature request? Open an issue on the
[GitHub repository](https://github.com/mateors1/adik.md-agentic-development-and-implementation-kit-Framework)
with the `roadmap` label.

Want to sponsor a specific feature? See the [Sponsor](https://github.com/sponsors/mateors1)
page for funding tiers.
