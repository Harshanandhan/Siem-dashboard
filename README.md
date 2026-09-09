# SIEM Detection Lab

Detection rules on **generated** auth, Apache, and iptables logs.

This is **not** a live Elasticsearch cluster. Docker is not installed on the machine that produced the results below, so there is no Kibana screenshot. The proof is `python generate_logs.py` then `python detect.py`, plus a **local Python dashboard** over the same `results/alerts.json`.

Author: **Harsha Nandhan Reddy Gajulapalli**  
Email: **harshanandhanreddy820@gmail.com**

![How this detection lab works](images/architecture.png)

## Rules

| ID | MITRE | Logic |
|---|---|---|
| `brute_force_ssh` | T1110.001 | >= 30 failed SSH passwords from one IP in 60 seconds |
| `sql_injection` | T1190 | >= 5 HTTP paths containing SQL tokens (`union`, `select`, `drop`, ...) |
| `port_scan` | T1046 | >= 10 unique destination ports from one IP in 60 seconds |

Successful SSH from `10.0.0.20` is in the same `auth.log` and **does not** fire the brute-force rule.

## Run

```bash
python generate_logs.py
python detect.py
python render_images.py
```

Stdlib only for generate/detect. Pillow is only for the PNGs.

## Dashboard

Local SOC-style web UI over **real** alerts from `detect.py` — not fake Kibana, not Elasticsearch, Docker not required.

```bash
python dashboard.py
```

Then open **http://127.0.0.1:8080/**

- Severity cards (critical / high / medium) and alert table (rule, MITRE, src_ip, key metrics)
- Log counts from the same JSON report
- Buttons: **Regenerate logs**, **Run detection**, **Refresh**
- Optional live poll of `GET /api/alerts` every 5 seconds
- Banner: *Local Python detection dashboard. Not Elasticsearch/Kibana. Docker not required.*

APIs (stdlib `http.server` only):

| Method | Path | Action |
|---|---|---|
| GET | `/api/alerts` | Read `results/alerts.json` (runs detect if missing) |
| POST | `/api/generate` | Run `generate_logs.py` |
| POST | `/api/detect` | Run `detect.py` |
| GET | `/` | Static dashboard |

## Evidence

**Re-run (2026-09-09, America/New_York)** on Windows PowerShell from this repo root:

```powershell
python generate_logs.py; python detect.py
```

Stdout / `results/alerts.json` from that run:

| Metric | Value |
|---|---:|
| Alert count | **3** |
| `brute_force_ssh` (T1110.001) | critical — 50 failures, peak **31** in 60s (threshold 30) |
| `sql_injection` (T1190) | high — **14** paths with SQL tokens |
| `port_scan` (T1046) | medium — **14** unique dest ports in 60s |
| Logs | ssh_fail=50, ssh_ok=2, http=101, fw=14 |

Attacker IP in the generated data: `203.0.113.45` (TEST-NET-3, RFC 5737 — not a real host).

Claims proven by this pipeline only: the three rule IDs above, the counts in the table, and the local dashboard reading the same JSON. **Not proven / not claimed:** live Elastic stack, Kibana UI, Logstash ingestion, production SOC deployment, or Scanner AI / BuggerHunt (separate apps).

## Results

From a local run (seed 42). Same numbers as the Evidence re-run above when seed and scripts are unchanged.

| Log file | Lines |
|---|---:|
| `auth.log` failed SSH | 50 |
| `auth.log` accepted SSH | 2 |
| `access.log` HTTP | 101 |
| `firewall.log` SYN | 14 |

![Three alerts from that run](images/results-alerts.png)

| Severity | Rule | What matched |
|---|---|---|
| critical | brute_force_ssh | 50 failures, **peak 31 in 60s** (threshold 30) |
| high | sql_injection | **14** paths with SQL tokens |
| medium | port_scan | **14** unique dest ports in 60s |

JSON: `results/alerts.json`

Seven of the generated "SQLi" URLs were `' OR '1'='1'` with **no** SQL keyword. This rule correctly ignored them.

## Layout

```
generate_logs.py     writes results/logs/
detect.py            reads logs + rules/, writes alerts.json
dashboard.py         stdlib http.server — local SOC UI + APIs
dashboard/           index.html + static CSS/JS
rules/               three JSON rules
results/logs/        auth.log, access.log, firewall.log
results/alerts.json  this run
images/              diagrams from that JSON
```

## License

MIT. Copyright (c) 2026 Harsha Nandhan Reddy Gajulapalli.
