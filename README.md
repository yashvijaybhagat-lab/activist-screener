# IB Research Terminal

A Bloomberg-style Chrome extension for investment banking research workflows. Enter any ticker to pull live merger filings from SEC EDGAR, real-time market data, insider transactions, and run DCF/WACC models — all from your browser, no subscription required.

![Extension tabs: FILINGS · QUOTE · INSIDER · DCF/WACC]

---

## Features

### FILINGS tab
- Queries SEC EDGAR for merger-related filings (8-K, SC TO-T, DEFM14A, 425)
- Parses each filing in real time for:
  - **Acquirer name** — regex against SEC legal boilerplate ("Agreement and Plan of Merger between X and Y")
  - **Deal value** — extracted from press release language ($M or $B)
  - **Consideration type** — CASH / STOCK / MIXED
  - **Offer premium** — fetches unaffected stock price from Yahoo Finance and computes the gap
- Rows populate live with skeleton loading animation while parsing
- One-click **EXPORT .XLS** — formatted Excel file ready to paste into a precedent transaction model

### QUOTE tab
16 real-time data points: price, day change, open/high/low, volume, market cap, 52W range, P/E, EPS, dividend yield, beta, float, sector. Data from Yahoo Finance.

### INSIDER tab
Recent Form 4 insider transaction filings from SEC EDGAR.

### DCF / WACC tab
- **WACC calculator** — CAPM-based (Rf + β × ERP), with after-tax cost of debt and weighted average output
- **Terminal value DCF** — EBITDA × exit multiple, discounted at WACC over N years, outputs equity value and implied price per share

---

## Install (Developer Mode)

1. Download and unzip the release
2. Open Chrome → `chrome://extensions`
3. Enable **Developer mode** (top right toggle)
4. Click **Load unpacked** → select the `precedent-scraper` folder
5. Click the extension icon (puzzle piece → "TERM") in your toolbar

No API keys required. All data sources are free and public.

---

## Good tickers to test
| Ticker | Deal |
|--------|------|
| `ATVI` | Microsoft acquisition — large all-cash deal |
| `TWTR` | Twitter / Elon Musk — cash |
| `VMW` | Broadcom — cash + stock |

---

## Architecture

```
precedent-scraper/
├── manifest.json       Chrome MV3 config
├── popup.html          UI — 4 tabs, command bar, footer
└── src/
    ├── popup.js        Controller — search, tabs, loading states, calculators
    ├── popup.css       Terminal design system (amber / dark palette)
    ├── edgar.js        SEC EDGAR API — ticker → CIK → filing list → raw text
    ├── parser.js       Filing parser — acquirer, deal value, consideration, premium
    ├── export.js       Excel export — formatted .xls with color-coded consideration
    └── background.js   MV3 service worker
```

## Data sources
| Source | Data | Cost |
|--------|------|------|
| SEC EDGAR `data.sec.gov` | Filings, CIK lookup, Form 4 | Free |
| Yahoo Finance `query1.finance.yahoo.com` | Quotes, historicals | Free |

## Limitations
- Insider tab shows filing dates only — full Form 4 XML parsing (insider name, shares, price) is not yet implemented
- Parser accuracy depends on consistent SEC filing language; some acquirer names may not resolve
- ~40 filing cap per ticker (EDGAR returns recent filings only)

---

## Related work
The EDGAR parsing pipeline in `edgar.js` and `parser.js` was built from the same methodology used in a published M&A event study: [Cash vs. Stock Consideration in Mid-Cap M&A (OSF)](https://doi.org/10.17605/OSF.IO/VEP4G)

**Author:** Yash Bhagat · Round Rock High School · Round Rock, TX · [github.com/yashvijaybhagat-lab](https://github.com/yashvijaybhagat-lab)
