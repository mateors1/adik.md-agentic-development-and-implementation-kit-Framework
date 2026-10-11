# Consumer guide: implement an adik

You have an adik from a tool or library developer. It includes actual SDK code and
matching skills, contracts, examples, and implementation context. Your coding agent
uses these to implement capabilities in your application.

## Register the completed bundle

Unpack it into a directory. With ADIK's helper available, validate and register it:

```bash
python3 scripts/adik-bundle.py validate --bundle /path/to/adik
python3 scripts/adik-bundle.py install --bundle /path/to/adik --target /path/to/app --client codex
```

Choose `claude` or `copilot` for the corresponding native adapter. Registration copies
all SDK and agentic files into `.adik/<id>/` and points the client at the implementation
skill. Follow your client's normal skill-reload behavior if the session is already open.

You can also explicitly direct an agent to the bundled `SKILL.md`. Installing an SDK
package through pip/npm alone does not guarantee that its agentic elements are registered.

## Give the agent the implementation task

> Implement [capability] from the [library] adik in [application area]. Load its
> bundled implementation skill and examples. Follow our existing application
> conventions, handle the documented errors, and run the integration checks.

The agent loads the producer's SDK knowledge, inspects relevant application files,
installs the bundled SDK into the application's language environment, and edits
application code. It should not rebuild the library contract from application source.

## Verify and maintain

Expect the agent to identify the SDK version, changed integration points, checks run,
and unresolved requirements. Review the implementation as you would other application
changes. For a new version, use the updated bundle and its migration guidance.

Removal of ADIK registration preserves application integration code and separately
installed language dependencies. See [ownership and removal](../specification/bundle-contract.md).
