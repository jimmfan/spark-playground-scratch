# Implement ARC Wayfinder Reference-Inheritance Cleanup — Phases 1 and 2

Continue from the reference-inheritance audit you completed in this conversation.

Use the prior conversation to understand the problem, but do not rely on prior reasoning as repository truth. Before editing, re-read and verify:

* the current Git state;
* the committed audit;
* current target-repository contents;
* applicable `AGENTS.md` and Wayfinder instructions;
* tests and verifiers;
* accepted ARC decisions;
* and the checked-out revisions of the reference repositories.

When prior conversation conclusions conflict with current repository evidence, current repository evidence wins.

## Target branch and audit

Work only in the existing `ghec-eks-arc-runners` checkout and only on this existing branch:

```text
fix/wayfinder-reference-inheritance
```

The branch has already been pushed. Do not create another branch or worktree.

The committed audit is expected at:

```text
fix-wayfinder reference/plans.md
```

Because the path contains a space and may differ slightly, verify its exact tracked path:

```bash
git ls-files '*plans.md'
```

Read the complete relevant audit before editing. Treat it as the reviewed evidence inventory and implementation plan, subject to verification against current repository truth.

Do not edit the audit file.

Do not push, merge, rebase, reset, force-push, or rewrite branch history.

Local commits are permitted after verification.

## Goal

Implement the safe portions of Phases 1 and 2 so that the ARC durable state:

* begins from a smaller, minimally assumed baseline;
* contains only facts established and materially applicable to ARC;
* retains real migration constraints from the existing runner system;
* keeps useful `ccoe-ami`, CDER/Coder, and other neighboring-project observations as accurately sourced evidence;
* does not silently turn reference-project choices into ARC requirements, architecture, or decisions;
* separates external observations from ARC inferences, expected benefits, recommendations, and design choices;
* keeps unresolved authority and architecture questions visibly unresolved;
* preserves truthful provenance and traceability;
* and uses the existing facts, evidence, unknowns, and decisions model without introducing a new subsystem.

Do not implement ARC infrastructure or decide unresolved architecture.

## Preflight

Before making any changes:

* Read every applicable `AGENTS.md`, Wayfinder contract, state-writing instruction, and repository verification instruction.
* Confirm the repository root.
* Confirm the current branch is exactly:

```text
fix/wayfinder-reference-inheritance
```

* Record:

  * current branch;
  * current `HEAD` SHA;
  * upstream branch and synchronization status;
  * working-tree status;
  * staged changes;
  * unstaged changes;
  * untracked files;
  * exact audit path.
* Identify the exact current Wayfinder effort directory.
* Locate its:

  * `facts.md`;
  * `evidence.md`;
  * `unknowns.md`;
  * `decisions.md`;
  * `map.md`;
  * contracts or state guidance;
  * related reference documents.
* Record the branch and SHA of every locally available reference repository before relying on it.
* Record the starting working-tree status of every reference repository.
* Review the audit’s description of prior cleanup commit `b162564` and verify it against Git history.
* Verify whether there are unrelated user changes in the target checkout.

Stop before editing if:

* the current branch is not `fix/wayfinder-reference-inheritance`;
* the audit cannot be located unambiguously;
* unrelated user changes overlap files required by this task;
* the current repository structure differs materially from the audited structure;
* or safe completion would require rewriting already-pushed history.

## Reference repositories

The local `reference-repos/` directory may remain physically inside the workspace while this task runs. The reference repositories should remain available for read-only inspection.

However, they must not be treated as ARC-owned source or included in the Phase 1 or Phase 2 commits.

Inspect exactly how the target repository tracks them:

```bash
git ls-files --stage -- reference-repos
git status --short -- reference-repos
find reference-repos -maxdepth 3 -name .git -print 2>/dev/null
test -f .gitmodules && cat .gitmodules || true
```

Also summarize the tracked modes:

```bash
git ls-files --stage -- reference-repos |
  awk '{print $1}' |
  sort -u
```

Apply the following rules.

### Case 1 — `reference-repos/` is not tracked

If `git ls-files --stage -- reference-repos` returns no entries:

* Leave the local directories where they are.
* Treat them as read-only.
* Add this entry to the local `.git/info/exclude` only when it is not already excluded:

```text
/reference-repos/
```

* Do not add this operator-specific workspace layout to the project `.gitignore`.
* Continue with Phases 1 and 2.

### Case 2 — Only embedded-repository pointers are tracked

