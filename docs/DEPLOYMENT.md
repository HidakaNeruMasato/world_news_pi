# DEPLOYMENT.md

## 1. Principle

Git is the source of truth.

Production nodes receive known versions from the repository.

## 2. Windows deployment tools

PowerShell scripts under `scripts/` SHOULD be the normal entry point.

Example:

`.\scripts\ops.ps1 status`

`.\scripts\ops.ps1 deploy-pi3`

`.\scripts\ops.ps1 deploy-pi4`

## 3. SSH aliases

Expected aliases:

- worldnews-pi3
- worldnews-pi4

Actual host addresses are maintained in the user's SSH configuration, not committed here.

## 4. Pi3 deployment

Deploy:

- collector source
- configuration template
- systemd unit
- Python environment/dependencies

Then:

- syntax/test check
- restart service
- health check

## 5. Pi4 deployment

Deploy:

- analyzer
- API
- configuration
- systemd units

The LLM model file is managed separately and is not copied on every code deployment.

## 6. Versioning

Deployment SHOULD record:

- Git commit
- deployment time
- target node
- service version

## 7. Rollback

Keep the previous known-good release.

Rollback MUST be possible by selecting a previous commit/release.

## 8. Secrets

Secrets remain outside Git.

Use environment files or OS-level secret storage with appropriate permissions.
