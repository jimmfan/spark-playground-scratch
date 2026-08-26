ARC Wayfinder Reference-Inheritance Audit

Audit the durable Wayfinder state and related documentation in the current "ghec-eks-arc-runners" repository.

This is an audit-only task. Do not edit, create, delete, rename, format, regenerate, stage, commit, stash, reset, check out, or push anything in any repository. Return findings and recommendations only.

Workspace and repository state

The target repository is:

ghec-eks-arc-runners/

The following sibling repositories should be available as read-only references:

../ccoe-ami/
../aws-eks-cder/
../aws-eks-cder-helm/
../cder-workspaces/

At the beginning:

- Read all applicable "AGENTS.md", Wayfinder contracts, and repository instructions in the target repository.
- Record the target repository’s current branch, "HEAD" SHA, working-tree status, and untracked files.
- Record the checked-out branch and SHA of each available reference repository.
- Treat committed "HEAD" in "ghec-eks-arc-runners" as the canonical baseline.
- Treat any current uncommitted changes as Claude’s candidate cleanup, not as approved project truth.
- Audit the committed baseline and the uncommitted diff separately.
- If a reference repository is unavailable, record that limitation and continue.
- Do not clone, fetch, pull, switch branches, or modify any repository.
- Read-only Git inspection such as "status", "diff", "show", "log", "grep", and "rev-parse" is allowed.

Keep progress updates brief. Put the substantive analysis in the final audit report.

User intent

ARC should begin from a smaller, minimally assumed baseline.

External and legacy repositories are useful sources of evidence, but their implementation choices must not silently become immutable ARC facts, constraints, requirements, or decisions.

In particular:

- "ccoe-ami" contains important information about the existing self-hosted runner fleet.
- ARC may later reuse parts of "ccoe-ami", but possible or likely reuse is not a decision to preserve its operating system, AMI-building process, baked toolchain, refresh schedule, Docker model, registration process, or other implementation choices.
- The CDER/Coder repositories are prior art from an internal EKS developer-workspace platform with a different workload and behavior.
- CDER/Coder may demonstrate that a pattern is possible or reveal an observed convention, but it is not the ARC design blueprint.
- Literal repository names, paths, revisions, and source citations must remain truthful.
- Replacing "CDER" or "Coder" with generic wording such as “reference environment” does not solve the problem when the underlying external assumption still governs ARC.
- Current ARC facts should describe verified ARC conditions, material migration constraints, or independently applicable requirements.
- Accepted ARC choices should be represented as decisions with clear status and authority.
- Unresolved applicability, authority, or design choices should remain visibly unresolved.
- Legacy and reference implementation details should default to non-binding evidence unless their applicability to ARC is independently established.

The goal is not to erase useful research. The goal is to stop facts about adjacent systems from masquerading as facts or decisions about ARC.

Authority

Use this authority order:

1. The user intent in this prompt.
2. Current target-repository source, Git state, tests, accepted ARC architecture decisions, and explicit ARC requirements.
3. Current statements from identified ARC owners or maintainers, with their scope and date.
4. Reference repositories as evidence about their own implementation at a recorded revision.
5. Inference, analogy, or hypothesis.

A reference repository is authoritative about what it implements at a particular revision. It is not automatically authoritative about what ARC must implement.

Do not infer an organization-wide policy from a convention found in one repository.

Do not treat an architecture decision as accepted ARC authority without checking its lifecycle status, scope, and applicability.

Hypothesis

Wayfinder may have promoted accurately sourced observations from "ccoe-ami", CDER/Coder repositories, and other neighboring sources into ARC facts, design direction, decisions, or documentation without adequately establishing:

- applicability to ARC,
- governing authority,
- migration relevance,
- durability,
- or explicit ARC adoption.

Some entries may also combine different kinds of claims—for example, a sourced observation about an old system followed by an inference or expected benefit for ARC—while labeling the entire entry "established".

Claude’s current candidate cleanup may reduce visible CDER/Coder naming without correcting these inherited assumptions.

Audit scope

Inspect the complete current Wayfinder effort and all related target-repository material. Do not limit the review to literal occurrences of "CDER", "Coder", or "ccoe-ami".

