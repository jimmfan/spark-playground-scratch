# Reconcile ARC Wayfinder map with roadmap

Review and simplify the existing ARC/EKS Wayfinder `map.md` in the repository currently open in VS Code.

Do not create or switch branches. Do not commit or push.

## Goal

Reconcile `map.md` with the ARC implementation roadmap that already exists in this repository.

The roadmap should remain the canonical high-level project plan. The Wayfinder map should become a compact re-entry/navigation surface that tells a fresh agent where the project is now, what materially blocks or constrains progress, and what is ready next.

Do not redesign Wayfinder or introduce new state types, phase files, trackers, registries, or planning artifacts.

## Inspect before editing

Read enough repository truth to make the rewrite safely:

- the complete current ARC/EKS `map.md`;
- the current Wayfinder contract/instructions;
- the existing ARC implementation roadmap;
- `facts.md`, `decisions.md`, and only the U#/E# records materially referenced by the map;
- `docs/open-questions.md` if present;
- the repo-local Jira ticket/register file and references to it;
- Architecture Navigator source/docs/tests that depend on `map.md`.

Use Git history only when necessary to determine whether unusual content is intentional or stale.

Do not simplify first and investigate afterward.

## Canonical roadmap

The ARC implementation roadmap already exists in this repository.

Treat it as the canonical owner of:

- overall project sequencing;
- phase goals;
- important phase-level considerations;
- phase exit criteria.

Do not recreate, duplicate, substantially rewrite, or replace the roadmap as part of this task unless a factual inconsistency with higher-authority current project state must be corrected.

Use this ownership model:

- **Roadmap:** where the project is going.
- **Wayfinder map:** where the project is now, material blockers/dependencies, ready frontier, and next milestone.
- **Facts / decisions / evidence:** durable supporting project knowledge.
- **Actual Jira:** implementation tickets, ticket status, ordering, and ticket-level acceptance criteria.

## Rewrite `map.md`

Reconcile the existing map rather than replacing it mechanically with a template.

Prefer a compact shape roughly like:

- Destination / scope
- Canonical roadmap link
- Territory
- Current position
- Current state
- Material blockers and dependencies
- Ready frontier / next work
- Next milestone
- Small set of useful canonical links

These are preferred responsibilities, not mandatory headings.

A fresh agent reading the map should quickly understand:

1. What this effort is trying to deliver.
2. What major areas and important seams matter.
3. Which roadmap governs the overall sequence.
4. Where the project currently stands.
5. What materially blocks or constrains the next move.
6. What can safely proceed now.
7. What milestone allows the project to advance.
8. Which few canonical artifacts contain deeper detail.

### Territory

Keep the useful low-resolution territory model.

Update it if necessary to reflect current project reality and important seams, but do not turn it into another backlog or detailed architecture specification.

### Current state

Reduce this substantially where possible.

Keep only consequential information needed to resume the effort now.

Do not repeat detailed history, audits, fact/decision rationale, prior-art notes, or future production planning already owned elsewhere.

Link canonical records instead.

### Roadmap position and next milestone

Reference the existing roadmap rather than reproducing all of its phases.

Identify the current roadmap position only when repository evidence supports it.

Do not claim a phase is complete merely because work was discussed, planned, or partially implemented.

Use the relevant roadmap exit criterion as the next milestone where useful.

### Blockers and dependencies

Keep only material current blockers and dependencies.

An unanswered future question is not automatically a current blocker.

Where practical, make clear what an actual blocker prevents.

### Ready frontier

Keep the smallest coherent work that can proceed now.

Do not reproduce a ticket backlog here.

### Assumptions

Reduce any large assumption ledger in the map.

Keep only assumptions that materially affect current navigation.

If an assumption is actually a consequential unresolved question, link its canonical unknown/open question rather than maintaining parallel settlement detail in the map.

Do not silently promote assumptions into facts or decisions.

### Future work

Remove detailed future validation, production-hardening, or later-stage work from the live map when the roadmap already owns that sequencing and the issue has no present effect on the current route.

Preserve future concerns only when they create a current dependency, blocker, or meaningful external lead-time constraint.

Correct stale project assumptions when current authoritative repository state clearly supersedes them.

### Notes and file inventories

Reduce broad file catalogs.

The repository itself is the file index.

Keep only links that materially help re-entry or current navigation.

## Architecture relationships and Architecture Navigator

Do not blindly delete the `Architecture relationships` or `Architecture Navigator governance` sections.

First inspect the Navigator implementation and tests.

Determine whether:

- the relationship table is machine-parsed;
- headings, columns, identifiers, or relationship types are contractual;
- Navigator requires this information to remain in `map.md`;
- governance prose has another canonical owner.

Preserve whatever the current Navigator genuinely requires.

If detailed Navigator governance is duplicated from an existing canonical document, prefer a concise link rather than repeating it in the ARC map.

Do not change Navigator behavior merely to make the map shorter.

Do not silently discard unique project-owned information.

## Jira cleanup

Review the repo-local Jira ticket/register file.

Jira itself is the canonical owner of tickets, ordering, status, and ticket-level acceptance criteria. We do not want to maintain an AI-generated shadow Jira plan in the repository.

If the local Jira file is primarily duplicated, stale, low-value planning material and contains no unique project knowledge:

- delete it;
- remove or replace references to it from `map.md` and elsewhere;
- preserve direct Jira ticket references only where they materially improve current navigation or traceability.

Do not replace it with another Jira register simply for symmetry.

Before deleting it:

- verify that it contains no unique project knowledge that lacks another canonical owner;
- search for repository references so no broken links remain.

If unique useful information exists only in that file, move only that information to its proper existing canonical owner when one clearly exists. Otherwise retain it and report the issue instead of guessing where it belongs.

## Supporting Wayfinder records

This task is primarily a roadmap/map reconciliation.

Do not broadly rewrite facts, decisions, evidence, unknowns, or open questions just to make the map cleaner.

Make supporting changes only when required to:

- prevent a broken reference;
- correct a clearly stale or false current statement;
- preserve unique information being removed from the map or Jira file.

Do not strengthen provisional decisions, manufacture facts, or resolve authority-owned questions through inference.

## Validation

After editing:

- reread `map.md` as if you were a fresh agent entering the project;
- verify retained Markdown links and Wayfinder identifiers;
- verify map statements against the canonical records they reference;
- verify the roadmap is linked rather than duplicated;
- verify removed map/Jira information was either genuinely redundant or still has a canonical owner;
- run targeted Architecture Navigator/map parsing tests if they exist;
- run existing documentation/link checks if available;
- run `git diff --check`;
- inspect the final diff for unnecessary churn.

Do not weaken tests to make the cleanup pass.

## Report back

Summarize:

- files changed or deleted;
- resulting high-level map structure;
- major content removed or reduced and why;
- whether the Jira file was deleted and what checks justified deletion;
- anything retained because Architecture Navigator depends on it;
- any unique information that could not safely be relocated;
- any conflicts discovered between the roadmap and existing project state;
- tests/checks run and results;
- anything that still requires human judgment.

Do not commit or push.