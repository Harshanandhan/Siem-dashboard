#!/usr/bin/env python3
"""Local SOC-style dashboard over real Python detections (stdlib only).

Serves dashboard/index.html and JSON APIs that read results/alerts.json
and can shell out to generate_logs.py / detect.py.

Author: Harsha Nandhan Reddy Gajulapalli
Email: harshanandhanreddy820@gmail.com
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

AUTHOR = "Harsha Nandhan Reddy Gajulapalli"
EMAIL = "harshanandhanreddy820@gmail.com"
HERE = Path(__file__).resolve().parent
ALERTS = HERE / "results" / "alerts.json"
DASH_DIR = HERE / "dashboard"
HOST = "127.0.0.1"
PORT = 8080

_run_lock = threading.Lock()


def _run_script(name: str) -> dict:
    """Run generate_logs.py or detect.py; return stdout/stderr/returncode."""
    script = HERE / name
    if not script.is_file():
        return {"ok": False, "error": f"missing {name}", "returncode": -1}
    with _run_lock:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(HERE),
            capture_output=True,
            text=True,
            timeout=120,
        )
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
    }


def _load_alerts(*, run_detect_if_missing: bool = True) -> dict:
    if not ALERTS.is_file() and run_detect_if_missing:
        logs = HERE / "results" / "logs"
        if not (logs / "auth.log").is_file():
            _run_script("generate_logs.py")
        _run_script("detect.py")
    if not ALERTS.is_file():
        return {
            "author": AUTHOR,
            "email": EMAIL,
            "method": "python rules on generated syslog/apache/iptables lines",
            "note": (
                "Local Python detection dashboard. Not Elasticsearch/Kibana. "
                "Docker not required. alerts.json missing — run Generate + Detect."
            ),
            "log_counts": {},
            "alert_count": 0,
            "alerts": [],
            "missing": True,
        }
    data = json.loads(ALERTS.read_text(encoding="utf-8"))
    data["missing"] = False
    data.setdefault(
        "dashboard_note",
        "Local Python detection dashboard. Not Elasticsearch/Kibana. Docker not required.",
    )
    return data


def _json_bytes(obj: dict, status: int = 200) -> tuple[int, bytes, str]:
    body = json.dumps(obj, indent=2).encode("utf-8")
    return status, body, "application/json; charset=utf-8"


def _read_static(rel: str) -> tuple[int, bytes, str] | None:
    # Map URL path under / to files in dashboard/
    # / -> index.html; /static/... -> dashboard/static/...
    if rel in ("", "/"):
        path = DASH_DIR / "index.html"
        ctype = "text/html; charset=utf-8"
    elif rel.startswith("/static/"):
        path = DASH_DIR / rel.lstrip("/")
        if path.suffix == ".css":
            ctype = "text/css; charset=utf-8"
        elif path.suffix == ".js":
            ctype = "application/javascript; charset=utf-8"
        elif path.suffix == ".png":
            ctype = "image/png"
        else:
            ctype = "application/octet-stream"
    else:
        return None
    path = path.resolve()
    try:
        path.relative_to(DASH_DIR.resolve())
    except ValueError:
        return 403, b"forbidden", "text/plain; charset=utf-8"
    if not path.is_file():
        return 404, b"not found", "text/plain; charset=utf-8"
    return 200, path.read_bytes(), ctype


class Handler(BaseHTTPRequestHandler):
    server_version = "SIEMDashboard/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/alerts":
            status, body, ctype = _json_bytes(_load_alerts())
            self._send(status, body, ctype)
            return
        if path == "/api/health":
            status, body, ctype = _json_bytes(
                {
                    "ok": True,
                    "author": AUTHOR,
                    "dashboard": "local-python",
                    "not": "elasticsearch/kibana",
                }
            )
            self._send(status, body, ctype)
            return
        result = _read_static(path)
        if result is None:
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        self._send(*result)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length:
            self.rfile.read(length)
        if path == "/api/generate":
            result = _run_script("generate_logs.py")
            status, body, ctype = _json_bytes(
                {**result, "action": "generate_logs"},
                200 if result["ok"] else 500,
            )
            self._send(status, body, ctype)
            return
        if path == "/api/detect":
            result = _run_script("detect.py")
            payload = {**result, "action": "detect"}
            if result["ok"]:
                payload["alerts"] = _load_alerts(run_detect_if_missing=False)
            status, body, ctype = _json_bytes(
                payload, 200 if result["ok"] else 500
            )
            self._send(status, body, ctype)
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")


def main() -> None:
    DASH_DIR.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"{AUTHOR}")
    print("Local Python detection dashboard. Not Elasticsearch/Kibana. Docker not required.")
    print(f"Open http://{HOST}:{PORT}/")
    print("APIs: GET /api/alerts  POST /api/generate  POST /api/detect")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.shutdown()


if __name__ == "__main__":
    main()
