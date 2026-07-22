# edge-data — price mirror for the Edge Research Engine

Nightly GitHub Action fetches daily closes (SPX, NDX, gold, VIX) from Yahoo
Finance and commits them to `data/`, so the Edge Engine's scheduled quarterly
research runs can read fresh data without a browser.

- Weeknights 22:30 UTC the workflow refreshes all four CSVs (full overwrite
  from 2023-01-01, so data corrections self-heal).
- `data/last_run.txt` carries a UTC timestamp + OK/PARTIAL status so consumers
  can distinguish "market holiday" from "fetch broke".
- CSV format: `YYYY-MM-DD,close` — no header, one row per trading day.
- Manual refresh: Actions tab → "Fetch daily prices" → Run workflow.
