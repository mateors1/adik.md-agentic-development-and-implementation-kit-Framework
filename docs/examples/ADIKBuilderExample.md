# Build your own ADIK implementation

An ADIK implementation produces one completed artifact containing generated SDK code
and the agentic elements another agent needs to implement it.

1. Define the source tool/library contract and selected target language.
2. Generate real SDK source and package metadata.
3. Generate a library-specific implementation skill from the emitted SDK, including
   capabilities, configuration, errors, lifecycle, runnable examples, and limitations.
4. Bind the SDK and skill to a versioned completed manifest with source provenance.
5. Validate structure and references; run SDK behavior checks.
6. Hand only the completed bundle and a consumer application to a fresh agent.
7. Evaluate whether the agent implements the capability correctly using the supplied context.

Use the [runnable Hello adik](reference-adik.md) as the minimal example and the
[bundle contract](../specification/bundle-contract.md) as the artifact specification.
The producer bootstrap is a way to deliver generation skills into a library repo;
it is not the completed SDK-and-agentic-elements product.
