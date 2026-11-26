# Runbook: HighLatencyP95

**Alert:** the p95 latency of `lab14-app` (`job:http_request_duration_seconds:p95_1m`) is above 0.5 s for 1 minute. **Severity:** ticket (work hours, not a page).

## What it means
5 % of the requests are slower than 0.5 s. The average can look fine while these users wait: look at the tail, not the mean.

## Impact
Slow pages, timeouts in clients. Not an outage yet.

## What to check, in this order
1. How slow and since when? Dashboard "Duration - p50 / p95" and the panel "p95 by route".
2. Which route? `histogram_quantile(0.95, sum by (route, le) (rate(http_request_duration_seconds_bucket{job="lab14-app"}[1m])))`
3. Is it every request or some? In Loki:
   `{service="lab14-app"} | json | duration_ms > 500 | line_format "{{.duration_ms}}ms {{.path}} {{.request_id}}"`
4. Does the p95 from the logs match the one from the metrics?
   `quantile_over_time(0.95, {service="lab14-app"} | json | path="/api/orders" | unwrap duration_ms [1m]) by (path)`
5. Was something changed? In the lab: `POST /chaos?slow_ms=...` shows as the log line `chaos changed`.

## How to fix
- Injected delay or slow dependency: remove the cause (`curl -s -X POST "localhost:8000/chaos?slow_ms=0"`), or scale out / fix the query.
- Wait for `[RESOLVED] HighLatencyP95`.

## Escalate
If the p95 is still above 0.5 s after the fix: the service owner (course student); open a ticket for a capacity or query review.
