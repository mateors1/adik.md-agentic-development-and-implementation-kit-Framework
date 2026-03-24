# /speckit.adik.status — Check SDK Sync Status

## When to Use

Run this command **at any time** to check whether the generated SDKs are in sync with the
current source code and Registry.

## What It Does

1. **Compare Registry freshness** — check whether `Registry.md` was generated from the current
   HEAD commit or if the source has changed since the last analysis
2. **Check SDK generation status** — verify that SDK packages exist for all configured languages
3. **Detect stale symbols** — identify Registry entries that may not reflect the current source
4. **Report build history** — read `adik.audit.log` and summarize recent builds
5. **Recommend actions** — suggest which `/speckit.adik.*` commands to run next

## Instructions for the AI Agent

### Step 1 — Read Project State

Check the following files:
- `Registry.md` → read the `Project Metadata` section for `lastAnalysedCommit` and timestamp
- `adik.config.json` → read `sdkLanguages` and `tier2Languages` to know expected outputs
- `adik.audit.log` → read the last 5 entries for build history

### Step 2 — Check Current Commit

Run `git rev-parse HEAD` and compare against the `lastAnalysedCommit` in Registry metadata.

### Step 3 — Check SDK Directories

For each configured language, verify that the output directory exists and contains expected files:
- `sdk/typescript/` → `package.json`, `src/client.ts`
- `sdk/python/` → `pyproject.toml`, `src/client.py`
- `sdk/csharp/` → `*.csproj`, `Client.cs`
- (and tier-2 equivalents if configured)

### Step 4 — Report

Present a status dashboard:

```
ADIK SDK Status
───────────────
Registry:       ✅ Up to date (commit abc1234, 2 hours ago)
                OR ⚠️ Stale (source has 3 commits since last analysis)

SDKs Generated:
  TypeScript:   ✅ sdk/typescript/ (47 files)
  Python:       ✅ sdk/python/ (32 files)
  C#:           ✅ sdk/csharp/ (28 files)
  Go:           ⏭️ Not configured

Boilerplate:    ✅ NestJS DI wiring + examples generated
Self-Embedding: ✅ Context files updated

Last Build:     2026-03-24T00:45:00Z — PASS (0 validation errors)

Recommended Actions:
  → None — everything is in sync!
  OR
  → Run /speckit.adik.registry — source has changed since last analysis
  → Run /speckit.adik.sdk — Registry updated but SDKs not regenerated
```

## Prerequisites

None — this command is informational and can be run at any time.
