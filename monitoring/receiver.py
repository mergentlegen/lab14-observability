# A stand-in for Slack/Telegram/PagerDuty: prints every notification from Alertmanager
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Hook(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        for a in body["alerts"]:
            print(f'[{a["status"].upper()}] {a["labels"]["alertname"]} '
                  f'severity={a["labels"].get("severity")} :: {a["annotations"].get("summary")}',
                  flush=True)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass

HTTPServer(("0.0.0.0", 8080), Hook).serve_forever()
