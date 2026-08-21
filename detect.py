#!/usr/bin/env python3
"""Apply the JSON rules to generated logs. No Elasticsearch required.

Author: Harsha Nandhan Reddy Gajulapalli
Email: harshanandhanreddy820@gmail.com
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

AUTHOR = "Harsha Nandhan Reddy Gajulapalli"
EMAIL = "harshanandhanreddy820@gmail.com"
HERE = Path(__file__).resolve().parent
YEAR = 2026

SSH_FAIL = re.compile(
    r"^(\w{3}\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+sshd\[\d+\]:\s+"
    r"Failed password for (\S+) from (\d+\.\d+\.\d+\.\d+)"
)
SSH_OK = re.compile(
    r"^(\w{3}\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+sshd\[\d+\]:\s+"
    r"Accepted password for (\S+) from (\d+\.\d+\.\d+\.\d+)"
)
APACHE = re.compile(
    r'^(\S+) - .* \[([^\]]+)\] "(GET|POST|HEAD|PUT|DELETE) (.+) HTTP/[\d.]+" (\d+)'
)
IPTABLES = re.compile(
    r"^(\w{3}\s+\d+\s+\d+:\d+:\d+).*SRC=(\d+\.\d+\.\d+\.\d+).*DST=(\d+\.\d+\.\d+\.\d+).*DPT=(\d+)"
)
SQL_RE = re.compile(r"(union|select|insert|update|delete|drop|alter)\b", re.I)


def parse_syslog(stamp: str) -> datetime:
    return datetime.strptime(f"{YEAR} {stamp}", "%Y %b %d %H:%M:%S")


def parse_apache_time(stamp: str) -> datetime:
    # 20/Aug/2026:21:00:30 +0000
    return datetime.strptime(stamp.split()[0], "%d/%b/%Y:%H:%M:%S")


def load_rule(name: str) -> dict:
    return json.loads((HERE / "rules" / name).read_text(encoding="utf-8"))


def brute_force(auth_path: Path, rule: dict) -> list[dict]:
    fails: dict[str, list[datetime]] = defaultdict(list)
    for line in auth_path.read_text(encoding="utf-8").splitlines():
        m = SSH_FAIL.match(line)
        if m:
            fails[m.group(3)].append(parse_syslog(m.group(1)))
    window = timedelta(seconds=rule["window_sec"])
    need = rule["threshold"]
    alerts = []
    for ip, times in fails.items():
        times.sort()
        best = 0
        j = 0
        for i, t in enumerate(times):
            while times[j] < t - window:
                j += 1
            best = max(best, i - j + 1)
        if best >= need:
            alerts.append(
                {
                    "rule": rule["id"],
                    "title": rule["name"],
                    "severity": rule["severity"],
                    "mitre": rule["mitre"],
                    "src_ip": ip,
                    "failed_ssh": len(times),
                    "peak_in_window": best,
                    "window_sec": rule["window_sec"],
                    "threshold": need,
                }
            )
    return alerts


def sql_injection(access_path: Path, rule: dict) -> list[dict]:
    hits = []
    for line in access_path.read_text(encoding="utf-8").splitlines():
        m = APACHE.match(line)
        if not m:
            continue
        ip, stamp, method, path, status = m.groups()
        if SQL_RE.search(path):
            hits.append(
                {
                    "src_ip": ip,
                    "method": method,
                    "path": path,
                    "status": int(status),
                    "time": parse_apache_time(stamp).isoformat(),
                }
            )
    if not hits:
        return []
    by_ip: dict[str, list] = defaultdict(list)
    for h in hits:
        by_ip[h["src_ip"]].append(h)
    return [
        {
            "rule": rule["id"],
            "title": rule["name"],
            "severity": rule["severity"],
            "mitre": rule["mitre"],
            "src_ip": ip,
            "requests": len(items),
            "sample_path": items[0]["path"],
        }
        for ip, items in by_ip.items()
        if len(items) >= rule.get("threshold", 1)
    ]


def port_scan(fw_path: Path, rule: dict) -> list[dict]:
    events: dict[str, list[tuple[datetime, int]]] = defaultdict(list)
    for line in fw_path.read_text(encoding="utf-8").splitlines():
        m = IPTABLES.search(line)
        if not m:
            continue
        events[m.group(2)].append((parse_syslog(m.group(1)), int(m.group(4))))
    window = timedelta(seconds=rule["window_sec"])
    need = rule["unique_ports"]
    alerts = []
    for ip, pairs in events.items():
        pairs.sort()
        peak = 0
        times = [p[0] for p in pairs]
        j = 0
        for i, (t, _port) in enumerate(pairs):
            while times[j] < t - window:
                j += 1
            uniq = {pairs[k][1] for k in range(j, i + 1)}
            peak = max(peak, len(uniq))
        if peak >= need:
            alerts.append(
                {
                    "rule": rule["id"],
                    "title": rule["name"],
                    "severity": rule["severity"],
                    "mitre": rule["mitre"],
                    "src_ip": ip,
                    "unique_ports": peak,
                    "packets": len(pairs),
                    "window_sec": rule["window_sec"],
                }
            )
    return alerts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", default=str(HERE / "results" / "logs"))
    parser.add_argument("--out", default=str(HERE / "results" / "alerts.json"))
    args = parser.parse_args()
    logs = Path(args.logs)

    alerts: list[dict] = []
    alerts += brute_force(logs / "auth.log", load_rule("brute_force_ssh.json"))
    alerts += sql_injection(logs / "access.log", load_rule("sql_injection.json"))
    alerts += port_scan(logs / "firewall.log", load_rule("port_scan.json"))

    auth_fail = sum(
        1
        for line in (logs / "auth.log").read_text(encoding="utf-8").splitlines()
        if "Failed password" in line
    )
    auth_ok = sum(
        1
        for line in (logs / "auth.log").read_text(encoding="utf-8").splitlines()
        if "Accepted password" in line
    )
    access_n = len((logs / "access.log").read_text(encoding="utf-8").splitlines())
    fw_n = len((logs / "firewall.log").read_text(encoding="utf-8").splitlines())

    report = {
        "author": AUTHOR,
        "email": EMAIL,
        "method": "python rules on generated syslog/apache/iptables lines",
        "note": "Elasticsearch/Kibana were not used. Docker is not installed on this machine.",
        "log_counts": {
            "ssh_failed": auth_fail,
            "ssh_accepted": auth_ok,
            "http": access_n,
            "firewall": fw_n,
        },
        "alert_count": len(alerts),
        "alerts": alerts,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"{AUTHOR}")
    print(f"Logs  ssh_fail={auth_fail} ssh_ok={auth_ok} http={access_n} fw={fw_n}")
    print(f"Alerts {len(alerts)}")
    for a in alerts:
        print(f"  [{a['severity']}] {a['rule']}  {a['src_ip']}  {a['mitre']}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
