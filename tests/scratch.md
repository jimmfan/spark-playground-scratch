# ARC Repository Structure — Proposed Design

## Recommended repository structure

```text
repo/
├── terraform/
│   │
│   ├── modules/
│   │   └── eks-cluster/
│   │       ├── main.tf                 # Common EKS implementation using terraform-aws-modules/eks/aws
│   │       ├── variables.tf            # Small project-facing EKS interface
│   │       ├── outputs.tf              # EKS outputs needed by consumers/CI/CD
│   │       ├── versions.tf             # Terraform and AWS provider requirements
│   │       └── tests/
│   │           └── eks-cluster.tftest.hcl
│   │                                       # Native Terraform tests; add as useful
│   │
│   └── eks/
│       ├── dev/
│       │   ├── backend.tf              # Dev Terraform state/backend configuration
│       │   ├── main.tf                 # Thin call to ../../modules/eks-cluster
│       │   ├── variables.tf            # Inputs specific to the dev root
│       │   ├── providers.tf            # Dev AWS provider/account/region configuration
│       │   └── versions.tf             # Root Terraform/provider constraints
│       │
│       └── prod/
│           ├── backend.tf              # Prod Terraform state/backend configuration
│           ├── main.tf                 # Thin call to ../../modules/eks-cluster
│           ├── variables.tf            # Inputs specific to the prod root
│           ├── providers.tf            # Prod AWS provider/account/region configuration
│           └── versions.tf             # Root Terraform/provider constraints
│
├── arc/
│   ├── dev/
│   │   ├── controller.values.yaml      # Dev ARC controller Helm values
│   │   └── runner-set.values.yaml      # Dev runner scale-set Helm values
│   │
│   └── prod/
│       ├── controller.values.yaml      # Prod ARC controller Helm values
│       └── runner-set.values.yaml      # Prod runner scale-set Helm values
│
├── .github/
│   └── workflows/                      # Repo CI/tests/smoke workflows as needed
│
├── .gitignore
└── README.md                            # Quick start, architecture summary, directory map
```

Files or directories should not be created merely to make the tree look complete. For example, `tests/` can be added when there is a useful Terraform test, and `.github/workflows/` should contain only workflows this repository actually needs.

---

## Directory map

| Directory                        | Purpose                                                   |
| -------------------------------- | --------------------------------------------------------- |
| `terraform/`                     | Everything in the repository managed by Terraform         |
| `terraform/modules/eks-cluster/` | Shared, opinionated EKS configuration for this project    |
| `terraform/eks/`                 | Deployable EKS Terraform roots                            |
| `terraform/eks/dev/`             | Dev EKS root module and Terraform state boundary          |
| `terraform/eks/prod/`            | Prod EKS root module and Terraform state boundary         |
| `arc/`                           | GitHub Actions Runner Controller deployment configuration |
| `arc/dev/`                       | ARC configuration deployed to the dev EKS cluster         |
| `arc/prod/`                      | ARC configuration deployed to the prod EKS cluster        |
| `.github/`                       | Repository-level GitHub configuration and workflows       |
| `README.md`                      | Quick start and concise explanation of the repository     |

The important distinction is:

```text
terraform/eks/dev     = one Terraform deployment/state
terraform/eks/prod    = another Terraform deployment/state

arc/dev               = dev ARC deployment
arc/prod              = prod ARC deployment
```

The repository is therefore a source-code boundary, **not a single deployment boundary**.

---

# Terraform design

## `terraform/modules/eks-cluster/`

This is the shared EKS composition layer.

It should **not implement EKS from raw AWS resources**.

Instead, it should use the established upstream module:

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "<approved-pinned-version>"

  # Common EKS configuration
}
```

The purpose of our module is to capture the EKS configuration that should be consistent between dev and prod.

Conceptually:

```text
dev root ──┐
           │
           ▼
      eks-cluster
           │
           ▼
terraform-aws-modules/eks/aws
           │
           ▼
          AWS
           ▲
           │
prod root ─┘
```

### `main.tf`

Contains the call to `terraform-aws-modules/eks/aws` and common EKS behavior.

Likely examples include:

* private EKS API endpoint
* control-plane logging
* required EKS add-ons
* managed node-group configuration/defaults
* access configuration
* common tags
* security defaults
* other EKS requirements that dev and prod should share

Illustrative shape:

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "<approved-pinned-version>"

  name               = var.cluster_name
  kubernetes_version = var.kubernetes_version

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  endpoint_private_access = true
  endpoint_public_access  = false

  enabled_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler",
  ]

  addons = {
    coredns            = {}
    kube-proxy         = {}
    vpc-cni            = {}
    aws-ebs-csi-driver = {}
  }

  eks_managed_node_groups = var.managed_node_groups

  tags = var.tags
}
```

