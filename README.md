# Strategic Vulnerability Screener

Automated Python pipeline that screens mid-cap SaaS companies for activist investor vulnerability using two factors: (1) a reverse DCF that isolates the market-implied revenue growth rate, and (2) NLP sentiment analysis on SEC 10-Q filings.

**Sample output — July 2026 run:**
| Company | Implied Growth | Historical CAGR | Gap | Score |
|---------|---------------|-----------------|-----|-------|
| Power Integrations (POWI) | 51% | -11% | +61pp | 55/100 MEDIUM |
| Tenable Holdings (TENB) | 52% | 14% | +38pp | 45/100 MEDIUM |

The tearsheet PDF is included in this repo: [`activist_vulnerability_screen_2026-07-26.pdf`](activist_vulnerability_screen_2026-07-26.pdf)

---

## How it works

### Step 1 — Reverse DCF Engine (`reverse_dcf.py`)
For each company, a scipy `brentq` solver finds the revenue growth rate that — when applied to a 7-year DCF (10% WACC, 3% terminal growth) — exactly reproduces the observed enterprise value. This isolates what the market is implicitly pricing in.

### Step 2 — Historical Reality Check (`universe.py`)
The implied rate is benchmarked against the company's 3-year historical revenue CAGR pulled from SEC financial statements via yfinance. The gap between implied and actual is the core signal.

### Step 3 — NLP Sentiment (`sentiment.py`)
MD&A sections from the three most recent 10-Q filings are extracted from SEC EDGAR and scored using a financial lexicon (negative terms: "headwinds", "restructuring", "below expectations", etc.). A deteriorating trend — management tone getting more negative across quarters — combined with valuation stretch raises the vulnerability score.

> **Note:** The sentiment step requires SEC EDGAR's CIK lookup endpoint, which rate-limits aggressively. Run with `--fast` to skip it and use only the reverse DCF signal, which is the stronger of the two factors.

### Step 4 — Composite Score (`scorer.py`)
A 0–100 score from four weighted components:
- Growth gap (40 pts)
- Sentiment trend (25 pts)
- Valuation premium vs. growth rate (20 pts)
- Operating margin compression (15 pts)

Scores ≥70 → HIGH · 45–69 → MEDIUM · 20–44 → LOW · <20 → UNDERVALUED

### Step 5 — PDF Tearsheet (`tearsheet.py`)
Bank advisory-format PDF with executive summary, methodology, and a per-company page showing the DCF finding, sentiment trend, and an activist investment thesis paragraph.

---

## Usage

```bash
pip install -r requirements.txt

# Full run with sentiment (~20 min, 26 companies)
python3 screener.py

# Fast run — reverse DCF only (~3 min)
python3 screener.py --fast

# Test run — 10 tickers, no sentiment (~2 min)
python3 screener.py --test --fast
```

Output: `activist_vulnerability_screen_YYYY-MM-DD.pdf` + `scored_universe_YYYY-MM-DD.csv`

---

## Universe
26 U.S. mid-cap SaaS companies ($500M–$10B market cap). Market data via Yahoo Finance (free). Filings via SEC EDGAR (free).

## Limitations
- Reverse DCF assumes constant WACC and flat capital structure
- Sentiment lexicon is rule-based, not a trained model — directional signal, not precise
- EDGAR rate-limiting makes full sentiment runs unreliable without delays
- Universe is manually curated; some tickers have been delisted or renamed since construction

---

## Related work
This screener was built as a direct extension of a published event study: [Cash vs. Stock Consideration in Mid-Cap M&A (OSF)](https://doi.org/10.17605/OSF.IO/VEP4G), which used the same SEC EDGAR pipeline to analyze announcement returns across 1,400 merger candidates.

**Author:** Yash Bhagat · Round Rock High School · Round Rock, TX