If every tracked entry has Git mode `160000`, and there is no intentionally approved `.gitmodules` configuration:

* Treat the entries as accidental embedded-repository pointers.
* Remove only those pointers from the ARC Git index while preserving the local reference-repository directories and their contents.
* Do not delete the local repositories.
* Add `/reference-repos/` to `.git/info/exclude`.
* Verify that all reference repositories remain locally readable and unchanged.
* Create a separate preliminary commit:

```text
chore: stop tracking local reference repositories
```

* Continue with Phases 1 and 2.

If `.gitmodules` intentionally defines them as approved submodules, stop and report the conflict rather than changing them.

### Case 3 — Ordinary reference-repository files were committed

If any tracked entries under `reference-repos/` use ordinary file modes such as `100644` or `100755`:

* Stop before making Phase 1 or Phase 2 changes.
* Do not delete the files.
* Do not rewrite history.
* Do not reset or force-push.
* Do not continue merely by adding a deletion commit.

Report:

* the number of committed files;
* which reference repository directories are affected;
* the commits that introduced them;
* whether they remain present at the current branch tip;
* whether they appear to come from repositories with different access restrictions;
* and whether any suspicious credential, secret, internal endpoint, or sensitive configuration files may have been copied.

Explain whether safe correction appears to require rewriting the unmerged branch history or another explicit user decision.

Wait for user authorization before continuing.

## Authority

Apply this authority order:

1. The user decisions in this prompt.
2. Current target-repository source, Git state, tests, accepted ARC decisions, and explicit ARC requirements.
3. Current statements from identified ARC owners or maintainers, including their date, forum, scope, and authority.
4. Reference repositories as evidence about their own implementation at a recorded revision.
5. Inference, analogy, or hypothesis.

A reference repository is authoritative about what it implements at a particular revision. It is not automatically authoritative about what ARC must implement.

Do not infer an organization-wide mandate from a convention found in one repository.

Do not promote a proposed or copied architecture decision into accepted ARC authority without verifying its lifecycle status, scope, and authority.

## User-approved treatment of reference material

The following is an explicit user decision and may be implemented without further authority:

* Retain specific, useful observations from `ccoe-ami`, CDER/Coder, and other neighboring repositories as accurately named, non-binding evidence.
* Do not restore or preserve broad CDER/Coder conventions as ordinary ARC design guidance.
* Do not anonymize real repository names, paths, commits, or source citations.
* Possible or likely reuse of `ccoe-ami` is not a decision to preserve:

  * Amazon Linux 2023;
  * the current Packer process;
  * the baked toolchain;
  * host Docker;
  * the current refresh schedule;
  * `regina-bot`;
  * or any other current implementation choice.
* A reference implementation choice becomes an ARC fact, requirement, or decision only after its ARC applicability and authority are independently established.
* Unanswered authority questions must remain unknown or provisional rather than being guessed.
* Unanswered authority questions do not block safe mechanical repairs or the demotion of unsupported certainty.

## Durable facts-writing rule

Add this concise rule to the existing guidance or header section of the current ARC effort’s `facts.md`:

> Only include facts here that are established and materially applicable to ARC. Facts about other systems belong in evidence unless they directly constrain ARC. Keep ARC inferences, recommendations, and design choices separate.

Do not create a new policy file, authority registry, state type, or framework subsystem for this rule.

## Phase 1 — Safe cleanup and reclassification

Phase 1 includes both objective mechanical repair and evidence-supported semantic reclassification.

Use two separate commits so mechanical corrections can be reviewed independently from changes in classification.

### Phase 1A — Mechanical repairs

Implement the objective path, reference, formatting, and citation repairs identified by the audit.

At minimum:

* Repair U18’s stale `infrastructure/runners/` reference so it points to the current valid ARC location.
* Correct or remove the stale `dependency-graph.md` reference.
* Fix the nonexistent U12 cross-reference.
* Correct the stale decision-workbook path.
* Remove or repair instructions referring to a nonexistent “Resolution” section.
* Correct `map.md` where it claims Terraform conventions were moved into an empty or non-equivalent `terraform/README.md`.
* Repair stale links, headings, anchors, and paths introduced by prior directory or heading renames.
* Restore the docs-authoring formatting regression identified in the audit.
* Correct false statements that removed material was preserved or moved elsewhere when it was not.
* Check relevant line-number citations against the recorded source-repository revision.
* Where a citation now points to changed content:

  * use the original historical revision when available;
  * otherwise reverify against the current revision and explicitly update the evidence date and limitation;
  * do not silently present current `HEAD` as the source of an older observation.
