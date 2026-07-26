# scorer.py — composite vulnerability score combining reverse DCF + sentiment

import pandas as pd
import numpy as np


def compute_vulnerability_score(row):
    """
    Composite vulnerability score 0–100.
    Higher = more likely activist target.

    Components:
    1. Growth gap (40 pts) — market implies much more than history
    2. Sentiment trend (25 pts) — management language deteriorating
    3. Valuation premium (20 pts) — EV/Revenue vs sector median
    4. Margin compression (15 pts) — margins declining
    """
    score = 0
    breakdown = {}

    # ── 1. Growth gap (40 pts) ──
    # High positive delta = market priced for perfection = vulnerable
    gap = row.get('growth_gap')
    if gap is not None:
        if gap > 0.20:   pts = 40
        elif gap > 0.15: pts = 32
        elif gap > 0.10: pts = 24
        elif gap > 0.05: pts = 16
        elif gap > 0:    pts = 8
        elif gap < -0.10: pts = 0   # undervalued signal
        else:            pts = 4
        score += pts
        breakdown['growth_gap_pts'] = pts

    # ── 2. Sentiment trend (25 pts) ──
    # Negative trend = management increasingly negative = vulnerable
    trend = row.get('sentiment_trend')
    if trend is not None:
        if trend < -0.20:   pts = 25
        elif trend < -0.10: pts = 20
        elif trend < -0.05: pts = 15
        elif trend < 0:     pts = 8
        else:               pts = 0
        score += pts
        breakdown['sentiment_pts'] = pts

    # ── 3. Valuation premium (20 pts) ──
    # High EV/Rev relative to growth = priced for perfection
    ev_rev = row.get('ev_revenue')
    rev_gr = row.get('rev_growth_yoy') or 0
    if ev_rev is not None:
        # Rule of 40: EV/Rev should roughly = (growth + margin) / some factor
        # Simple: if paying >10x revenue for <20% growth, that's stretched
        if ev_rev > 10 and rev_gr < 0.20:   pts = 20
        elif ev_rev > 7 and rev_gr < 0.25:  pts = 15
        elif ev_rev > 5 and rev_gr < 0.30:  pts = 10
        elif ev_rev > 3:                     pts = 5
        else:                                pts = 0
        score += pts
        breakdown['valuation_pts'] = pts

    # ── 4. Margin compression (15 pts) ──
    op_margin = row.get('op_margin') or 0
    gross_margin = row.get('gross_margin') or 0
    if op_margin < -0.20:    pts = 15
    elif op_margin < -0.10:  pts = 10
    elif op_margin < 0:      pts = 5
    else:                    pts = 0
    score += pts
    breakdown['margin_pts'] = pts

    return min(score, 100), breakdown


def classify_vulnerability(score):
    if score >= 70:   return 'HIGH', '#c0392b'
    elif score >= 45: return 'MEDIUM', '#e67e22'
    elif score >= 20: return 'LOW', '#27ae60'
    else:             return 'UNDERVALUED', '#2980b9'


def build_scores(df):
    """Apply scoring to the full universe dataframe."""
    results = []
    for _, row in df.iterrows():
        score, breakdown = compute_vulnerability_score(row)
        label, color     = classify_vulnerability(score)
        results.append({
            **row.to_dict(),
            'vulnerability_score': score,
            'vulnerability_label': label,
            'vulnerability_color': color,
            **breakdown,
        })

    scored = pd.DataFrame(results)
    scored = scored.sort_values('vulnerability_score', ascending=False)
    return scored


def generate_thesis(row):
    """Generate a one-paragraph activist thesis for a flagged company."""
    name    = row.get('name', row.get('ticker'))
    ticker  = row.get('ticker')
    implied = row.get('implied_growth_rate', 0)
    hist    = row.get('hist_rev_growth_3yr') or row.get('rev_growth_yoy', 0)
    gap     = row.get('growth_gap', 0)
    ev_rev  = row.get('ev_revenue', 0)
    margin  = row.get('op_margin', 0)
    sent    = row.get('latest_sentiment_label', 'NEUTRAL')

    thesis = (
        f"{name} ({ticker}) trades at {ev_rev:.1f}x trailing revenue, "
        f"implying a {implied*100:.0f}% annual revenue CAGR over the next seven years. "
        f"Against a {hist*100:.0f}% three-year historical growth rate, "
        f"this represents a {gap*100:.0f} percentage-point expectation gap — "
        f"the market is pricing in a sustained acceleration that the company's "
        f"own track record does not support. "
    )

    if margin < -0.05:
        thesis += (
            f"Operating margins of {margin*100:.0f}% leave little room for error. "
        )

    if sent == 'NEGATIVE':
        thesis += (
            f"Management sentiment in recent filings has turned increasingly defensive, "
            f"a pattern historically associated with pre-activist situations. "
        )

    thesis += (
        f"The combination of stretched valuation, decelerating growth, and "
        f"deteriorating management tone creates the conditions for an activist "
        f"campaign targeting a strategic review or outright sale."
    )

    return thesis


if __name__ == '__main__':
    # Quick test
    test_row = {
        'name': 'TestCo', 'ticker': 'TEST',
        'growth_gap': 0.18, 'sentiment_trend': -0.15,
        'ev_revenue': 8.5, 'rev_growth_yoy': 0.12,
        'op_margin': -0.08, 'hist_rev_growth_3yr': 0.10,
        'implied_growth_rate': 0.28, 'latest_sentiment_label': 'NEGATIVE',
    }
    score, breakdown = compute_vulnerability_score(test_row)
    label, color     = classify_vulnerability(score)
    thesis           = generate_thesis(test_row)
    print(f"Score: {score}/100  —  {label}")
    print(f"Breakdown: {breakdown}")
    print(f"\nThesis:\n{thesis}")
