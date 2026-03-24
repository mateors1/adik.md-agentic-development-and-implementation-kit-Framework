# ADIK SDK Generator — Gemini CLI Agent Commands

These slash commands are installed into `.gemini/` for Gemini CLI integration.

## Usage

After Spec Kit's `/speckit.implement` completes:

1. `/speckit.adik.registry` — Scan source + Spec Kit contracts → populate Registry.md
2. `/speckit.adik.sdk` — Validate Registry → generate SDK packages
3. `/speckit.adik.boilerplate` — Detect framework → generate integration code
4. `/speckit.adik.status` — Check SDK sync status

## Command Templates

The command templates are identical to the Claude versions in `commands/claude/`.
Copy them to `.gemini/commands/` and they will work identically.
