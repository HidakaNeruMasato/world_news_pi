# OPERATIONS.md

## 1. Standard operations

Use repository scripts whenever possible.

Commands:

- status
- health
- logs
- deploy-pi3
- deploy-pi4
- restart-pi3
- restart-pi4
- backup
- test

## 2. Service names

Pi3:

`world-news-collector.service`

Pi4:

`world-news-analyzer.service`
`world-news-api.service`
`llama-server.service`

Exact names may be changed during implementation but MUST then be documented.

## 3. Health checks

Pi3:

- service active
- last feed success
- queue size
- disk usage
- CPU temperature

Pi4:

- API response
- database health
- analyzer process
- LLM process
- pending jobs
- failed jobs
- RAM/disk/temperature

## 4. Logs

Use journald/systemd logs.

Application logs SHOULD be structured enough for automated diagnosis.

## 5. Backup

Back up SQLite database to the Windows PC or other storage.

A backup MUST NOT overwrite the only previous backup.

## 6. Recovery

After reboot:

- services start automatically
- queue resumes
- database opens
- active event expiration works
- failed jobs remain retryable

## 7. Monitoring thresholds

Thresholds are configuration, not hard-coded assumptions.

At minimum monitor:

- disk free space
- RAM
- CPU temperature
- queue backlog
- feed failure count
- LLM error rate
- API availability
