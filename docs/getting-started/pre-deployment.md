# Before deployment: identify the artifact

| You have | Next action |
|---|---|
| ADIK framework source and a library to analyze | Bootstrap the producer toolkit, then ask the agent to build an adik |
| A generated adik containing SDK code, skills, and manifest | Validate it and register its consumer implementation skill |
| Only empty registry templates and generic producer skills | Run producer generation before distributing a completed adik |

Read the [producer guide](quickstart-guide.md), [consumer guide](consumer-guide.md),
and [completed bundle contract](../specification/bundle-contract.md).

Registration copies code and knowledge together. SDK installation into the language
environment and application integration are performed by the consumer's host agent.
