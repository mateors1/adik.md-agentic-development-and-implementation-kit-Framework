# Producer quickstart: build an adik

You are the developer of a tool, API, service, or library. Your output is a completed
adik containing **generated SDK code plus matching implementation skills and context**.

## Prepare

Make your source and authoritative contracts available to your coding agent. Decide
which SDK languages and consumer environments you support. Python, TypeScript, and
C# skills are included; other bundled language skills are optional.

From the ADIK toolkit repository:

```bash
python3 -m pip install -r requirements-adik.txt
python3 scripts/adik-deploy.py --source . --target /path/to/library --embed
```

This is a producer bootstrap. It adds generation skills and helpers; SDK generation
happens when the host agent follows the producer procedure.

## Ask the agent to generate the complete deliverable

> Read `skills/build-adik/SKILL.md`. Build an adik from this library in a dedicated
> output directory. Generate Python SDK source code and matching implementation
> skills, contracts, references, and runnable examples. Use bundle ID `my-library`
> and version `1.0.0`. Start with framework-neutral consumer guidance. Run the SDK
> checks, seal and validate the bundle, and report the results.

The producer's framework is recorded as source architecture. Consumer support is
controlled separately through `consumerFrameworks` or explicit requirements.

## Validate and distribute

```bash
python3 scripts/adik-bundle.py validate --bundle /path/to/generated-adik
python3 scripts/adik-bundle.py pack --bundle /path/to/generated-adik --output /path/to/my-library-adik.zip
```

Share the complete archive through your chosen distribution channel. It includes
SDK source and agentic elements together. Package publication is performed by your
chosen tools when requested.

Continue with the [consumer guide](consumer-guide.md),
[reference example](../examples/reference-adik.md), or [bundle contract](../specification/bundle-contract.md).
