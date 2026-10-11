# Implement an adik: quick reference

1. Obtain the complete SDK-and-agentic-elements bundle.
2. Validate it and register the consumer skill with your coding agent.
3. Ask the agent to implement a named capability in your application.
4. The agent uses packaged library knowledge, inspects integration points, installs
   the bundled SDK, edits application code, and runs relevant checks.

```bash
python3 scripts/adik-bundle.py validate --bundle /path/to/adik
python3 scripts/adik-bundle.py install --bundle /path/to/adik --target /path/to/app --client codex
```

[Full consumer guide](consumer-guide.md) · [Reference exercise](../examples/reference-adik.md)