* Preserve literal repository names and source paths.

During Phase 1A:

* Do not alter claim classifications except when required to correct an objectively false reference.
* Do not renumber state IDs.
* Do not change workflows, implementation code, or generated graph data.

After focused verification, create:

```text
fix: repair stale wayfinder references and links
```

Use exact-path staging. Do not use `git add .` or `git add -A`.

### Phase 1B — Semantic reclassification

Implement the audit-supported separation between ARC truth and external evidence.

For every affected entry, identify:

* what the source actually proves;
* which system it describes;
* whether it directly constrains ARC;
* whether applicability to ARC was independently established;
* whether it is fact, migration constraint, evidence, decision, unknown, inference, hypothesis, or volatile snapshot;
* and whether a future agent could reasonably mistake it for something ARC must preserve.

Do not retain an item in `facts.md` merely because it is accurately sourced.

#### F9–F15 — Existing runner fleet and `ccoe-ami`

Use `ccoe-ami` as important evidence about the existing runner fleet, without treating possible reuse as an ARC decision.

* **F9:** Preserve that the current fleet uses an Amazon Linux 2023-based image as legacy implementation evidence. Do not treat Amazon Linux 2023, the existing image build, or Packer as selected ARC architecture.
* **F10:** Move the weekly Auto Scaling Group refresh schedule and similar operational detail to legacy evidence unless a narrowly stated part directly constrains coexistence or migration.
* **F11:** Treat host Docker as existing-system evidence and a compatibility question. Do not call it an ARC requirement without evidence from the workflows ARC must support.
* **F12:** Preserve the bounded observation that sampled workflows use job containers. Separate that observation from any conclusion about ARC’s required execution model.
* **F13:** Move the detailed baked-toolchain inventory to evidence. Do not infer that ARC requires a custom image or must reproduce the accumulated tool list.
* **F14:** Treat GitHub OIDC usage as an observed practice in the examined workflows, not an organization-wide policy or a complete ARC pod-identity decision.
* **F15:** Split the verified legacy observation from the ARC prediction:

  * explicit cleanup of offline legacy runner registrations is an existing-system observation;
  * any claim that JIT registration will remove or reduce the burden is an ARC hypothesis, expected benefit, or decision rationale.

Keep only existing-system conditions that directly constrain ARC coexistence, compatibility, migration, or cutover as narrowly written ARC migration facts.

#### F16–F21 — CDER/Coder reference material

Use CDER/Coder as prior art rather than an ARC blueprint.

* **F16:** Retitle and scope it so it describes the actual reference cluster. Move module versions, Kubernetes versions, and other volatile pins into dated evidence.
* **F17:** Treat private-only API access, subnet tags, and related configuration as reference-project evidence unless ARC independently adopted them.
* **F18:** Preserve the bounded result that the specified examined repositories did not create VPC resources. Remove any appended inference that ARC therefore should consume existing networking or avoid managing network resources.
* **F19:** Separate:

  * what the ADR text says;
  * the ADR’s lifecycle status;
  * the authority behind it;
  * any agent interpretation;
  * and unresolved implementation choices such as IRSA versus EKS Pod Identity.
* **F20:** Correct the entry to match the cited Terraform source, including exceptions. Do not preserve a claim that every role has a boundary when the source contradicts it. Leave the organization-wide mandate and the applicable ARC boundary ARN unresolved unless current authoritative evidence establishes them.
* **F21:** Split:

  * any independently supported ARC phased-migration constraint;
  * from the CDER/Coder delivery-chain observation.

  The fact that an examined project uses GitHub Actions, Artifactory, Harness, or Terraform Cloud does not automatically establish ARC’s delivery architecture.

Do not solve these issues by replacing `CDER` or `Coder` with “reference environment.”

#### F24–F25 — Network observations

* Move repository-visible CIDRs and historical range lists out of established ARC facts.
* Preserve useful values only as dated, incomplete evidence.
* State that an authoritative current IPAM/network inventory and ARC allocation process remain unresolved.
* Do not treat absence of overlap in a bounded repository scan as enterprise-wide non-overlap validation.
* Do not present the historical list as final ARC allocation.

#### F27c and related Artifactory claims

