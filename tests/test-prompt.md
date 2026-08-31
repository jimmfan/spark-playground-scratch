Wayfinder interactive plan-map prototype

Work in "jimmfan/agentic-workflow".

Create an isolated interactive prototype that explores a better human-facing visualization of Wayfinder coordination state.

Target branch:

prototype/wayfinder-plan-map

Base the work on current "origin/main" after verifying repository and Git truth. Do not build this on an unrelated in-progress refactor branch. Preserve uncommitted work; use an isolated worktree if necessary.

Push the completed branch to:

origin/prototype/wayfinder-plan-map

Do not merge it, open a PR, or modify "main".

Goal

Prototype a visual plan map that lets a human understand, at a glance:

- where an effort is trying to go;
- which meaningful checkpoints have been reached;
- which checkpoint is next;
- what can proceed now;
- which unresolved questions block specific future work;
- which accepted decisions govern specific parts of the plan; and
- why a particular checkpoint is blocked or ready.

This is a visualization experiment, not a new Wayfinder state model.

Do not change current Wayfinder semantics, state storage, routing, ADRs, contracts, or production behavior merely to make the prototype work.

Starting concept

An earlier mockup used a dark dependency graph titled approximately:

Unknown dependencies and completion status

It showed decision and unknown nodes connected by labeled dependency arrows, with an explicit edge list underneath.

The useful idea was that a human could visually see:

decision / unknown
        ↓
governs or blocks
        ↓
downstream work

Preserve that strength, but improve the information architecture.

The new model should make the established plan the visual spine, with Wayfinder state overlaid on it.

Conceptually:

Checkpoint A ──→ Checkpoint B ──→ Checkpoint C ──→ Checkpoint D
                      ▲                 ▲
                      │                 │
                 U1 blocks         D2 governs

Primary plan nodes represent meaningful outcomes or achieved states, not applications or infrastructure components.

Examples:

Request prepared
      ↓
Request submitted
      ↓
Approval received
      ↓
Approach selected
      ↓
Change implemented
      ↓
Outcome validated

The visualization must remain general enough that a checkpoint could represent:

- an approval;
- a request;
- a technical decision;
- an external dependency becoming available;
- implementation completion;
- validation;
- or another meaningful project outcome.

Do not hard-code Agent Workflow around the words "phase", "milestone", or "checkpoint". The prototype may call these "Checkpoints", but the future model should be able to display whatever structure an authoritative plan uses.

Hypothesis

A plan-centered graph with progressively disclosed Wayfinder detail will be easier for a human to understand than either:

- a flat status document; or
- a dependency graph containing only D#/U# records.

The plan should answer:

«Where are we going?»

Wayfinder overlays should answer:

«Given what we know now, what portions of that route are actually open, and why?»

The detail inspector should answer:

«What exactly is this node, what affects it, and where is its authoritative detail?»

Treat this as a hypothesis to explore visually, not an established product requirement.

Research

Before implementation, inspect current repository truth relevant to this concept, especially:

.agent-workflow/contracts/wayfinder-state.md
.agents/skills/wayfinder/SKILL.md
architecture-decisions/0011-use-map-first-wayfinder-state.md
architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md
architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md
docs/architecture.md

Also inspect representative current Wayfinder maps if useful.

Recover only the semantics needed to make the prototype truthful.

In particular preserve these boundaries:

- "map.md" remains a low-resolution coordination/re-entry view.
- An unresolved question is not globally blocking merely because it exists.
- Blocking is scoped to affected work.
- Decisions require appropriate project authority.
- Decisions and unknowns may affect more than one checkpoint.
- An unresolved non-blocking question may remain while independent work proceeds.
- Detailed executable implementation decomposition remains outside Wayfinder when another artifact such as tickets owns it.
- Do not invent a mandatory graph schema simply because this prototype uses one internally.

Prototype location and implementation

Keep the experiment isolated under something similar to:

prototypes/wayfinder-plan-map/
├── README.md
├── index.html
├── styles.css
├── app.js
├── data.js
└── artifacts/
    ├── D1-existing-request-path.md
    ├── D2-existing-service.md
    ├── U1-approval-authority.md
    ├── U2-approval-evidence.md
    └── U3-future-automation.md

Adjust exact filenames when useful.

Prefer:

- plain HTML;
- plain CSS;
- plain JavaScript;
- SVG for the graph/connectors;
- no framework;
- no package manager;
- no build step;
- no network dependency;
- no new production dependency.

Do not introduce React, Vue, Vite, D3, a graph database, a visualization subsystem, or a generalized Wayfinder parser for this prototype.

The prototype should be runnable with a trivial local static server.

Demo scenario

Use a deliberately generic fictional effort rather than AWS/EKS or another product-specific architecture.

A reasonable destination is:

Secure production access is available and validated

Use approximately these plan checkpoints:

M1  Request prepared
M2  Request submitted
M3  Approval received
M4  Approach selected
M5  Change implemented
M6  Outcome validated

Include decisions and unknowns that demonstrate the semantics:

D1  Reuse the existing request workflow
D2  Use the existing service path rather than create a new platform

U1  Who has final approval authority?
U2  What evidence is required before approval?
U3  Can the rollout be automated later?

Arrange relationships so that:

- D1 governs request preparation/submission.
- U1 blocks "Approval received".
- U2 blocks "Approval received".
- D2 governs "Approach selected" and downstream implementation.
- U3 remains unresolved but does not block the currently available route.

That last case is important: the visualization must demonstrate that unresolved uncertainty and blocked work are not synonymous.

Feel free to refine the exact fictional wording while preserving these semantics.

Visual design

Create a polished dark-mode visualization inspired by the earlier dependency-map mockup, but materially improve its hierarchy.

