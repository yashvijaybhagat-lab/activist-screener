# sentiment.py — Rule-based financial sentiment (no external model required)
# Uses a curated financial lexicon tuned for 10-Q/earnings language

import requests
import re
import time

EDGAR_BASE = "https://data.sec.gov"
SEC_BASE   = "https://www.sec.gov"
HEADERS    = {"User-Agent": "Yash Bhagat ybhagat2011@gmail.com"}

# ── Financial sentiment lexicon ──
NEGATIVE_TERMS = [
    'headwinds', 'challenging', 'uncertainty', 'decline', 'decreased', 'deteriorat',
    'difficult', 'weakness', 'softness', 'concern', 'cautious', 'pressure',
    'impairment', 'restructur', 'workforce reduction', 'layoff', 'downturn',
    'below expectations', 'miss', 'shortfall', 'decelerat', 'slowdown',
    'competitive pressure', 'churn', 'attrition', 'macro', 'inflationary',
    'cost overrun', 'margin compression', 'loss', 'write-off', 'write-down',
    'goodwill impairment', 'going concern', 'covenant', 'default risk',
    'delayed', 'postponed', 'cancelled', 'terminated', 'reduced guidance',
    'lower than expected', 'below plan', 'risks and uncertainties',
]

POSITIVE_TERMS = [
    'growth', 'momentum', 'strong', 'record', 'exceeded', 'outperform',
    'accelerat', 'expansion', 'opportunity', 'pipeline', 'demand', 'robust',
    'healthy', 'confident', 'optimistic', 'traction', 'adoption', 'retention',
    'net revenue retention', 'upsell', 'cross-sell', 'market share gain',
    'above expectations', 'beat', 'raised guidance', 'increase', 'improved',
    'higher than expected', 'ahead of plan', 'favorable', 'efficient',
    'scalable', 'durable', 'resilient', 'differentiated',
]

DEFENSIVE_TERMS = [
    # Language that appears when mgmt is under pressure
    'we believe', 'we are confident that', 'despite', 'notwithstanding',
    'we remain committed', 'we continue to monitor', 'we are taking steps',
    'proactive measures', 'we are addressing', 'we are actively',
    'in response to', 'given the current environment',
]


def score_text(text):
    """Score a block of text using financial lexicon."""
    text_lower = text.lower()
    words      = len(text_lower.split())
    if words == 0:
        return 0

    neg = sum(text_lower.count(t) for t in NEGATIVE_TERMS)
    pos = sum(text_lower.count(t) for t in POSITIVE_TERMS)
    def_ = sum(text_lower.count(t) for t in DEFENSIVE_TERMS) * 0.5

    # Normalize by text length (per 1000 words)
    norm    = words / 1000
    net_pos = (pos - neg - def_) / max(norm, 0.5)

    # Map to -1 to +1 range
    score = max(-1.0, min(1.0, net_pos / 10))
    return round(score, 4)


def get_cik(ticker):
    import time; time.sleep(1.5)
    res  = requests.get(f"{EDGAR_BASE}/files/company_tickers.json", headers=HEADERS, timeout=15, verify=False)
    data = res.json()
    for e in data.values():
        if e['ticker'].upper() == ticker.upper():
            return str(e['cik_str']).zfill(10)
    return None


def get_recent_filings_text(ticker, n=3):
    """Fetch MD&A text from last n 10-Q filings."""
    cik = get_cik(ticker)
    if not cik:
        return []

    res  = requests.get(f"{EDGAR_BASE}/submissions/CIK{cik}.json", headers=HEADERS, timeout=15, verify=False)
    data = res.json()
    f    = data.get('filings', {}).get('recent', {})

    forms   = f.get('form', [])
    accNums = f.get('accessionNumber', [])
    dates   = f.get('filingDate', [])

    filings = []
    for i, form in enumerate(forms):
        if form in ('10-Q', '10-K'):
            filings.append({'acc': accNums[i], 'date': dates[i], 'form': form})
        if len(filings) >= n:
            break

    texts = []
    for filing in filings:
        try:
            acc_clean = filing['acc'].replace('-', '')
            cik_int   = int(cik)
            idx_url   = f"{SEC_BASE}/Archives/edgar/data/{cik_int}/{acc_clean}/{filing['acc']}-index.htm"
            idx_res   = requests.get(idx_url, headers=HEADERS, timeout=15, verify=False)

            doc_match = re.search(
                r'href="(/Archives/edgar/data/[^"]+\.htm)"',
                idx_res.text, re.IGNORECASE
            )
            if not doc_match:
                continue

            doc_url = f"{SEC_BASE}{doc_match.group(1)}"
            doc_res = requests.get(doc_url, headers=HEADERS, timeout=15)

            raw = re.sub(r'<[^>]+>', ' ', doc_res.text)
            raw = re.sub(r'\s+', ' ', raw).strip()

            # Extract MD&A section
            mda_match = re.search(
                r"management.{0,20}discussion.{0,20}analysis(.{500,8000}?)(?:quantitative|liquidity|critical|item\s+[34])",
                raw, re.IGNORECASE | re.DOTALL
            )
            section = mda_match.group(1) if mda_match else raw[2000:8000]

            texts.append({'date': filing['date'], 'form': filing['form'], 'text': section})
            time.sleep(0.4)
        except:
            continue

    return texts


def analyze_ticker(ticker):
    """Full sentiment pipeline for one ticker."""
    texts = get_recent_filings_text(ticker, n=3)
    if not texts:
        return None

    scores = []
    for t in texts:
        s = score_text(t['text'])
        scores.append({
            'date':            t['date'],
            'form':            t['form'],
            'sentiment_score': s,
            'label':           'POSITIVE' if s > 0.05 else ('NEGATIVE' if s < -0.05 else 'NEUTRAL'),
        })

    if not scores:
        return None

    avg   = sum(s['sentiment_score'] for s in scores) / len(scores)
    trend = scores[0]['sentiment_score'] - scores[-1]['sentiment_score'] if len(scores) >= 2 else 0

    return {
        'filings':         scores,
        'avg_sentiment':   round(avg, 4),
        'sentiment_trend': round(trend, 4),
        'latest_label':    scores[0]['label'],
    }


if __name__ == '__main__':
    result = analyze_ticker('YEXT')
    if result:
        print(f"Avg: {result['avg_sentiment']:.4f}  Trend: {result['sentiment_trend']:.4f}  [{result['latest_label']}]")
        for f in result['filings']:
            print(f"  {f['date']} {f['form']}: {f['sentiment_score']:.4f} ({f['label']})")