At minimum, inspect:

- "facts.md"
- "decisions.md"
- "evidence.md"
- "unknowns.md", open-question files, or their equivalents
- "map.md"
- Wayfinder contracts and instructions
- root and infrastructure "README.md" files
- documents under "docs/"
- architecture-decision and reference documents
- generated navigation or graph artifacts where relevant
- ".github/workflows/"
- all external repositories and files cited by the durable state
- the complete current uncommitted diff

Build an inventory of every target-repository claim materially derived from an external, legacy, or neighboring project.

For each claim, determine:

- What does the cited source actually prove?
- Is the claim about ARC, the existing runner fleet, a reference project, an observed convention, or a broader organizational condition?
- Is its basis source evidence, explicit authority, an accepted decision, a proposed decision, inference, analogy, or hypothesis?
- Was its applicability to ARC independently established?
- Does ARC have to account for it during coexistence, migration, or cutover?
- Could ARC validly choose a different implementation without violating a real requirement?
- Is it durable project knowledge or a dated repository snapshot?
- Does the entry combine an observation with an ARC inference, recommendation, expected benefit, or decision?
- Could a future agent reasonably misread it as something ARC must preserve?
- Is the information useful but too detailed or non-binding for the active ARC fact ledger?

Also identify executable workflows, instructions, or other artifacts that appear copied from a reference repository without a demonstrated ARC purpose. Report them separately; do not modify or delete them.

Classifications

Use the smallest accurate classification for each item:

- ARC fact: independently established and materially true for ARC.
- ARC migration constraint: an existing condition ARC must account for during coexistence, migration, or cutover.
- Authority-backed requirement: an applicable requirement established by an authorized owner, accepted decision, policy, or equivalent authority.
- Accepted ARC decision: a choice explicitly selected for ARC with verified status and authority.
- Candidate ARC choice: an option under consideration but not yet selected.
- Legacy implementation evidence: a sourced observation about the existing runner fleet.
- Reference-project evidence: a sourced observation about CDER/Coder or another neighboring implementation.
- Observed convention: a pattern that may suggest a broader rule but does not prove one.
- Inference or hypothesis: an expected implication, benefit, or conclusion that has not been verified.
- Unknown: an unresolved question about applicability, authority, ownership, compatibility, or target behavior.
- Volatile snapshot: versions, CIDRs, branch contents, schedules, or similar details likely to change and not backed by an authoritative current inventory.
- Irrelevant or accidental carryover: material that does not meaningfully inform ARC.
- Suspected copied artifact: executable or instructional content inherited without a demonstrated ARC purpose.

A statement may be fully established as true about another system while remaining non-binding for ARC.

Do not equate "Status: established" with “authoritative or binding for ARC.” Evaluate both truth and applicability.

Representative cases

These examples calibrate the audit but do not predetermine the results and are not the complete scope.

F9–F15: existing fleet and "ccoe-ami"

Determine which details are genuine ARC migration or compatibility constraints and which are only observations about the existing implementation.

Pay particular attention to:

- Amazon Linux 2023
- the existing AMI and Packer process
- weekly Auto Scaling Group refreshes
- Docker running on the host
- workflow job containers
- the baked toolchain
- GitHub OIDC usage
- offline or zombie runner cleanup
- claims that JIT registration will remove an operational burden

Possible reuse of "ccoe-ami" does not make these choices immutable.

Separate observed current behavior from:

- an ARC requirement,
- a future implementation choice,
- a compatibility question,
- and a predicted ARC benefit.

F16–F20: CDER/Coder precedent

Determine whether these entries describe only the reference implementation or something ARC independently adopted.

Pay particular attention to:

- EKS Auto Mode
- EKS module and Kubernetes versions
- API authentication settings
- private-only EKS API access
- tagged subnet discovery
- whether ARC creates or consumes networking
- prohibiting long-lived credentials
- IRSA versus EKS Pod Identity
- permissions boundaries
- claims based on an unverified organizational policy

For negative findings such as “none of the examined repositories creates VPC resources,” preserve the bounded search result without turning it into an organization-wide conclusion or an ARC design decision.

For ADR-derived statements, verify whether the ADR is accepted, proposed, historical, copied, or unresolved.