Main workspace

Use approximately:

┌───────────────────────────────────────────────────────────────────────┐
│ Destination / current orientation                                    │
├───────────────────────────────────────────────┬───────────────────────┤
│                                               │                       │
│                 PLAN MAP                      │   DETAIL INSPECTOR    │
│                                               │                       │
│  M1 ───── M2 ───── M3 ───── M4 ───── M5      │   selected node       │
│                    ▲         ▲                │   relationships       │
│                 U1 U2       D2                │   provenance          │
│                                               │   source artifact     │
│                                               │                       │
└───────────────────────────────────────────────┴───────────────────────┘

The plan/checkpoint lane must remain visually dominant.

Decisions and unknowns are overlays, not competing primary timelines.

Use restrained visual semantics for at least:

- complete;
- current / ready;
- blocked;
- upcoming;
- decision;
- unresolved question.

Do not communicate meaning through color alone. Use labels, borders, shapes, icons/badges, or other redundant cues.

Avoid graph spaghetti. Prefer readable connectors and short relationship labels such as:

blocks
governs
depends on

Orientation

At first load, a human should be able to determine within a few seconds:

- the destination;
- how far along the route the effort is;
- the next meaningful checkpoint;
- whether it is ready or blocked;
- and what is causing the block.

A compact orientation line such as:

Next checkpoint: Approval received · blocked by 2 unresolved questions

is useful if it can be derived from the fixture data rather than duplicated manually.

Do not turn the page into a KPI dashboard.

Interactive inspector

The right-side inspector is a core part of the prototype.

Clicking any checkpoint, decision, or unknown should select it and populate the inspector without navigating away.

For a selected item, show useful fields such as:

- ID and type;
- title;
- current state;
- concise explanation;
- why it matters;
- what it blocks, governs, or depends on;
- related checkpoints;
- related decisions/unknowns;
- authority or external owner when applicable;
- evidence/provenance where applicable;
- source artifact path.

For example, clicking "U1" should make it immediately obvious that:

U1: Who has final approval authority?

Status
Unresolved

Effect
Blocks M3 — Approval received

Why
The request cannot be treated as approved until the responsible authority is identified.

Source
artifacts/U1-approval-authority.md

The inspector should include an actual link to the small demo Markdown artifact.

Cross-navigation

Relationships shown in the inspector should themselves be interactive.

For example:

- click "U1";
- inspector shows "Blocks → M3 Approval received";
- click "M3";
- graph selects/highlights M3;
- inspector now shows the two unknowns blocking it.

Likewise, selecting a decision should show every checkpoint it governs.

Highlight the selected node and its immediate relationships while visually de-emphasizing unrelated graph elements.

Deep links

Support simple URL-fragment selection such as:

#U1
#D2
#M3

Reloading the page with that fragment should restore the corresponding selection.

This gives the prototype a real version of:

«link me directly to this decision or unknown.»

Do not build a router framework for this.

Artifact links

Create tiny fixture Markdown files for the decisions and unknowns so the inspector's source links are real within the prototype.

These are demo data only.

Do not write them into ".agent-wayfinder/", and do not treat them as actual current project state.

Responsive behavior

Desktop is primary, but make the layout degrade coherently.

At normal desktop widths:

- graph remains visible;
- inspector occupies roughly one-third of the workspace;
- inspector does not overlap the graph.

At narrow widths:

- allow the inspector to become a drawer or stack below the graph;
- preserve basic interaction and legibility.

Accessibility

At minimum:

- graph nodes must be keyboard-focusable;
- Enter/Space selects a focused node;
- selected state is visible;
- text contrast is reasonable;
- relationship meaning does not depend on color alone.

Do not build an accessibility framework.

Tests and validation

Treat this primarily as a visual/interaction prototype, but verify it rather than merely writing files.

Verify at least:

1. The prototype serves locally without a build step.
2. The initial graph is legible at common desktop dimensions.
3. Every node can be selected.
4. Selecting a node updates the inspector correctly.
5. Related-node links cross-navigate correctly.
6. URL fragments restore selections.
7. "U1" and "U2" visibly block only the checkpoint(s) they actually affect.
8. "U3" can remain unresolved without falsely marking the current route blocked.
9. Decision relationships do not masquerade as factual or authority-free decisions.
10. The prototype does not modify Wayfinder's production contracts, ADRs, routing, storage, or runtime.

If a browser automation or screenshot capability already exists in the environment, use it to inspect the prototype at desktop size and correct obvious layout defects.

Do not add a browser-testing dependency solely for this prototype.

Design discipline

The objective is to answer:

«Is this a substantially better human interface to the coordination model?»

It is not to answer yet:

«How should Agent Workflow permanently implement a visualization system?»

Therefore do not add:

- a map parser;
- a graph schema to the Wayfinder contract;
- automatic file watching;
- a server;
- a database;
- an API;
- a plugin;
- a new CLI command;
- lifecycle machinery;
- migration logic;
- compatibility logic;
- or production installation behavior.

Keep the data model inside the prototype clean enough that a future experiment could populate it from real state, but stop there.

If the most attractive visual design would require a large new mechanism, simplify the visual instead.

Output and Git

When complete:

- review the resulting prototype critically rather than assuming the first visual layout is good;
- make one refinement pass for hierarchy, spacing, relationship readability, and inspector usefulness;
- run available validation;
- commit the coherent prototype;
- push "prototype/wayfinder-plan-map" to "origin".

Then report:

- branch and commit SHA;
- files created;
- exact local command to open the prototype;
- what interaction model you implemented;
- what materially improved over the old dependency-only graph;
- any visual or usability limitation that remains;
- verification performed;
- confirmation that no production Wayfinder semantics or contracts changed.

Do not merge or open a pull request.