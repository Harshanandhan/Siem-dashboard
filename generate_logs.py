#!/usr/bin/env python3
"""Write mixed auth / web / firewall logs for the detector to read.

Author: Harsha Nandhan Reddy Gajulapalli
Email: harshanandhanreddy820@gmail.com
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

AUTHOR = "Harsha Nandhan Reddy Gajulapalli"
BASE = datetime(2026, 8, 20, 21, 0, 0)
ATTACKER = "203.0.113.45"
USERS = ["root", "admin", "ubuntu", "oracle"]
SQL = [
    "/login.php?user=' OR '1'='1' --",
    "/search.php?q=1' UNION SELECT * FROM users--",
    "/item.php?id=1; DROP TABLE accounts--",
]
HERE = Path(__file__).resolve().parent


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def auth_logs(rng: random.Random) -> list[str]:
    lines = []
    # 50 failed SSH from one IP, 2 seconds apart (covers a 60s / 30-fail rule)
    for i in range(50):
        ts = BASE + timedelta(seconds=i * 2)
        user = rng.choice(USERS)
        pid = 12000 + i
        port = 41000 + i
        lines.append(
            f"{ts.strftime('%b %d %H:%M:%S')} prod-web sshd[{pid}]: "
            f"Failed password for {user} from {ATTACKER} port {port} ssh2"
        )
    # a few successes from the internal net — should not alert
    for i, user in enumerate(["alice", "bob"]):
        ts = BASE + timedelta(minutes=10 + i)
        lines.append(
            f"{ts.strftime('%b %d %H:%M:%S')} prod-web sshd[{20000+i}]: "
            f"Accepted password for {user} from 10.0.0.20 port 51000 ssh2"
        )
    return lines


def access_logs(rng: random.Random) -> list[str]:
    lines = []
    for i, path in enumerate(SQL * 7):  # 21 injection GETs
        ts = BASE + timedelta(seconds=30 + i * 3)
        lines.append(
            f'{ATTACKER} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
            f'"GET {path} HTTP/1.1" 403 512 "-" "sqlmap/1.7"'
        )
    for i in range(80):
        ts = BASE + timedelta(minutes=rng.randint(0, 40))
        path = rng.choice(["/", "/index.html", "/about", "/api/health"])
        status = rng.choice([200, 200, 200, 304])
        ip = rng.choice(["10.0.0.10", "10.0.0.20", "192.168.1.100"])
        lines.append(
            f'{ip} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
            f'"GET {path} HTTP/1.1" {status} {rng.randint(200, 4000)} '
            f'"-" "Mozilla/5.0"'
        )
    return lines


def firewall_logs(rng: random.Random) -> list[str]:
    lines = []
    ports = [22, 23, 25, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443, 5900]
    for i, port in enumerate(ports):
        ts = BASE + timedelta(seconds=i * 2)
        lines.append(
            f"{ts.strftime('%b %d %H:%M:%S')} edge kernel: iptables: "
            f"IN=eth0 SRC={ATTACKER} DST=192.168.1.50 PROTO=TCP "
            f"SPT={50000+i} DPT={port} SYN"
        )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(HERE / "results" / "logs"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    out = Path(args.out)
    auth = auth_logs(rng)
    access = access_logs(rng)
    fw = firewall_logs(rng)
    write(out / "auth.log", auth)
    write(out / "access.log", access)
    write(out / "firewall.log", fw)
    print(f"{AUTHOR}")
    print(f"Wrote {len(auth)} auth, {len(access)} access, {len(fw)} firewall lines -> {out}")


if __name__ == "__main__":
    main()