F21: mixed evidence and authority

Separate:

- details of the reference project’s Terraform delivery chain, and
- any current ARC maintainer clarification that migration will be phased and existing runners will remain available.

The latter may be a real ARC migration fact even when the former is only reference evidence.

F24–F25: CIDRs and network observations

Determine whether these are merely repository-visible, dated observations rather than:

- an authoritative network inventory,
- an enterprise-wide non-overlap check,
- or final ARC network allocation.

Do not let raw repository snapshots substitute for current network authority.

Claude’s current candidate cleanup

Assess whether the uncommitted changes:

- correctly separate prior art from ARC truth,
- merely replace "CDER" or "Coder" with generic terms,
- preserve inherited design assumptions under less visible wording,
- move reference-project choices into ARC-facing Terraform documentation,
- obscure or weaken provenance,
- introduce unsupported ARC conclusions,
- correct valid stale links or paths,
- modify unrelated operational instructions,
- or touch workflows and executable artifacts beyond safe documentation cleanup.

Do not assume generic wording is more accurate.

Required output

Return one focused audit report with five sections.

1. Repository state and executive verdict

Report:

- target branch and "HEAD" SHA
- target working-tree status
- concise description of any current candidate diff
- each available reference repository’s branch and SHA
- unavailable or unverifiable sources

Then give one verdict:

- "SUPPORTED"
- "PARTIALLY SUPPORTED"
- "NOT SUPPORTED"

State plainly:

- whether reference inheritance is a real problem,
- its practical severity,
- whether the committed baseline overstates external authority,
- and whether Claude’s candidate cleanup materially solves it.

2. Claim-classification inventory

Produce a table with these columns:

| ID or file | Current claim | Source and revision | What the source proves | Applies to | Current problem | Recommended classification | Recommended disposition | Human decision needed |

Use concrete dispositions such as:

- keep
- narrow
- split
- move to evidence
- move to decisions
- convert to unknown
- retain as migration constraint
- retain citation but rewrite interpretation
- remove from active state
- investigate separately

Group mechanically identical items when appropriate, but do not combine materially different claims or lose traceability to fact and decision IDs.

3. Minimal-assumption ARC baseline

Provide two concise groups:

Safe to treat as established now

Include only independently supported ARC truths, authority-backed requirements, accepted decisions, and real migration constraints.

Must remain unresolved or non-binding

Include reference implementation choices, candidate reuse, observed conventions, volatile snapshots, unsupported inferences, and unresolved authority questions.

Keep the established baseline intentionally small.

4. Claude diff and suspicious artifacts

For Claude’s current candidate diff, identify:

- sound corrections
- cosmetic renaming that leaves the underlying problem
- unsupported or harmful changes
- unrelated but potentially valid fixes
- items requiring user approval

Then list any suspicious copied workflows or artifacts, including examples such as "create-tag.yaml", "check-label.yaml", or workflow-dispatch files when present.

For each suspicious artifact, report:

- apparent origin
- current ARC purpose or lack of one
- whether it appears executable in this repository
- missing dependencies or referenced reusable workflows
- recommended separate investigation

Do not repair or delete anything.

5. Recommended implementation plan and unresolved authority questions

Provide a small, ordered implementation plan using exact target-repository paths.

Separate:

- mechanical reclassification and cross-reference work
- changes requiring human authority
- workflow or executable-artifact investigations
- verification checks

Use the exact implementation branch name:

fix/wayfinder-reference-inheritance

Do not create the branch or implement the plan.

Ask only questions that require genuine user, owner, security, IAM, networking, or platform authority and cannot be answered from the available repositories.

For each question, state what classification or design choice it blocks.

Constraints

Do not:

- globally replace "CDER", "Coder", or "ccoe-ami"
- alter truthful repository names or source paths
- anonymize provenance
- treat observed conventions as organizational mandates
- treat bounded negative searches as proof of general absence
- treat likely reuse as an ARC decision
- preserve detailed legacy facts merely because they might eventually be useful
- delete or repair workflows during this audit
- introduce a new state type, registry, or documentation subsystem
- generate a patch
- make any repository change
- begin the implementation pass

Stop after returning the audit report.