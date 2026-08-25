Wayfinder Fact Organization

Proceed with the consuming-project cleanup and consolidation. Do not return another design proposal unless repository reality makes the settled target unsafe.

Repository and branch

- Verify the exact repository, current branch, HEAD, worktree status, and intended base before editing.
- Create and use the branch "refactor/arc-wayfinder-consolidation".
- Preserve unrelated work.
- Commit and push the completed changes.
- Do not merge.

This consuming-project migration is coordinated with a parallel Agent Workflow source change on "refactor/wayfinder-consolidated-knowledge". The user explicitly authorizes migrating this project-owned Wayfinder state to the target representation below even if the currently installed contract still describes individual F#/D# files.

Do not hand-edit ".agent-workflow/", installed skill projections, or other framework-owned files. If the parallel framework change is not installed when you finish, complete the project-owned consolidation but report final framework-contract validation as pending. Do not undo the new representation merely to satisfy the old installed projection.

Goal

This project is in initial planning and has essentially no product implementation code. It is maintained by one developer, who must be able to open "map.md", understand the project’s current planning state and next questions, and drill into only a few supporting artifacts.

Preserve valuable knowledge, provenance, authority boundaries, accepted decisions, consequential unresolved questions, Jira identifiers, and hard-won analysis. Remove repetitive templates, duplicate frontier representations, and file fragmentation that do not improve navigation or continuation.

Add this exact instruction to the project-owned section of "AGENTS.md", outside any framework-managed region:

«Human maintainability: This project is maintained by a single developer. Keep planning, documentation, and durable state easy to understand and manage; prefer a small number of clear canonical artifacts over unnecessary file proliferation.»

Target Wayfinder representation

Use this as the target unless the repository reveals a concrete reason for a small adjustment:

.agent-wayfinder/arc-eks-architecture/
├── map.md
├── facts.md
├── decisions.md
├── unknowns/
│   └── U#-<readable-name>.md
└── evidence/
    └── E#-capacity-analysis.md

The exact number of surviving unknown files is not predetermined.

- "map.md" is the everyday orientation and sole canonical frontier.
- "facts.md" is one compact, structured current-fact ledger.
- "decisions.md" is one compact, structured current-decision ledger.
- A separate U# file remains only when the question’s reasoning, authority, external lead time, dependencies, consequences, or reconstruction cost materially justify independent preservation.
- Evidence remains a separate artifact only when it is substantial, expensive to reproduce, independently reusable, or requires its own methods and limitations.
- Preserve all existing current F#/D#/U#/E# identifiers where their underlying records survive. Do not renumber merely for neatness.
- Retire old per-record files only after their valuable content and every current reference have been reconciled.

Use the installed mutation-safety rules as far as applicable: reread affected state, serialize the effort mutation, reconcile references before removal, and never overwrite a concurrent change silently.

Facts and provenance

Consolidate current facts into "facts.md". Preserve the factual conclusions and exact useful citations while trimming repeated template language and duplicated context.

Use H2 sections such as:

# Facts

## F19 — Static credentials are prohibited

- Status: established
- Scope: ARC production environment
- Source: <canonical URL or repo/path:lines>
- Authority: <named person or canonical authority artifact, date, forum>
- Derived from: <supporting F#/E#/source and concise derivation>
- Limitations: <material limitation, if any>

<Concise scoped conclusion.>

Rules:

- Every fact must have at least one real provenance field: "Source", "Authority", or "Derived from".
- Omit provenance fields that do not apply; do not fill them ceremonially.
- "Source" must point to the source that actually establishes the claim.
- Another agent-authored document is not independent evidence merely because it repeats the claim.
- "Authority" must name the actual responsible authority or link the accepted authority artifact. Do not invent a person or forum.
- If authority or support cannot be established, downgrade the statement or keep it unresolved rather than presenting it as an established fact.
- Preserve scope and limitations so a Coder precedent, development observation, or environment-specific constraint is not generalized to the whole organization.
- Working assumptions are not F# records. Put them concisely in "map.md" using "Assumed:" and "Settled by:", or retain the relevant U# when independent preservation is justified.

Decisions and authority

Consolidate current decisions into "decisions.md".

Use H2 sections such as:

# Decisions

## D2 — <Committed choice>

- Status: accepted | provisional | superseded
- Authority: <named person, responsible project role, or accepted authority artifact; include date and forum where applicable>
- Based on: <links to relevant facts, evidence, unknowns, policies, or ADRs>
- Revisit when: <required for a provisional decision; optional otherwise>
- Consequences: <concise material consequences>

<The choice, decisive rationale, tradeoffs, and explicit remaining uncertainty.>

Rules:

- "accepted" means the current committed choice.
- "provisional" means an authority explicitly adopted a temporary choice and supplied or accepted a revisit condition. It does not mean “the agent currently recommends this.”
- A proposal, inferred preference, or unresolved architecture option is not a D#.
- Evidence can support a decision but cannot supply decision authority.
- Where D5/D6 or another decision depends on verbal authority that was not durably identified, preserve the actual state honestly. Name the authority when the repository establishes it; otherwise mark authority unresolved and do not strengthen the decision.
- Do not settle the architecture findings from the audit merely because consolidation is authorized.

