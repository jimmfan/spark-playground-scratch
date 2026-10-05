Use this as guidance rather than a rigid checklist. The goal is to deeply investigate the available repositories and identify knowledge we should extract from our departing Coder lead today. You may change the investigation approach or output structure if the evidence suggests a better direction. Prioritize important discoveries over exhaustive coverage.

The following constraints are firm:

- This is read-only. Do not modify repositories, create branches, commit changes, or change infrastructure.
- Distinguish VERIFIED facts from INFERRED conclusions and UNKNOWN areas.
- Cite repository names and file paths for important findings.
- Do not recommend asking the lead questions that you can confidently answer from the repositories.

Context

I understand the Coder workspace templates, AMI/image-building process, and several surrounding processes reasonably well.

My weaker areas include EKS, Kubernetes, Helm, and some of the infrastructure connecting the pieces together. However, do not restrict the investigation to those areas. I want you to discover risks I may not know to look for.

Treat all available repositories as components of one Coder platform rather than analyzing them independently.

What I need you to do

1. Reconstruct the system

Determine what each repository owns and how the pieces connect.

Trace the important paths across repositories, including where relevant:

- Terraform/AWS infrastructure
- EKS
- Kubernetes
- Helm
- IAM/workload identity
- networking, DNS, ingress, TLS
- Coder control plane
- database
- workspace provisioning
- persistent storage
- AMIs/images
- Coder templates
- CI/CD
- secrets
- monitoring/alerting
- upgrades and recovery

Follow actual references, outputs, values, workflows, manifests, scripts, and configuration across repositories.

Do not fill gaps with generic Kubernetes or AWS assumptions.

2. Find handoff risks

Focus on knowledge that may be difficult to reconstruct after the lead leaves.

Look especially for:

- implementation where the architectural rationale is unclear
- manual or externally managed resources
- production-only configuration or behavior
- deployment or upgrade sequencing
- rollback/recovery procedures
- known fragile areas
- unusual IAM/networking/storage decisions
- undocumented dependencies
- version compatibility constraints
- operational troubleshooting knowledge
- historical incidents/workarounds
- areas disproportionately maintained by the departing lead
- upcoming work or technical debt that may not be visible in the repositories

Ask yourself:

If Coder breaks next Monday, what will we wish we had asked him today?

And:

If we had to rebuild this platform from these repositories alone, what important information would still be missing?

3. Separate repository knowledge from tribal knowledge

For each important uncertainty, classify it as:

- Repo-answerable: you can determine the answer confidently. Answer it yourself.
- Partially recoverable: substantial evidence exists but rationale or operational details remain unclear.
- Human/tribal knowledge: unlikely to be reliably reconstructed once the lead leaves.

Our limited meeting time should primarily be spent on the third category.

4. Build today's interview

Create a focused list of questions for the departing lead.

Rank them:

- P0 — Ask before he leaves
- P1 — Ask if time remains
- Don't ask — repositories already answer this

For each P0 question, tell me:

- the question
- why it matters
- what you already discovered in the repositories
- exactly what information is still missing

Avoid generic Kubernetes questions. Questions should emerge from evidence you found in our system.

Areas worth investigating

These are starting points, not a mandatory checklist:

- What is the actual production deployment path?
- Which repo/system is authoritative for each layer?
- What exists outside Terraform/Git/Helm?
- Which Helm values or infrastructure settings are dangerous to change?
- How do IAM, networking, DNS, TLS, ingress, storage, and secrets fit together?
- What happens when nodes disappear or workspaces fail?
- How are Coder/EKS/Helm upgrades performed and rolled back?
- What is backed up and how is it restored?
- What monitoring does an experienced operator look at first?
- What failures have happened historically?
- What manual processes or known workarounds exist?
- What upcoming changes should the remaining team know about?

Do not limit yourself to these questions.

Final output

Give me:

1. A concise architecture explanation.
2. The largest knowledge-transfer risks you discovered.
3. P0 questions for today's meeting.
4. P1 questions if time remains.
5. Important questions that the repositories already answered, with those answers.
6. External/manual dependencies or unclear sources of truth.
7. Exactly five questions to ask if I only get five minutes with the lead.

The main objective is not to produce a comprehensive report. It is to find the small amount of important knowledge that could disappear when this developer leaves.