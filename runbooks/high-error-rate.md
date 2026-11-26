# Runbook: HighErrorRate

**Alert:** the 5xx ratio of `lab14-app` is above 2 % for 1 minute, with more than 0.5 req/s of traffic. **Severity:** page.

## What it means
More than 2 % of the requests to the app end with `5xx` (in the lab: `503 database timeout` on `/api/orders`).

## Impact
Users get errors instead of orders. The error budget is being spent.

## What to check, in this order
1. Is it real traffic? `job:http_requests:rate1m` (the alert only fires above 0.5 req/s).
2. How big is it, and since when? `job:http_errors:ratio_rate1m` in the **lab14 - RED** dashboard, panel "Errors - 5xx ratio".
3. Which status and route?
   `sum by (route, status) (rate(http_requests_total{job="lab14-app", status=~"5.."}[1m]))`
4. What does the app say? Grafana -> Explore -> Loki:
   `{service="lab14-app"} | json | level="ERROR"`
   `sum by (status) (count_over_time({service="lab14-app"} | json [5m]))`
5. Take one failing `request_id` from step 4 and read the whole story:
   `{service="lab14-app"} |= "<request_id>"`
6. Was there a change right before it started (a release, a config change)? In the lab: `POST /chaos?error_rate=...`
   shows as the log line `chaos changed`.

## How to fix
- Bad config or release: roll back (Compose: `curl -s -X POST "localhost:8000/chaos?error_rate=0"`, in a real service redeploy the previous image).
- Dependency (database) failing: fix or fail over the dependency, the app only reports it.
- Then wait for `[RESOLVED] HighErrorRate` in the webhook (1-2 minutes).

## Escalate
If the ratio is still above 2 % 15 minutes after the rollback: the service owner (course student), then the platform team.
