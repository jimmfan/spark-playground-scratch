ARC Runners on EKS — Implementation Plan

Goal

Build a production EKS platform for GitHub Actions Runner Controller (ARC) using the company's required deployment path, proving each layer works before adding the next one.

At the highest level:

FOUNDATION

Cloud/network requirements
        ↓
GitHub → Harness → Terraform Cloud → AWS
        ↓

PLATFORM

EKS
        ↓
ARC
        ↓
First successful runner job
        ↓

ADOPTION

Company runner image
        ↓
Real workloads
        ↓
Production hardening and migration

Guiding Rule

«Solve what is necessary to safely complete the next phase. Important future questions should be recorded, but they do not need to be answered until they become relevant.»

---

Phase 1 — Understand the Foundation

Goal

Collect the company-specific inputs and requirements we must use rather than designing around assumptions.

Important things to confirm

Cloud/network

- AWS account and region
- Existing VPC
- Private subnets and Availability Zones
- Routing/NAT/proxy model
- DNS requirements
- Firewall/egress restrictions
- How the private EKS API is accessed
- Approved container registry

The Cloud/platform team can own the underlying VPC/networking while this project consumes it and identifies what EKS and the runners need.

Delivery process

Confirm the established implementation of:

GitHub
   ↓
Harness
   ↓
Terraform Cloud
   ↓
AWS

We are not choosing whether to use this architecture. It is a project requirement.

The goal is to understand how the company already implements it so we can reuse that approach.

Secrets/Vault

At this point we only need to understand:

- Whether Vault is the required secret source
- How GitHub/Harness/Terraform Cloud normally obtain credentials
- How Terraform Cloud authenticates with AWS
- Who owns the relevant Vault paths, roles, and policies
- What we need to request rather than create ourselves

We do not need to design every ARC or runner secret yet.

Done when

We know:

- Where EKS will run
- How infrastructure must be deployed
- The high-level authentication/secrets model
- Who owns the things this project depends on

There should be no foundational unknown that prevents us from building the deployment pipeline.

---

Phase 2 — Establish the Infrastructure Deployment Path

Goal

Make the company's required infrastructure delivery path work for this repository before depending on it to create EKS.

GitHub
   ↓
CI / approved trigger
   ↓
Harness
   ↓
Terraform Cloud
   ↓
AWS

Important work

Set up the minimum required pieces, such as:

- GitHub workflow/configuration
- Harness pipeline/configuration
- Terraform Cloud project/workspace
- Repository/workspace connection
- Required variables
- Required Vault/secrets integration
- Terraform Cloud → AWS authentication
- Required approvals/gates

Prefer the company's existing patterns instead of inventing ARC-specific ones.

Secret-management goal

Prove that the deployment systems can authenticate without putting long-lived passwords, tokens, or AWS keys into:

- Git
- Terraform files
- workflow YAML
- committed Harness configuration

Done when

«A change in this repository can successfully travel through the approved GitHub → Harness → Terraform Cloud process and Terraform Cloud has the authorized ability to plan/apply infrastructure in the intended AWS account.»

We don't need ARC yet.

We need a trustworthy road from Git to AWS.

---

Phase 3 — Build and Validate EKS

Goal

Use the deployment path from Phase 2 to create a working Kubernetes platform.

Build

Implement the required EKS infrastructure, including as appropriate:

- EKS control plane
- Private endpoint
- Managed node groups
- Launch templates
- Cluster and node IAM roles
- AWS workload identity/OIDC requirements
- Security groups
- VPC CNI
- CoreDNS
- kube-proxy
- EBS CSI
- Control-plane logging

Keep the Terraform understandable and avoid unnecessary abstraction early.

Example:

terraform/
└── eks/
    ├── main.tf
    ├── providers.tf
    ├── variables.tf
    ├── outputs.tf
    └── ...

Deploy it the real way

The important test is not:

