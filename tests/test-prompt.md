I am at the very beginning of this EKS GitHub Actions ARC runner project.

The repository currently contains only early project documentation, architectural decisions, an existing Wayfinder map, and the Agentic Workflow framework. Do not assume there is already a meaningful implementation to review.

Use the existing repository documentation and Wayfinder state to understand what has already been decided, what remains unknown, and what the project is trying to accomplish.

Then determine the best next concrete implementation step for moving this project forward.

Do not simply give me another architecture document or planning summary if there is enough information to begin implementing something useful.

Your goal is to:

1. Inspect the existing decisions and Wayfinder findings.
2. Identify any unknowns that genuinely block the next implementation step.
3. Resolve those unknowns from the repository where possible.
4. If external technical facts are needed, research only the facts necessary to proceed.
5. Choose a small, high-value first implementation slice that is consistent with the existing decisions.
6. Define acceptance criteria for that slice.
7. Implement it.
8. Run whatever validation is appropriate for what you created.
9. Review the result for incorrect assumptions, unnecessary complexity, or conflicts with the existing decisions.
10. Correct anything found during verification or review.

Do not attempt to build the entire EKS ARC platform in one pass.

Prefer the smallest useful vertical slice that creates a real foundation for subsequent work.

Do not invent requirements that are not supported by the repository. When something is unknown but does not block the current implementation, record it as an unknown and continue.

At the end, report:

- which workflow stages/routes were used,
- why each transition happened,
- which existing decisions affected the implementation,
- what unknowns were encountered,
- what first implementation slice was selected and why,
- what changed,
- what verification was performed,
- and what the logical next step should be.


“Determine from the existing decisions and project state what the next actionable unit of work should be. If that requires further discovery, decomposition, research, or resolution of an unknown, do that as appropriate. If enough is already known to implement something safely, proceed with implementation"





Migrate this project's existing Wayfinder state to the current Agentic Workflow Wayfinder contract.

The framework has changed from the older U#/D#/T# model. Wayfinder no longer owns T# implementation tickets.

The current model is:

- "map.md" — current state, blockers, dependencies, navigation, and smallest coherent next work
- "unknowns/" / U# — unresolved consequential questions
- "evidence/" / E# — independently valuable observations/findings with provenance
- "facts/" / F# — sufficiently established durable descriptive conclusions
- "decisions/" / D# — committed choices

Wayfinder state should remain sparse. "map.md" alone is valid. Do not create E#/F#/U#/D# artifacts merely to populate the structure.

Please inspect the repository's current framework contract and existing Wayfinder state before making changes. Treat the installed/current Wayfinder contract as authoritative.

For each existing Wayfinder effort:

1. Inspect its "map.md", U#, D#, T#, and other existing state.
2. Preserve existing project knowledge and history. Do not invent facts, evidence, decisions, or requirements.
3. Move the live status, blockers, dependencies, and smallest coherent next action formerly represented by T# into "map.md".
4. Preserve independently valuable unresolved questions as U#.
5. Create E# or F# only when the existing state contains information that clearly belongs there and preserving it independently is useful.
6. Preserve valid D# decisions.
7. Remove active T# references from "map.md".
8. If remaining work genuinely requires substantial/dependency-aware decomposition, use or point to the framework's "to-tickets" workflow rather than creating Wayfinder T# artifacts.
9. Do not mechanically convert T# → F#, D#, E#, or U#. Classify information by meaning.
10. Do not delete historical project-owned "tickets/" content unless the current contract explicitly requires deletion. Prefer preserving obsolete T# artifacts as historical/legacy state when safe.
11. Do not modify frozen benchmark/evaluation artifacts merely to conform them to the new model.
12. Do not create a README or additional state structure unless the current framework contract requires it.

After migration, verify that:

- active Wayfinder state follows the current contract;
- no active "map.md" depends on T#;
- Wayfinder is not being used as an implementation ticket system;
- existing important knowledge was not lost;
- next work remains clear enough for a fresh agent/session to resume;
- no unnecessary U#/E#/F#/D# artifacts were created.

Before finishing, review the diff specifically for accidental loss or reinterpretation of project-owned state.

Then summarize:

- what you migrated;
- what happened to each old T#;
- any E#/F# artifacts you created and why they justified separate durable state;
- any legacy T# files/directories intentionally preserved;
- anything ambiguous that you intentionally did not change.

Do not redesign the framework itself. This task is only to migrate this consuming project's durable Wayfinder state to the framework's current contract.




Audit all current and historical efforts under .agent-wayfinder/ for state quality. This is read-only; do not modify files.
Use the installed Wayfinder contract and current authoritative repository state as the standard. Check whether maps and U/E/F/D records are accurate, correctly classified, sufficiently supported, still useful, and consistent with current canonical artifacts and other efforts.
Pay particular attention to false certainty: inference recorded as fact, recommendation recorded as decision, inconclusive evidence treated as conclusive, resolved questions still recorded as unknown, stale state, unclear authority, and children that should have been settled/retired.
Validate questionable claims using the minimum sufficient method. Inspect repository source/tests/artifacts for repository claims. Use Research only when external primary-source evidence is actually required; do not use it to validate claims the repository can establish.
Report only meaningful findings, grouped by effort, with the file/item, problem, supporting evidence, and recommended correction. Do not manufacture findings. Finish with an overall assessment of whether the Wayfinder state is trustworthy and whether any recurring/systemic problem exists.
Do not implement fixes.


## next prompt
Audit all efforts under ".agent-wayfinder/" for the quality of the project's planning state. The project is still pre-implementation, so evaluate the state as planning knowledge rather than against nonexistent runtime behavior. This is read-only; do not modify files.

Use the installed Wayfinder contract, explicit human/project authority, requirements, accepted project artifacts, and properly supported external evidence as the standard.

Assess whether:

- facts are genuinely established rather than assumptions or inference;
- decisions are actually adopted choices, have the required authority, and are not presented as better-supported than their rationale/evidence warrants;
- unknowns capture consequential unresolved questions without prematurely resolving them;
- evidence actually supports the claims that depend on it;
- maps accurately represent the project's current planning state, dependencies, blockers, and frontier;
- important consequential unknowns, assumptions, dependencies, or decisions appear to be missing;
- Wayfinder records contradict or unnecessarily duplicate canonical project artifacts;
- child records still have independent navigational value or should have been settled.

Pay particular attention to false certainty. Do not treat agreement among agent-created documents as independent evidence; trace important claims back to the actual authority, requirement, observation, or evidence that justifies them.

Use the minimum sufficient validation method. Use Research only for material external factual or technical uncertainty that genuinely requires primary-source evidence. External research cannot substitute for human/project authority.

Do not redesign the project or reopen sound decisions merely because another reasonable choice exists.

Report only meaningful findings, grouped by effort, with the affected item, why it is questionable, what actually supports or contradicts it, and the recommended correction or question to resolve. Also identify consequential missing state when there is concrete evidence that something important has been overlooked.

Finish with:

- whether the planning state is broadly trustworthy;
- the highest-risk findings;
- any recurring/systemic Wayfinder-state problem;
- whether the project appears sufficiently grounded to continue planning toward implementation.

Do not implement fixes.