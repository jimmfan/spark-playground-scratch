Investigate how Git authentication works in this Coder workspace/project.

Please determine:

1. Whether Git auth is using HTTPS tokens, SSH keys, GIT_ASKPASS, a Git credential helper, Coder’s Git auth integration, VS Code auth, or something else.
2. Whether credentials are user-scoped or shared/service-account based.
3. Whether the token/key appears short-lived or long-lived.
4. Whether GitHub RBAC is enforced based on the individual user’s GitHub identity.
5. Where the authentication is configured: startup script, image/AMI, devcontainer, Coder template, Terraform, Kubernetes Secret, environment variable, or Git config.
6. Whether any secrets/tokens are exposed in logs, shell history, files, environment variables, or Git config.
7. Whether this is a safe enterprise pattern or if there are risks.

Please inspect relevant files and commands, but do not print secrets. Redact any tokens or credentials. Summarize the flow as:

User login → Coder → workspace → Git credential mechanism → GitHub

Inside the workspace, ask it to run/check:

git remote -v
git config --show-origin --list | grep -Ei 'credential|askpass|insteadOf|url'
env | grep -Ei 'GIT|GITHUB|ASKPASS|CODER|TOKEN' | sed -E 's/(TOKEN|PASSWORD|SECRET|KEY)=.*/\1=<redacted>/'
ls -la ~/.git-credentials ~/.config/git ~/.ssh 2>/dev/null
ps aux | grep -Ei 'askpass|git|coder' | grep -v grep

Then outside the workspace, in the Coder/EKS/template repo, use:

Now investigate the platform configuration that creates this Git authentication behavior.

Search the Coder templates, startup scripts, Terraform, Helm values, Kubernetes manifests, AMI/user-data scripts, and devcontainer files for Git auth configuration.

Look for:

- GIT_ASKPASS
- credential.helper
- github
- gitAuth
- coder_external_auth
- external_auth
- OAuth
- token
- SSH key mounting
- Kubernetes Secrets
- environment variables passed into workspaces

Do not print secrets. Redact sensitive values. Explain exactly which files configure Git authentication and whether the design is user-scoped and safe. 