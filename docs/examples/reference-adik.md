# Reference adik: Hello

`examples/hello-adik/` in the repository is a complete, runnable reference bundle.
It contains actual Python SDK source plus a matching native implementation skill,
contract, capability guide, and runnable example. `examples/producer/hello.py` is
the simple source-library fixture. `reference:hello-v1` is a fixture provenance label,
not a real upstream Git commit or a claim about a live generation run.

## Inspect and run

From the repository root:

```bash
python3 scripts/adik-bundle.py validate --bundle examples/hello-adik
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=examples/hello-adik/sdk/python python3 examples/hello-adik/skills/implement-hello/assets/example.py
python3 -m unittest discover -s tests -v
```

The code implements `hello_sdk.greet(name)`. It trims whitespace, preserves Unicode,
and rejects blank or non-string input. The skill explains integration and errors
using those exact semantics.

## Try the consumer handoff

```bash
python3 scripts/adik-bundle.py install --bundle examples/hello-adik --target /tmp/hello-consumer --client codex
```

Give your coding agent a small Python application and ask:

> Implement the Hello adik to greet users. Use the bundled SDK and implementation
> skill. Follow the application's conventions and handle blank names appropriately.

The host agent can use the native adapter at
`.agents/skills/hello-implement-hello/SKILL.md`. It loads the canonical skill and
references under `.adik/hello/`, then installs the included SDK and adapts the application.

The deterministic tests exercise the SDK, registration/removal, and a consumer code
fixture. A live-agent implementation exercise is a separate evaluation. Use the
[protocol and scorecard](consumer-evaluation.md) to record it; no model results are
implied by the fixture passing.
