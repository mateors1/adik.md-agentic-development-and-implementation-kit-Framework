# ADIK SDK Generator — Copilot Agent Commands

These slash commands are installed into `.github/` for GitHub Copilot integration.

## Usage

After Spec Kit's `/speckit.implement` completes:

1. `/speckit.adik.registry` — Scan source + Spec Kit contracts → populate Registry.md
2. `/speckit.adik.sdk` — Validate Registry → generate SDK packages
3. `/speckit.adik.boilerplate` — Detect framework → generate integration code
4. `/speckit.adik.status` — Check SDK sync status

## Integration

Copilot reads `.github/copilot-instructions.md` which ADIK's `adik-embed.py` updates
automatically during the boilerplate step. After first run, Copilot is fully ADIK-aware.

## Command Templates

The command templates are identical to the Claude versions in `commands/claude/`.
Copy them to `.github/commands/` (or wherever your Copilot agent reads commands from)
and they will work identically.
