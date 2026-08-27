# Reconcile legacy resolved Wayfinder unknowns

Work in the current consuming project.

Create and use branch:

`fix/retire-answered-wayfinder-unknowns`

Do not merge or push.

## Goal

Bring the project's existing Wayfinder state into the current semantics:

* current U# files represent unanswered questions only;
* an actually answered U# should have any independently useful outcome preserved in its proper current owner, affected current state reconciled, then the U# retired;
* unanswered uncertainty that was merely accepted by responsible authority remains open;
* Git owns history.

## Scope

Inspect only the relevant current Wayfinder effort(s) containing U# files marked `resolved` or otherwise representing already-answered questions.

Do not perform a repository-wide cleanup of unrelated Wayfinder data, historical artifacts, or opaque project-owned content.

Before mutating Wayfinder state, read the installed current Wayfinder contract and follow its locking, reconciliation, reference, and retirement rules.

## Reconcile each affected U#

For each current U# that appears resolved:

1. Determine whether the underlying question was actually answered by valid evidence or authority.
2. If answered:

   * identify any information in the U# that still has independent current value;
   * preserve that information in its proper existing/current owner only when justified;
   * do not create an F# or D# ceremonially;
   * reconcile the map, blockers, dependencies, frontier, and all known current references that depend on the U#;
   * retire the U#.
3. If the question was not actually answered and progress was only authorized despite uncertainty:

   * keep or restore the U# as open;
   * record the responsible authority's accepted uncertainty and the exact boundary it unblocks where current project state requires it;
   * do not treat the underlying question as resolved.
4. If evidence is insufficient to determine which case applies, preserve the U# and report the ambiguity rather than guessing.

An empty `unknowns/` directory has no semantic meaning. Do not create work merely to remove or preserve it.

## Important constraints

* Preserve current decisions, facts, evidence, and canonical project artifacts unless reconciliation requires a truthful update.
* Do not retain a resolved U# solely for historical traceability.
* Do not create an archive, tombstone, migration record, replacement history file, or cleanup registry.
* Do not renumber unaffected current U/E/F/D identifiers.
* Do not remove useful information until its current owner is clear.
* Preserve unrelated work and untracked files.

## Verification

After reconciliation:

* no current U# file should be marked `resolved`;
* every remaining U# should represent a genuinely unanswered question;
* no current map, fact, decision, evidence record, or other known current reference should point to a retired U#;
* dependent blockers/frontier state should reflect the actual answers now available;
* unrelated state should remain unchanged.

Run the project's normal relevant verification/tests if available, plus:

`git diff --check`

Review the diff specifically for accidental loss of rationale or useful current information.

## Finish

Commit the reconciliation on the target branch.

Report:

* branch and commit SHA;
* which U# records were inspected;
* which were retired and what current owner, if any, preserved their useful outcome;
* which remained/reverted to open and why;
* dependent state reconciled;
* any ambiguous records left untouched;
* verification results;
* final working-tree status.

Do not merge or push.