terraform apply from laptop

It is:

GitHub
   ↓
Harness
   ↓
Terraform Cloud
   ↓
AWS
   ↓
EKS created

That proves both the infrastructure and its operating model.

Validate EKS independently

Check that:

- Cluster is healthy
- Managed nodes join
- Nodes report "Ready"
- Required add-ons are healthy
- Kubernetes DNS works
- A simple pod can run
- Logging works
- The private API can be reached through the approved path

Done when

«EKS is deployed through the required enterprise pipeline and can independently run a normal Kubernetes workload.»

Do not troubleshoot ARC until this works.

---

Phase 4 — Deploy ARC and Establish ARC Authentication

Goal

Connect the working EKS cluster to GitHub through ARC.

Use GitHub's supported ARC deployment model and the company's approved Harness deployment process.

Conceptually:

arc/
├── controller.values.yaml
└── runner-set.values.yaml

Avoid creating our own Helm chart unless an actual company requirement makes that necessary.

Deployment path

Determine the established company pattern for deploying Helm workloads through Harness.

This may differ slightly from the Terraform infrastructure path.

For example:

Infrastructure:

GitHub
 → Harness
 → Terraform Cloud
 → AWS/EKS

versus potentially:

Kubernetes workload:

GitHub
 → Harness
 → Helm deployment
 → EKS

We should reuse whatever Helm deployment pattern the organization already supports rather than design a new one.

ARC authentication/secrets

Now we solve the second secret problem:

«How does ARC authenticate with GitHub?»

Determine:

- Approved GitHub authentication method
- Where the credential lives
- How ARC receives it
- How Vault/Harness/Kubernetes participate

Do not hard-code the credential into Git, Terraform, Helm values, or the runner image.

Only implement the secret integration needed for ARC.

Start small

Use one runner scale set and minimal capacity.

The purpose is proving connectivity—not production sizing.

Done when

- ARC components are healthy
- ARC authenticates successfully with GitHub
- Credentials travel through the approved secret path
- A runner scale set is registered and ready for work

---

Phase 5 — Prove One GitHub Actions Job

Goal

Prove the complete system using the simplest possible workflow.

GitHub Actions
      ↓
ARC
      ↓
EKS
      ↓
ephemeral runner pod
      ↓
job runs
      ↓
runner disappears

Use a deliberately boring test.

For example:

jobs:
  arc-smoke-test:
    runs-on: arc-runner-set

    steps:
      - run: |
          echo "ARC runner is working"
          uname -a
          whoami

Do not add Terraform, AWS access, internal systems, or complicated tooling yet.

Done when

«One GitHub Actions job successfully runs from beginning to end on an ephemeral ARC runner.»

This is one of the most important milestones in the project.

At this point we have independently proven:

- Deployment pipeline
- EKS
- ARC
- GitHub authentication
- Basic GitHub network connectivity
- Runner creation/destruction

---

Phase 6 — Build the Company Runner Image

Goal

Replace the basic runner with the image developers will eventually use.

Start with the smallest company-approved image possible.

Example:

runner-image/
└── Dockerfile

It might initially contain:

GitHub runner requirements
        +
corporate CA certificates
        +
Git
        +
basic utilities
        +
required security configuration

Then add tooling as requirements become real:

- AWS CLI
- Terraform
- Python
- Node
- kubectl
- Helm
- other approved tools

CI/CD for the image

This is where the pipeline grows to include:

Dockerfile change
        ↓
CI validation/testing
        ↓
build image
        ↓
security/image checks
        ↓
publish to approved registry
        ↓
Harness deployment/update
        ↓
ARC uses new image

Do not put passwords, tokens, AWS keys, Vault tokens, or other secrets inside the image.

Validate

Repeat the Phase 5 smoke test using the company image.

Done when

«The same basic GitHub Actions job succeeds using the company runner image delivered through the approved build/deployment process.»

---

