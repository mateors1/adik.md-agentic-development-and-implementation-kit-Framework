# Build an adik: quick reference

1. Make the producer source available to the host coding agent.
2. Read `skills/build-adik/SKILL.md`; choose bundle ID/version and SDK languages.
3. Generate SDK code AND library-specific implementation skills, contracts, and examples.
4. Run SDK checks and examples.
5. Seal, validate, and package the complete output.

```bash
python3 scripts/adik-bundle.py seal --bundle /path/to/adik
python3 scripts/adik-bundle.py validate --bundle /path/to/adik
python3 scripts/adik-bundle.py pack --bundle /path/to/adik --output /path/to/adik.zip
```

[Full producer guide](quickstart-guide.md) · [Bundle contract](../specification/bundle-contract.md)
