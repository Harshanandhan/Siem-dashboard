"""PNGs from results/alerts.json."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "images"
FONT_DIR = Path(r"C:\Windows\Fonts")
NAVY = (15, 23, 42)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
LINE = (30, 41, 59)
ACCENT = (56, 189, 248)
CRIT = (220, 38, 38)
HIGH = (234, 88, 12)
MED = (202, 138, 4)
SEV = {"critical": CRIT, "high": HIGH, "medium": MED}


def font(name: str, size: int):
    for n in (name, "segoeui.ttf", "arial.ttf"):
        p = FONT_DIR / n
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def architecture():
    w, h = 1400, 680
    im = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(im)
    title, body, small = font("segoeuib.ttf", 36), font("segoeui.ttf", 22), font("segoeui.ttf", 18)
    d.text((48, 36), "How this detection lab works", font=title, fill=WHITE)
    d.text((48, 88), "Harsha Nandhan Reddy Gajulapalli  ·  no Elasticsearch in this run", font=small, fill=MUTED)
    boxes = [
        (50, 180, 340, 400, "1. Generate", "auth.log  access.log\nfirewall.log"),
        (390, 180, 720, 400, "2. Rules", "T1110.001  T1190\nT1046"),
        (770, 180, 1100, 400, "3. Detect", "Python matcher\nthresholds + windows"),
        (1150, 180, 1350, 400, "4. Alerts", "alerts.json"),
    ]
    for x1, y1, x2, y2, head, desc in boxes:
        d.rounded_rectangle((x1, y1, x2, y2), 18, fill=LINE)
        d.text((x1 + 20, y1 + 28), head, font=body, fill=ACCENT)
        d.multiline_text((x1 + 20, y1 + 90), desc, font=small, fill=WHITE, spacing=8)
    d.text((48, 470), "Docker / ELK is not installed here, so I did not fake a Kibana screenshot.", font=small, fill=MUTED)
    d.text((48, 510), "The numbers below are from python generate_logs.py && python detect.py", font=small, fill=MUTED)
    d.text((48, 600), "harshanandhanreddy820@gmail.com", font=small, fill=MUTED)
    IMG.mkdir(exist_ok=True)
    im.save(IMG / "architecture.png")


def alerts_card(data: dict):
    w, h = 1400, 780
    im = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(im)
    title, body, small = font("segoeuib.ttf", 32), font("segoeui.ttf", 22), font("segoeui.ttf", 18)
    c = data["log_counts"]
    d.text((48, 28), "Results  ·  generated logs + 3 rules", font=title, fill=WHITE)
    d.text(
        (48, 76),
        f"ssh_fail={c['ssh_failed']}  ssh_ok={c['ssh_accepted']}  http={c['http']}  fw={c['firewall']}  ·  {data['author']}",
        font=small,
        fill=MUTED,
    )
    y = 140
    for a in data["alerts"]:
        color = SEV.get(a["severity"], ACCENT)
        d.rounded_rectangle((48, y, 1352, y + 170), 18, fill=LINE)
        d.rounded_rectangle((72, y + 24, 220, y + 56), 8, fill=color)
        d.text((84, y + 30), a["severity"].upper(), font=small, fill=WHITE)
        d.text((240, y + 26), f"{a['title']}  ·  {a['mitre']}", font=body, fill=WHITE)
        d.text((240, y + 64), f"src {a['src_ip']}", font=small, fill=MUTED)
        extra = []
        if "peak_in_window" in a:
            extra.append(f"{a['failed_ssh']} failed SSH, peak {a['peak_in_window']} in {a['window_sec']}s (need {a['threshold']})")
        if "requests" in a:
            extra.append(f"{a['requests']} HTTP paths with SQL tokens")
        if "unique_ports" in a:
            extra.append(f"{a['unique_ports']} unique dest ports in {a['window_sec']}s")
        d.text((240, y + 100), "  ·  ".join(extra), font=small, fill=WHITE)
        y += 196
    im.save(IMG / "results-alerts.png")


def main():
    data = json.loads((ROOT / "results" / "alerts.json").read_text(encoding="utf-8"))
    architecture()
    alerts_card(data)
    print("wrote", list(IMG.glob("*.png")))


if __name__ == "__main__":
    main()