This is only the intended shape. The actual options should be chosen from real project requirements rather than copied blindly from the future EKS-module story.

### `variables.tf`

Defines the **small contract this ARC platform needs**, rather than exposing every upstream EKS-module variable.

Likely inputs:

```text
cluster_name
kubernetes_version
vpc_id
subnet_ids
managed_node_groups
access_entries
tags
```

The goal is:

```text
GOOD

project requirement
      ↓
local module input
      ↓
upstream implementation
```

not:

```text
AVOID

150 upstream inputs
      ↓
150 identical local variables
      ↓
150 pass-through assignments
```

If the local module becomes only a pass-through wrapper, it should be reconsidered.

### `outputs.tf`

Expose only information useful outside the module.

Likely examples:

```text
cluster_name
cluster_arn
cluster_endpoint
cluster_security_group_id
oidc/provider information if required
```

Do not mirror every output from the upstream EKS module.

### `versions.tf`

Defines the module's Terraform/provider requirements.

For example:

```hcl
terraform {
  required_version = ">= <approved-version>"

  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}
```

The actual versions should follow company standards.

### `tests/`

Use Terraform's native test framework for useful module behavior.

Early tests should focus on meaningful requirements rather than maximizing coverage, for example:

* public EKS endpoint is disabled
* required logging is enabled
* required add-ons are configured
* expected node groups are created/configured
* required inputs are validated

This directory can wait until the first meaningful tests exist.

---

# Environment roots

## `terraform/eks/dev/`

This is a **Terraform root module**, deployment boundary, and state boundary for dev.

It should remain deliberately thin.

### `main.tf`

Calls the shared module:

```hcl
module "eks_cluster" {
  source = "../../modules/eks-cluster"

  cluster_name       = var.cluster_name
  kubernetes_version = var.kubernetes_version

  vpc_id     = var.vpc_id
  subnet_ids = var.subnet_ids

  managed_node_groups = var.managed_node_groups

  tags = {
    Environment = "dev"
    Application = "arc"
  }
}
```

The full EKS implementation should **not** be duplicated here.

### `backend.tf`

Defines or participates in configuring the dev Terraform backend/state.

Dev and prod should have independent state.

Exactly how backend configuration is supplied should follow the company's CI/CD/Terraform platform. Do not place credentials or secrets here.

### `providers.tf`

Contains the AWS provider configuration necessary for the dev account/environment.

Potential responsibilities include:

* region
* role assumption
* default tags
* provider aliases if actually required

### `variables.tf`

Contains only inputs the **dev root** needs.

These may include values supplied by CI/CD or existing infrastructure, such as:

```text
cluster_name
vpc_id
subnet_ids
AWS region
environment-specific node sizing
```

Do not introduce `.tfvars`, `.auto.tfvars`, or custom configuration layers until the CI/CD input mechanism is understood.

### `versions.tf`

Defines the root Terraform/provider requirements.

This may look very similar to prod.

That small amount of duplication is intentional: dev and prod are independent deployable roots, and keeping their provider/state configuration obvious is more valuable than eliminating every repeated line.

---

## `terraform/eks/prod/`

Has the same role as dev, but for production.

```text
terraform/eks/dev   → dev account/state
terraform/eks/prod  → prod account/state
```

The two roots should call the same `eks-cluster` module.

Differences should mostly be **inputs**, not separate EKS implementations.

Examples:

```text
cluster name
AWS account/role
subnet IDs
capacity
instance types
scaling limits
environment tags
```

The target is:

```text
same architecture
+ different environment inputs
```

rather than:

```text
dev Terraform implementation
vs.
separately maintained prod Terraform implementation
```

---

# Why some dev/prod duplication is intentional

The goal is not absolute DRYness.

We want to remove duplication of **infrastructure behavior** while retaining explicit **deployment boundaries**.

### Share

```text
EKS implementation
security defaults
logging configuration
required add-ons
common node behavior
common tags/policy
upstream EKS-module version
```

These belong in:

```text
terraform/modules/eks-cluster/
```

### Keep separate

```text
Terraform state
backend configuration
AWS account/role
environment-specific values
deployment/approval lifecycle
production capacity
```

These belong in:

```text
terraform/eks/dev/
terraform/eks/prod/
```

A few repeated lines in the root modules are preferable to adding another orchestration technology solely for DRYness.

No Terragrunt/Atmos/etc. should be introduced unless the number of accounts, regions, environments, or Terraform units eventually creates a real orchestration problem.

---

# ARC design

