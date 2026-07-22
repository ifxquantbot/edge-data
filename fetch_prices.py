"""Edge Engine data mirror — fetches daily closes from Yahoo Finance and writes
CSVs to data/. Runs inside GitHub Actions (which has unrestricted egress).

Symbols: ^GSPC (SPX), ^NDX, GC=F (gold front-month), ^VIX.
Output: data/spx.csv, data/ndx.csv, data/gold.csv, data/vix.csv
Format: date,close (one row per trading day, 2023-01-01 onward, full overwrite
each run so revisions/corrections self-heal).
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SYMBOLS = {"spx": "^GSPC", "ndx": "^NDX", "gold": "GC=F", "vix": "^VIX"}
START = int(datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp())
OUT = Path("data")
OUT.mkdir(exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def fetch(symbol):
    end = int(time.time())
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + urllib.parse.quote(symbol)
           + "?interval=1d&period1=" + str(START) + "&period2=" + str(end))
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.load(r)
    res = j["chart"]["result"][0]
    ts, cl = res["timestamp"], res["indicators"]["quote"][0]["close"]
    rows = []
    for t, c in zip(ts, cl):
        if c is None:
            continue
        d = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d")
        rows.append(d + "," + format(c, ".2f"))
    return rows


def main():
    failures = []
    for name, sym in SYMBOLS.items():
        try:
            rows = fetch(sym)
            if len(rows) < 500:
                raise ValueError("only " + str(len(rows)) + " rows — refusing to overwrite")
            (OUT / (name + ".csv")).write_text("\n".join(rows) + "\n")
            print(name, len(rows), "rows, last", rows[-1])
            time.sleep(2)  # be polite
        except Exception as e:
            failures.append(name + " (" + sym + "): " + str(e))
            print("FAILED", name, e)
    (OUT / "last_run.txt").write_text(
        datetime.now(timezone.utc).isoformat() + "\n"
        + ("OK" if not failures else "PARTIAL: " + "; ".join(failures)) + "\n")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