* Narrow the entry to the Artifactory or Helm behavior directly supported by available evidence.
* Remove “container registry” or equivalent wording unless the cited source directly establishes that behavior.
* When cited Artifactory or change-management documents are unavailable, retain truthful provenance and mark the relevant claim unverified.
* Do not invent generic replacement authority.

#### F40, F42, F44, F46, and other derived claims

* Preserve bounded derivations as inference or observed convention when that is all the sources support.
* Do not convert sampled repository behavior into enterprise-wide fact.
* For F46:

  * retain independently supported account or environment facts;
  * separate the disputed isolation conclusion;
  * preserve the contradiction with D2;
  * do not choose between runner-group repository scoping on shared infrastructure and separate cluster, VPC, or namespace isolation.

#### Decisions and unknowns

Review D2–D6 and all related unknowns.

* Keep proposed ADR-dependent decisions proposed or provisional unless current authoritative evidence proves approval.
* Keep D5 and D6 provisional when their authority or source remains unresolved.
* Do not silently promote a proposal because it appears plausible or is repeated elsewhere.
* Do not delete an unknown merely because a reference implementation suggests an answer.
* Preserve links between evidence, unknowns, and decisions.
* Do not renumber identifiers solely for cleanliness.

#### ARC-facing documentation

Correct outward-facing documentation so that it describes only:

* current repository truth;
* accepted ARC decisions;
* explicit requirements;
* or clearly labeled candidates, examples, or unresolved choices.

Specifically:

* Do not present reference-derived Terraform structure as established ARC structure.
* Remove or qualify IRSA-specific module or directory guidance while IRSA remains unresolved.
* Do not restore broad CDER conventions as ARC instructions.
* Keep useful prior art in evidence with accurate repository names and revisions.
* Remove generic wording that conceals the source of inherited assumptions.
* Do not claim deleted conventions were moved into an empty README.
* Preserve real migration constraints even when they originated in analysis of the old system.
* The root README should describe the repository as it exists or label proposed structure explicitly.

After focused verification, create:

```text
refactor: reclassify inherited reference claims
```

Use exact-path staging. Do not use broad staging commands.

## Phase 2 — Resolve what repository evidence can resolve and preserve authority questions

Review all unresolved questions identified by the audit, including Q1–Q9 and related questions scattered through the classification table.

Do not ask the user to answer questions that current authoritative repository artifacts can resolve.

### Safe agent resolution

Resolve an item only when current authoritative project evidence clearly establishes the answer.

Examples include:

* correcting a statement contradicted by its cited Terraform;
* determining whether a referenced file or workflow exists;
* determining an ADR’s checked-in lifecycle status;
* confirming whether an entry applies only to a reference repository;
* correcting a stale path;
* distinguishing current evidence from an outdated snapshot;
* or identifying the exact scope of a named maintainer statement already preserved in the repository.

For every resolved item, record:

* source;
* revision or date;
* scope;
* authority or basis;
* material limitation.

### Explicitly resolved user question

Treat the audit’s question about how to handle CDER/Coder and `ccoe-ami` precedent as resolved by this prompt:

> Retain only specific, useful, truthfully cited observations as non-binding evidence. Do not make broad reference-project conventions ARC guidance. Possible reuse is not adoption.

Apply that answer wherever relevant.

### Authority questions the agent must not guess

Unless current authoritative target-repository evidence genuinely resolves one, leave these unresolved:

* Whether every ARC IAM role requires a permissions boundary.
* Which permissions-boundary ARN applies.
* Which pilot-isolation model is authoritative.
* Whether ARC selected IRSA or EKS Pod Identity.
* What current authoritative CIDR/IPAM inventory and allocation process ARC must use.
* Whether inaccessible Artifactory or change-management documents remain current authority.
* Whether the ARC ADR has received human review or approval beyond its recorded lifecycle status.
* Who authorized the guidance behind D5 and D6 and whether there is a durable authoritative record.

For each unresolved authority question:

* Keep or create one canonical entry in the existing `unknowns.md`.
* State the minimum question clearly.
* State what downstream fact, decision, or implementation it blocks.
* Link the supporting and conflicting evidence.
* Record the evidence limitation.
* Identify the required owner or authority where known.
* Keep affected decisions provisional or proposed.
* Add backlinks from affected facts, evidence, and decisions where useful.
* Avoid duplicating the same question under multiple IDs.
* Do not create a separate authority-register file or subsystem.

When sources conflict:

* Preserve the conflict explicitly.
* Do not choose one source by inference.
* Prevent either source from appearing as an uncontested established ARC fact.
* Identify the authority required to resolve it.

