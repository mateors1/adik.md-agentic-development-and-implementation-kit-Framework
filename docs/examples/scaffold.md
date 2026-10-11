# Master prompt: scaffold a completed adik

Use this prompt in your existing coding agent with the ADIK producer toolkit and
library source available:

> Build a completed adik from this tool/library using `skills/build-adik/SKILL.md`.
> Generate actual SDK code in the requested language(s), plus matching implementation
> skills, contracts, references, runnable examples, and any supporting assets.
> Package them together under one bundle ID and release version.
>
> Preserve the producer source. Record producer architecture separately from supported
> consumer frameworks. Generate a library-specific consumer skill that helps another
> agent select a capability, inspect application integration points, install the SDK,
> implement the requested application changes, and verify them.
>
> Use a dedicated output directory. Validate public symbols and artifact relationships,
> run SDK checks and examples, seal and validate the completed bundle, and report the
> artifact location, actual checks, and limitations. Follow the host's normal execution
> and permission rules.

See the [producer guide](../getting-started/quickstart-guide.md),
[bundle contract](../specification/bundle-contract.md), and
[reference adik](reference-adik.md) for concrete formats.
