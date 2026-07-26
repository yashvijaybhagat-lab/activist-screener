# Strategic Vulnerability Screener — Setup

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
# Full run (all 49 tickers, with sentiment) — ~20 mins
python3 screener.py

# Fast run (no sentiment) — ~5 mins  
python3 screener.py --fast

# Test run (10 tickers, no sentiment) — ~2 mins
python3 screener.py --test --fast
```

## Output
- `activist_vulnerability_screen_YYYY-MM-DD.pdf` — the tearsheet
- `scored_universe_YYYY-MM-DD.csv` — full ranked table
- `universe_raw.csv` — cached financial data (reused on re-runs)

## Files
| File | Purpose |
|------|---------|
| `screener.py` | Master script — run this |
| `universe.py` | Pulls financials for 49 SaaS tickers via yfinance |
| `reverse_dcf.py` | Solves for market-implied growth rate |
| `sentiment.py` | Scores MD&A text from 10-Q filings |
| `scorer.py` | Composite vulnerability score + thesis generator |
| `tearsheet.py` | PDF tearsheet builder |