Evidence and capacity

Keep one substantial capacity-analysis artifact under "evidence/", using the new contract’s E# naming and preserving an existing applicable E# when one exists.

- Treat it as canonical capacity and sizing evidence, not a sizing decision.
- Fold the useful caveats and source classifications from the earlier-draft evidence into it.
- Preserve raw figures, calculations, assumptions, provenance, limitations, the demonstrated allocatable-capacity defect, pod-IP/max-pods analysis, and the distinction between rejection bounds and design values.
- State plainly in "map.md" that no final sizing decision exists unless project authority has actually made one.
- Do not create a generic "evidence.md" merely for symmetry.

Unknowns and current frontier

Re-evaluate the existing U# files while preserving their substantive questions and answers.

- Human-owned asks may live in "docs/open-questions.md" plus a concise map entry when a separate U# adds no additional coordination value.
- Questions safely answerable through implementation and testing in the initial development or non-production environment should remain visible in a concise "Validate in development" section rather than appearing as parallel current blockers.
- Keep a separate U# when the detailed analysis, owner, lead time, dependencies, or consequences warrant it.
- Do not force the result to exactly one unknown.
- The egress/allow-list question, account/CIDR sizing loop, and execution-mode compatibility are plausible survivors, but decide from their actual retained coordination value.
- Preserve "open-questions.md" as the stakeholder-facing worksheet and fix its stale references.
- "map.md" must contain one truthful current frontier and link to detail. Do not keep another authoritative frontier in the backlog, dependency graph, or tracker.

Replace unsupported uses of “pilot” with the project’s actual terminology:

- what must be answered before creating the initial development/non-production environment;
- what can be validated in development;
- what must be resolved before production or broader adoption.

Do not investigate where the word “pilot” originally came from.

Coder/CDER precedent

Remove the standalone Coder/CDER precedent record unless unique retained content genuinely earns an artifact.

Process its content as follows:

- Verified organizational constraints may enter "facts.md", but only with their real source or authority and correct scope.
- A Coder implementation choice is evidence about Coder, not proof that ARC must make the same choice.
- If a Coder example remains useful, preserve only a concise, explicitly non-authoritative precedent note.
- Questions about whether a Coder constraint also applies to ARC belong in "open-questions.md" or a justified U#.
- Implementation conventions that may help later can move to an implementation README only when they remain genuinely useful; otherwise defer or remove them.
- Do not let Coder precedent determine ARC architecture implicitly.

Visual decision tracker

The visual decision tracker is useful to the developer and is outside this cleanup.

- Do not delete, redesign, or modify the tracker application.
- Do not count its application source files as planning files the developer must read.
- Do not delete or rename an input that is required for the tracker to continue building.
- If "dependency-graph.md", generated graph data, or another duplicate is currently required by the tracker, leave it intact for now and clearly label/report it as a non-authoritative projection or deferred integration issue.
- Do not make the tracker’s future adaptation a blocker for this consolidation.

Verify that tracker-owned files are unchanged.

Ticket backlog and duplicate state

Reduce the large agent-authored ticket backlog to a compact register when that can be done without losing real identifiers.

Preserve:

- every real Jira key;
- readable title;
- known status;
- genuine unresolved gap not already owned elsewhere.

Jira or the project’s real ticket system remains canonical for ordered implementation work. Do not retain a second hand-maintained ready frontier in the repository, and do not invent or mutate external tickets.

Fix broken links and remove duplicate dependency/frontier descriptions only when doing so does not break the out-of-scope visual tracker.

Boundaries

- Do not conduct another broad audit.
- Do not broadly research every surviving claim.
- Use the prior audit findings and already collected primary-source evidence.
- Inspect a source only when necessary to preserve or correct a specific claim during consolidation.
- Do not decide unresolved project architecture, sizing, regional topology, execution mode, security exceptions, or stakeholder-owned policy.
- Do not create a new planning subsystem, registry, archive, migration log, or compatibility layer.
- Git is sufficient history; do not retain duplicate files merely as an archive.

Acceptance checks

Before committing, verify:

- A fresh developer can understand the destination, current state, adopted decisions, assumptions, active blockers, development-validation items, and next action from "map.md".
- Facts and decisions remain owned by the Wayfinder effort.
- Every surviving fact has truthful typed provenance and scope.
- Every accepted or provisional decision has actual authority.
- No assumption or proposal is presented as an established fact or accepted decision.
- All valuable content from retired files survives in the map, ledgers, surviving U#/E# artifacts, stakeholder worksheet, or another justified canonical owner.
- No current Markdown link is dangling or misleading.
- Jira keys are preserved.
- The capacity analysis remains evidence and retains its calculations and limitations.
- The visual decision tracker and its required inputs are unchanged.
- No framework-owned installation files were hand-edited.
- The branch contains no unrelated changes.

Report:

- base SHA, branch, commit SHA, and push status;
- before/after Wayfinder file and approximate line counts;
- resulting structure;
- retired and consolidated records;
- tracker files verified unchanged;
- unresolved architecture/authority questions;
- verification performed;
- whether final validation against the parallel Agent Workflow branch remains pending.

Do not merge.