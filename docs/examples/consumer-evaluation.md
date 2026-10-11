# Consumer implementation evaluation

This exercise measures the ADIK handoff. The host agent executes the task using the
completed adik; ADIK does not provide an execution service.

## Inputs

Give a fresh coding-agent session only a completed adik and a small consumer
application. Keep the producer source repository outside its workspace. Record the
bundle ID/version, source revision, host agent/model version, and application fixture.

## Task

> Implement [capability] using the supplied adik. Load its implementation skill,
> use its actual SDK code, follow this application's conventions, and verify the
> integration. Report the files changed, checks run, and unresolved requirements.

## Scenarios

1. Happy-path integration into an existing call site.
2. Invalid input and documented error handling.
3. A consumer framework different from the producer framework.
4. Missing configuration or an unsupported environment: explain the actual gap.
5. A version mismatch or changed bundle: detect it before claiming completion.

## Scorecard

| Measure | Evidence to record |
|---|---|
| Discovery | Correct implementation skill selected |
| SDK use | Bundled package and correct version imported |
| Behavior | Capability and error assertions pass |
| Conventions | Existing configuration, DI, and error patterns reused |
| Context | Capability references and relevant symbols read |
| Search effort | Unnecessary broad library searches and total files read |
| Scope | Unrelated application and producer contracts preserved |
| Verification | Actual commands/results, including failures or missing tools |

Use a baseline without the agentic elements to compare search effort and corrections,
then repeat with the complete adik. Record results rather than assuming an improvement.
A deterministic fixture pass establishes helper/SDK behavior; it is not a live-agent score.

## Run record template

```text
Bundle / version:
Host agent / model:
Consumer fixture:
Requested capability:
Skill selected:
References and source files read:
Application edits:
Commands and outcomes:
Unnecessary searches:
Corrections required:
Remaining limitations:
```