ARC deliberately lives outside `terraform/`.

```text
terraform/
    ↓
creates EKS

arc/
    ↓
deploys software onto EKS
```

This matches the different lifecycles.

## `arc/dev/controller.values.yaml`

Contains values for the ARC controller running in the dev cluster.

Examples could eventually include:

```text
resource requests/limits
controller settings
pod scheduling requirements
service-account configuration
company-required labels/annotations
```

Only settings that differ from chart defaults or that should be explicitly controlled should be added.

## `arc/dev/runner-set.values.yaml`

Contains configuration for the dev GitHub Actions runner scale set.

Likely examples:

```text
GitHub organization/repository target
runner scale-set name
min/max runners
runner container image
resource requests/limits
node selectors
tolerations
volume configuration
runner pod template
```

Prod gets equivalent files under:

```text
arc/prod/
```

Do not introduce `base/`, overlays, templates, or custom Helm charts just to eliminate a small amount of YAML duplication. Refactor common ARC configuration only if actual duplication becomes painful.

---

# Deployment boundaries

The initial dev environment has two primary deployment steps.

```text
1. EKS infrastructure

terraform/eks/dev
      ↓
terraform plan
      ↓
approval
      ↓
terraform apply
      ↓
EKS ready


2. ARC

arc/dev
   ↓
deploy ARC controller
   ↓
wait for readiness
   ↓
deploy runner scale set
   ↓
validate runner
```

These may be two pipelines or two ordered stages in the company's CI/CD platform.

They **do not need separate repositories**.

A normal EKS deployment should converge in **one Terraform apply**. The design should not depend on repeatedly applying Terraform, waiting manually, and applying again.

Day-to-day, the two deployments can also operate independently:

```text
Terraform change
      ↓
EKS deployment only
```

or:

```text
ARC values change
      ↓
ARC deployment only
```

---

# README repository map

The top-level README should include a small table like this:

| Directory                        | Purpose                                                                                        |
| -------------------------------- | ---------------------------------------------------------------------------------------------- |
| `terraform/`                     | Infrastructure managed by Terraform                                                            |
| `terraform/modules/eks-cluster/` | Shared EKS configuration and project policy, implemented using `terraform-aws-modules/eks/aws` |
| `terraform/eks/`                 | EKS Terraform deployment roots                                                                 |
| `terraform/eks/dev/`             | Dev EKS root module and state boundary                                                         |
| `terraform/eks/prod/`            | Prod EKS root module and state boundary                                                        |
| `arc/`                           | Actions Runner Controller deployment configuration                                             |
| `arc/dev/`                       | ARC configuration for the dev EKS cluster                                                      |
| `arc/prod/`                      | ARC configuration for the prod EKS cluster                                                     |
| `.github/`                       | Repository CI, validation, and GitHub workflow configuration                                   |

---

# Future company EKS module

The local `eks-cluster` module also gives us a useful place to discover requirements for the future company-owned EKS module.

Initially:

```text
ARC repo
   ↓
terraform/modules/eks-cluster
   ↓
terraform-aws-modules/eks/aws
```

While implementing dev, separate discoveries into:

```text
ARC-specific requirement
        ↓
remains with ARC project

company-wide EKS standard
        ↓
candidate for company EKS module
```

Later, the company module could become:

```text
company/eks/aws
      ↓
company policy + supported interface
      ↓
terraform-aws-modules/eks/aws
```

The ARC project could then either:

```text
eks-cluster
    ↓
company/eks/aws
```

if the local wrapper still adds ARC-specific value, or call the company module directly if the local wrapper no longer serves a useful purpose.

The transition should be treated as an explicit Terraform migration: prove it in dev first and ensure the plan does **not unintentionally recreate the EKS cluster** before applying the same migration to prod.

---

# Current design principles

* One repository is sufficient.
* `terraform/` and `arc/` represent separate deployment lifecycles.
* Dev and prod have independent Terraform state.
* Dev should be a rehearsal for prod.
* Use `terraform-aws-modules/eks/aws` rather than rebuilding EKS ourselves.
* Keep a small local `eks-cluster` composition module because it removes meaningful dev/prod duplication and captures project policy.
* Do not mirror the entire upstream EKS-module API.
* Pin upstream module versions and upgrade deliberately.
* Keep Terraform roots thin.
* Accept a small amount of duplication where it makes environment/state boundaries clearer.
* Do not introduce Terragrunt or other orchestration until scale demonstrates a need.
* Do not split ARC into another repository merely because it has a separate deployment.
* Do not add speculative directories or abstraction layers before something actually needs them.
* Use the dev implementation to discover requirements for the future company-owned EKS module.
