# Operations Manual

## Daily operations

- Check backend readiness and frontend availability.
- Review Prometheus alerts and Grafana dashboards.
- Confirm backup jobs completed successfully.
- Validate log ingestion into Loki and trace sampling in Tempo.

## Incident response

- Freeze deploys during service instability.
- Roll back the Helm release if error rate or latency spikes persist.
- Restore from backups if data corruption is confirmed.

## Maintenance

- Rotate secrets on the published schedule.
- Apply dependency and container updates weekly.
- Re-run smoke and soak tests after significant platform changes.
