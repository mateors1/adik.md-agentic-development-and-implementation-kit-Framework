# Producer configuration

Place optional `adik.config.json` in the producer repository. The host coding agent
reads generation preferences; only registry selection and fields returned by MCP
are enforced by the helper scripts. Configuration does not start a background runner.

```json
{
  "projectType": "library",
  "registryPath": "contracts/registry.json",
  "sdkLanguages": ["python"],
  "tier2Languages": [],
  "outputDir": "generated/my-adik",
  "consumerFrameworks": ["framework-agnostic"]
}
```

| Field | Meaning |
|---|---|
| `projectType` | Producer contract: api, service, or library. Record the resolved value in registry metadata. |
| `registryPath` | Explicit normalized relative file path; takes precedence over automatic selection. Use `Registry.md` for legacy monolithic input. |
| `registryMode` | `monolithic` or `partitioned` for legacy input; an index template alone does not activate partitions. |
| `sdkLanguages` | Requested TypeScript, Python or C# recipes. |
| `tier2Languages` | Optional Go, Java or Kotlin recipes. |
| `outputDir` | Completed bundle root, containing `sdk/`, `skills/`, `contracts/` and the manifest. |
| `consumerFrameworks` | Intended consumer environments. Independent of the producer framework. |

Without an explicit registry path, helpers prefer a completed bundle's manifest,
then `contracts/registry.json`, then explicitly active partitions, then `Registry.md`.
Paths must stay inside the selected root; avoid `./` prefixes and symlinks.

MCP build defaults offer TypeScript, Python and C# recipes. Set languages explicitly
for a focused first bundle. `output_dir` supplied to MCP takes precedence over config.
The producer chooses a bundle version and native package names during generation;
all SDK and implementation skill version declarations must agree.

`adik.env.json` can record producer observations for optional tools. It must not
supply consumer framework defaults. Historical `syncOnCommit`, startup scheduling
and vector settings do not implement execution: use your own host agent or CI.

See the [producer guide](quickstart-guide.md),
[consumer guide](consumer-guide.md) and [migration guide](migration-v2.md).
