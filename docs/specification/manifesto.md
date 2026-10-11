# The ADIK thesis

Developers should be able to give an agent both a usable SDK and the knowledge needed
to implement it well. An adik carries these together: generated SDK code, skills,
contracts, examples, and implementation context.

The tool or library developer invokes ADIK through a coding agent. Producer skills
extract public contracts, generate SDK code, and create the matching agentic elements.
The complete bundle carries that understanding to another environment.

The user asks their own agent to implement the adik in their application. It starts
with the library's implementation knowledge, then inspects the application where it
needs to integrate. Broad library rediscovery should become unnecessary for documented
capabilities.

## Principles

- **Code and knowledge travel together.** A release includes the actual generated SDK
  and instructions that match its behavior and version.
- **Implementation is a product feature.** Configuration, lifecycle, examples, errors,
  and verification are part of the deliverable.
- **Context has a purpose.** A capability index directs the agent to the recipe and
  contracts needed for the task. Source references support deeper investigation.
- **Ownership is clear.** Producers own library contracts; consumers own application
  integration decisions and source changes.
- **Skills compose with host agents.** ADIK supplies the procedures and handoff. The
  agent already chosen by the developer or user performs the work.
- **Claims follow evidence.** Structural validation, SDK behavior checks, and consumer
  exercises establish different properties and should be reported accurately.

Optional MCP, vector search, languages, and distribution integrations extend this
thesis. The essential outcome remains a complete adik that another agent can implement.
