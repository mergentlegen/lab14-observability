import json, logging, os, random, socket, sys, time, uuid
from datetime import datetime, timezone
import flask.cli
from flask import Flask, g, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)
VERSION = os.environ.get("APP_VERSION", "dev")
# Fault injection, changeable at runtime with POST /chaos (for the practice only)
CHAOS = {"error_rate": float(os.environ.get("ERROR_RATE", "0")),
         "slow_ms": int(os.environ.get("SLOW_MS", "0"))}

# Same names and labels as campus-app in the final project
REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "route"],
                    buckets=(0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5))


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "level": record.levelname, "msg": record.getMessage()}
        data.update(getattr(record, "fields", {}))
        return json.dumps(data)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
log = logging.getLogger("lab14")
log.addHandler(handler)
log.setLevel(logging.INFO)
logging.getLogger("werkzeug").disabled = True       # we log requests ourselves
flask.cli.show_server_banner = lambda *args: None    # every line on stdout is JSON


@app.before_request
def start():
    g.start = time.perf_counter()
    g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]


@app.after_request
def observe(response):
    route = request.url_rule.rule if request.url_rule else "unmatched"
    if route == "/metrics":
        return response
    elapsed = time.perf_counter() - g.start
    REQUESTS.labels(request.method, route, str(response.status_code)).inc()
    LATENCY.labels(request.method, route).observe(elapsed)
    response.headers["X-Request-ID"] = g.request_id
    level = logging.ERROR if response.status_code >= 500 else logging.INFO
    log.log(level, "request", extra={"fields": {
        "request_id": g.request_id, "method": request.method, "path": request.path,
        "status": response.status_code, "duration_ms": round(elapsed * 1000, 1)}})
    return response


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": VERSION, "host": socket.gethostname()}


@app.get("/api/orders")
def orders():
    time.sleep(random.uniform(0.01, 0.06) + CHAOS["slow_ms"] / 1000)
    if random.random() < CHAOS["error_rate"]:
        log.error("database timeout", extra={"fields": {"request_id": g.request_id}})
        return {"error": "database timeout"}, 503
    return {"orders": [{"id": i, "total": 1000 * i} for i in range(1, 4)]}


@app.post("/chaos")
def chaos():
    CHAOS["error_rate"] = float(request.args.get("error_rate", CHAOS["error_rate"]))
    CHAOS["slow_ms"] = int(request.args.get("slow_ms", CHAOS["slow_ms"]))
    log.warning("chaos changed", extra={"fields": {"request_id": g.request_id, **CHAOS}})
    return CHAOS


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
