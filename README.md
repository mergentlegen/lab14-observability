# lab14-observability

A small Flask app (`lab14-app`) with RED metrics and JSON logs with a `request_id`, monitored by
Prometheus (recording + alert rules), Alertmanager (-> webhook), Loki + Grafana Alloy (logs), and Grafana
(data sources and the dashboard are **provisioned**, the dashboard lives as JSON in `dashboards/`).

Track used: **B (Docker Compose)**.

```bash
echo "GRAFANA_PASSWORD=$(openssl rand -hex 12)" > .env      # .env is in .gitignore
docker compose up -d --build
docker compose ps                                           # 7 services, all Up
```

| What | URL |
|---|---|
| App | http://localhost:8000 (`/api/orders`, `/metrics`, `/healthz`, `POST /chaos`) |
| Prometheus | http://localhost:9090 |
| Alertmanager | http://localhost:9093 |
| Grafana (admin / password from `.env`) | http://localhost:3000 -> Dashboards -> lab14 -> "lab14 - RED" |
| Alloy UI | http://localhost:12345 |

Files: `app/`, `monitoring/` (Prometheus, rules, Alertmanager, Loki, Alloy, Grafana provisioning),
`dashboards/lab14.json`, `runbooks/` (one per alert).

Stop and clean: `docker compose down -v`, `docker image rm lab14-app:1.0.0`.
