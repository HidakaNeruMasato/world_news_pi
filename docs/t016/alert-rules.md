# T016 Alert Management Rules

## 1. Severities
- **INFO**: Routine operational state changes or normal events.
- **WARNING**: Potential anomaly or threshold breach requiring attention.
- **ERROR**: Functional error or degraded processing state.
- **CRITICAL**: Threat to data integrity, safety properties, or service outage.

## 2. Deduplication & State Machine
1. **Deduplication**: Alerts sharing the same `alert_key` update `last_seen` and increment `count` rather than firing duplicate alerts.
2. **State Machine**:
   - `OPEN`: Active alert condition.
   - `RESOLVED`: Fired when a previously failing metric returns to healthy levels.

## 3. Cooldown Rules
- **WARNING Cooldown**: 6 hours
- **ERROR Cooldown**: 1 hour
- **CRITICAL Cooldown**: 15 minutes