Phase 7 — Validate Real Workloads, Networking, and Workload Secrets

Goal

Move from:

«ARC works.»

to:

«ARC can actually perform the jobs our developers need.»

Introduce requirements incrementally.

For example:

basic shell job
    ↓
AWS API access
    ↓
internal package/artifact access
    ↓
Terraform/deployment job
    ↓
representative existing workflow

Networking

Build a simple list of actual destinations runners require.

For example:

Destination| Why
GitHub| Runner communication
Container registry| Pull runner images
AWS APIs| AWS workloads
Artifact repository| Dependencies
Internal APIs| Workflow-specific

Add destinations when a real workflow requires them instead of attempting to predict everything now.

Workload secrets

This is the third secret problem.

For each workload determine:

What credential does it need?
        ↓
Where should it live?
        ↓
How does the job obtain it?
        ↓
What is the minimum access required?

Reuse the company's Vault and identity patterns.

Do not invent a separate ARC-specific secrets system.

Done when

«At least one representative real company workflow succeeds with its actual networking, AWS access, and secret requirements.»

---

Phase 8 — Production Hardening and Controlled Migration

Goal

Use what we learned from the working system to make the decisions we intentionally deferred.

Runner strategy

Determine whether actual usage justifies:

one general runner

or something like:

runner-base
├── runner-python
├── runner-node
└── runner-infrastructure

Do not create multiple images just because we can.

Scaling

Determine from measurements:

- Minimum runners
- Maximum runners
- Expected concurrency
- CPU/memory requirements
- Node capacity
- Startup performance
- Cost

Security

Review:

- GitHub authentication
- Terraform Cloud/AWS authentication
- Vault integration
- AWS workload identity
- Least privilege
- Secret rotation/expiration
- Runner isolation
- Kubernetes permissions
- Network access
- Image security

Operations

Establish:

- Monitoring
- Logging
- Alerting
- ARC upgrades
- EKS upgrades
- Runner-image updates
- Troubleshooting
- Rollback

Migration

Move workloads gradually.

smoke test
    ↓
low-risk workflow
    ↓
representative workflow
    ↓
small production rollout
    ↓
broader adoption

Done when

«The platform can safely support the intended production workloads and the team has a reasonable operating model for maintaining it.»

---

How Secrets Fit Without Becoming Their Own Project

Secrets are important throughout the project, but they do not need a separate giant phase.

There are three distinct moments:

Phase 2
Deployment secrets
GitHub → Harness → Terraform Cloud → AWS

Phase 4
Platform secret
ARC → GitHub

Phase 7
Workload secrets
Runner → AWS/internal systems/etc.

Phase 8 then hardens all three.

That is enough structure to make sure secrets are never forgotten without turning “Vault integration” into a parallel project.

---

The Eight Checkpoints

If the detailed plan ever feels overwhelming, come back to these:

1. Foundation understood
   We know the network, company processes, and ownership.

2. Deployment pipeline works
   GitHub → Harness → Terraform Cloud → AWS is usable.

3. EKS works
   Kubernetes runs a normal workload.

4. ARC works
   ARC is deployed and authenticated.

5. One runner job works
   GitHub successfully executes an ephemeral ARC job.

6. Company runner works
   Our runner image can execute the same test.

7. A real workload works
   Networking, AWS access, and workload secrets are proven.

8. Production is hardened
   Scaling, security, operations, and migration are addressed.

---

Immediate Focus

Right now, I would concentrate only on:

1. Confirm Cloud/network inputs

2. Understand the existing company implementation of
   GitHub → Harness → Terraform Cloud → AWS

3. Identify the credentials/Vault pieces that pipeline requires

4. Establish the minimal deployment path for this repository

5. Finish the EKS Terraform design

6. Deploy EKS through the real pipeline

7. Validate EKS

STOP

Then begin ARC.

Everything after that can remain planned but does not need to be solved yet.