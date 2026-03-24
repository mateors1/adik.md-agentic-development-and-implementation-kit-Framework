# ADIK SDK Generator — Generic Agent Commands

For agents not explicitly supported, use `specify init --ai generic --ai-commands-dir <path>`.

## Usage

1. Copy the command templates from `commands/claude/` to your agent's commands directory
2. Point `--ai-commands-dir` at that directory during `specify init`
3. Use `/speckit.adik.*` commands as documented

## Command Templates

All four templates (`speckit.adik.registry.md`, `speckit.adik.sdk.md`,
`speckit.adik.boilerplate.md`, `speckit.adik.status.md`) are agent-agnostic —
they reference ADIK's agent and skill specs via relative paths.