### Traceability model

Use the existing Wayfinder files:

* observation about a legacy or reference system → `evidence.md`
* condition established and materially applicable to ARC → `facts.md`
* unresolved applicability or authority → `unknowns.md`
* accepted or provisional ARC choice → `decisions.md`

Preserve the reason a question existed through links rather than deleting its history after reclassification.

## Out of scope

Do not modify:

* Terraform implementation;
* Kubernetes manifests;
* Helm implementation;
* ARC runtime code;
* copied GitHub Actions workflows;
* `check-label.yaml`;
* `create-tag.yaml`;
* workflow-dispatch files;
* graph-generation scripts;
* committed generated graph data;
* reference repositories;
* the committed audit;
* global Agent Workflow framework source;
* or unrelated documentation.

Do not decide:

* the final ARC operating system;
* whether ARC reuses Packer or `regina-bot`;
* whether ARC requires a custom image;
* final toolchain contents;
* final host-Docker or job-container behavior;
* the final deployment chain;
* the final cluster topology;
* final network design;
* the permissions-boundary policy;
* or the pod-to-AWS identity mechanism.

Report suspicious workflows and generated artifacts in the final report, but do not repair, delete, or reclassify them as part of this branch.

## Verification

Discover and run all verification required by the repository’s instructions.

At minimum:

* Run the Wayfinder/state verifier.
* Run the repository’s full verification command.
* Validate Markdown links, headings, anchors, and state cross-references where supported.
* Search for every stale path and identifier called out in the audit.
* Confirm facts, evidence, unknowns, and decisions link consistently.
* Confirm literal repository names and source paths remain truthful.
* Confirm unresolved choices do not appear accepted.
* Confirm real migration constraints were not accidentally removed.
* Confirm no state IDs were unintentionally renumbered.
* Run:

```bash
git diff --check
```

* Review each complete commit diff, not only its summary.
* Confirm Phase 1 and Phase 2 did not modify:

  * `.github/workflows/`;
  * infrastructure implementation;
  * graph-generation files;
  * generated graph data;
  * the audit;
  * or reference-repository contents.
* Confirm every reference repository remains on its starting branch and SHA.
* Confirm every reference repository has no new working-tree changes.
* Confirm `reference-repos/` is absent from the mechanical and semantic commit contents.

When an automated check does not exist, perform a focused manual inspection and label it clearly as manual verification.

## Commit requirements

Permitted commits are:

### Preliminary repository-hygiene commit, only when safe and required

```text
chore: stop tracking local reference repositories
```

### Mechanical repair commit

```text
fix: repair stale wayfinder references and links
```

### Semantic reclassification and unknown-preservation commit

```text
refactor: reclassify inherited reference claims
```

Do not amend previously pushed commits.

Do not squash these commits.

Do not push or merge.

Use exact-path staging for every commit.

## Stop conditions

Stop and report before further changes if:

* ordinary reference-repository files were committed into the pushed branch;
* a required change would choose an unresolved ARC architecture, policy, or owner decision;
* an existing unrelated user change overlaps required files;
* the state contract materially differs from the audit;
* verification reveals broad corruption outside this scope;
* a reference repository would need to be modified;
* or safe completion requires branch-history rewriting.

Do not stop merely because an authority question remains unanswered. Demote unsupported certainty, preserve the question, and continue with safe work.

## Final report

Return a concise but complete report containing:

* starting branch and base SHA;
* exact committed audit path used;
* initial and final target-repository status;
* how `reference-repos/` was represented in Git;
* how it was handled;
* reference-repository branches and SHAs;
* preliminary hygiene commit SHA, if created;
* mechanical commit SHA;
* semantic commit SHA;
* files changed in each commit;
* objective repairs completed;
* entries retained as ARC facts;
* entries retained as migration constraints;
* entries moved to evidence;
* entries converted into unknowns or hypotheses;
* decisions left proposed or provisional;
* authority questions still unresolved;
* suspicious artifacts deliberately left untouched;
* automated verification commands and exact results;
* manual checks performed;
* failures, blockers, and unverified areas;
* final `git status`;
* whether the branch is ready for independent review;
* and explicit confirmation that nothing was pushed, merged, rebased, reset, or force-pushed.

Distinguish clearly between:

* verified corrections;
* implemented but manually verified changes;
* unresolved authority questions;
* recommendations;
* and work deliberately left out of scope.
