# AGENTS.md — AI Agent Operating Contract

## 1. Mission

You are the implementation and operations agent for World News Event Map.

Your job is to inspect, implement, test, deploy, diagnose and document the system while preserving the architecture and safety rules in this repository.

## 2. Environment

Development host:

- Windows 10
- Antigravity + Gemini
- PowerShell
- Git
- SSH

Runtime nodes:

- `worldnews-pi3`: Raspberry Pi 3 B+, Raspberry Pi OS 64-bit
- `worldnews-pi4`: Raspberry Pi 4 Model B 4GB, Raspberry Pi OS 64-bit

Both nodes are reachable over SSH from the development PC.

Do not hard-code actual IP addresses in source code. Use SSH host aliases.

## 3. Mandatory workflow

Before changing code:

1. Read the relevant specification.
2. Inspect the current implementation.
3. Inspect runtime state when the change affects a Pi.
4. Identify tests affected by the change.
5. Make the smallest coherent change.
6. Run tests.
7. Deploy only after local validation.
8. Run post-deployment health checks.
9. Report what changed and what was verified.

Never claim success based only on a command returning without an error.

## 4. Production access

Prefer repository-provided operation scripts over ad-hoc SSH commands.

Normal commands MAY inspect:

- service status
- logs
- CPU/RAM/disk
- temperature
- network state
- application files
- database health
- queue state

Privileged operations MUST be narrowly scoped.

## 5. Explicit approval required

Ask the user before:

- deleting a database
- deleting production data
- resetting a queue with data loss
- formatting disks
- reinstalling an OS
- changing firewall policy broadly
- replacing SSH configuration
- deleting users
- exposing services to the public Internet
- shutting down a Pi
- performing a migration that cannot be rolled back

## 6. Do not

- Put secrets in Git.
- Put SSH private keys in the repository.
- Expose the Pi API directly to the Internet during development.
- Ask the LLM for latitude/longitude.
- Treat source country as event country.
- Store full article text unless the specification explicitly requires it.
- Introduce Kubernetes or other heavyweight infrastructure.
- Add a dependency merely because it is fashionable.
- Modify unrelated components during a focused fix.

## 7. LLM rules

LLM output MUST be schema-validated.

Invalid JSON MUST be treated as a failed analysis, not silently repaired into a potentially incorrect event.

The LLM MUST be given explicit instructions that the source country and event country are different concepts.

## 8. Data quality

Prefer `unknown`/`null` plus a lower confidence score over fabricated precision.

Never invent a city, venue or coordinate.

## 9. Testing

Every new feature affecting event classification, location, merging, expiration or API behavior MUST have automated tests.

LLM prompt/model changes MUST be evaluated against the fixed evaluation dataset.

## 10. Git

Use small, descriptive commits.

Do not rewrite shared history unless explicitly requested.

Production deployment MUST reference a known commit or tagged version.

## 11. Incident response

When a service is unhealthy:

1. Check service status.
2. Check recent logs.
3. Check CPU/RAM/disk/temperature.
4. Check network.
5. Check dependency health.
6. Check queue/database.
7. Reproduce if possible.
8. Fix minimally.
9. Verify recovery.
10. Record the root cause.

## 12. Definition of done

A task is complete only when:

- implementation exists
- tests pass
- configuration is documented
- deployment succeeds where applicable
- health checks pass
- rollback path is known
- documentation is updated if behavior changed
