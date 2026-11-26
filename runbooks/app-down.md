# Runbook: AppDown

**Alert:** `up{job="lab14-app"} == 0`, or the series does not exist at all (`absent(...)`), for 30 seconds. **Severity:** page.

## What it means
Prometheus cannot scrape the app: the container is stopped or crashed, the network is broken, or (in Kubernetes) there are no pods, so there are no targets and no `up` series.

## Impact
The whole service is unavailable. This is the one message you need: while it fires, `HighErrorRate` and `HighLatencyP95` are **inhibited** (suppressed) because they are only symptoms.

## What to check, in this order
1. Is the container running? `docker compose ps` (Compose) / `kubectl -n lab14 get pods` (Kubernetes).
2. Why did it stop? `docker compose logs --tail 50 lab14-app` / `kubectl -n lab14 logs deploy/lab14-app`.
3. What does Prometheus see? Status -> Target health: the error text of the target (connection refused, no such host).
4. Is it only the scrape that fails, not the app? `curl -s localhost:8000/healthz` should print `{"status":"ok"}`.
5. Was it stopped on purpose (maintenance)? Check the silences in Alertmanager (`localhost:9093`, "Silences").

## How to fix
- Stopped: `docker compose start lab14-app` / `kubectl -n lab14 scale deploy/lab14-app --replicas=2`.
- Crash loop: read the logs from step 2, fix the cause, restart.
- After it is back: the target is UP within 5-15 s, the alert resolves, and `[RESOLVED] AppDown` arrives in the webhook.

## Escalate
If the app is not UP 10 minutes after a restart: the service owner (course student), then the platform team.
