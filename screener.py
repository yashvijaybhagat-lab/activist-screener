#!/usr/bin/env python3
"""
screener.py — Strategic Vulnerability Screener
Activist Vulnerability Screen: U.S. Mid-Cap SaaS

Run: python3 screener.py
Output: activist_vulnerability_screen_YYYY-MM-DD.pdf
"""

import pandas as pd
import numpy as np
import time
import os
from datetime import datetime

from universe   import build_universe, SAAS_UNIVERSE
from reverse_dcf import reverse_dcf, compute_vulnerability_delta
from sentiment  import analyze_ticker
from scorer     import build_scores, generate_thesis, classify_vulnerability
from tearsheet  import build_tearsheet

OUTPUT_DIR = '.'

def run_screener(max_tickers=None, skip_sentiment=False):
    print("\n" + "="*60)
    print("  STRATEGIC VULNERABILITY SCREENER")
    print("  U.S. Mid-Cap SaaS — Activist Vulnerability Analysis")
    print("="*60 + "\n")

    # ── Stage 1: Universe + Financials ──
    print("[1/4] BUILDING UNIVERSE + PULLING FINANCIALS...")
    universe_csv = 'universe_raw.csv'
    if os.path.exists(universe_csv):
        print(f"  Found cached {universe_csv} — loading...")
        df = pd.read_csv(universe_csv)
    else:
        df = build_universe()

    if max_tickers:
        df = df.head(max_tickers)

    print(f"  Universe: {len(df)} companies\n")

    # ── Stage 2: Reverse DCF ──
    print("[2/4] RUNNING REVERSE DCF ENGINE...")
    dcf_results = []
    for _, row in df.iterrows():
        ticker = row['ticker']
        result = reverse_dcf(
            enterprise_value       = row.get('enterprise_value'),
            revenue_ttm            = row.get('revenue_ttm'),
            ebitda_margin_current  = row.get('op_margin') or 0.05,
        )
        if result:
            hist  = row.get('hist_rev_growth_3yr') or row.get('rev_growth_yoy')
            gap   = compute_vulnerability_delta(
                result['implied_growth_rate'],
                row.get('hist_rev_growth_3yr'),
                row.get('rev_growth_yoy')
            )
            dcf_results.append({
                'ticker':              ticker,
                'implied_growth_rate': result['implied_growth_rate'],
                'growth_gap':          gap,
            })
            print(f"  {ticker:6s}  implied={result['implied_growth_rate']*100:.0f}%  gap={gap*100:.0f}pp" if gap else f"  {ticker:6s}  implied={result['implied_growth_rate']*100:.0f}%")
        else:
            dcf_results.append({'ticker': ticker, 'implied_growth_rate': None, 'growth_gap': None})

    dcf_df = pd.DataFrame(dcf_results)
    df     = df.merge(dcf_df, on='ticker', how='left')
    print()

    # ── Stage 3: Sentiment Analysis ──
    if not skip_sentiment:
        print("[3/4] RUNNING FINBERT SENTIMENT ANALYSIS...")
        sent_results = []
        for _, row in df.iterrows():
            ticker = row['ticker']
            print(f"  {ticker}...", end=' ', flush=True)
            result = analyze_ticker(ticker)
            if result:
                sent_results.append({
                    'ticker':                 ticker,
                    'avg_sentiment':          result['avg_sentiment'],
                    'sentiment_trend':        result['sentiment_trend'],
                    'latest_sentiment_label': result['latest_label'],
                })
                print(f"avg={result['avg_sentiment']:.3f}  trend={result['sentiment_trend']:.3f}  [{result['latest_label']}]")
            else:
                sent_results.append({
                    'ticker': ticker,
                    'avg_sentiment': None,
                    'sentiment_trend': None,
                    'latest_sentiment_label': 'UNKNOWN',
                })
                print("no data")
            time.sleep(0.5)

        sent_df = pd.DataFrame(sent_results)
        df      = df.merge(sent_df, on='ticker', how='left')
        print()
    else:
        print("[3/4] SENTIMENT SKIPPED (--fast mode)\n")
        df['avg_sentiment']          = None
        df['sentiment_trend']        = None
        df['latest_sentiment_label'] = 'UNKNOWN'

    # ── Stage 4: Score + Rank ──
    print("[4/4] COMPUTING VULNERABILITY SCORES...")
    scored_df = build_scores(df)

    # Top companies for tearsheet
    top_n = scored_df[scored_df['vulnerability_label'].isin(['HIGH', 'MEDIUM'])].head(5)
    if len(top_n) == 0:
        top_n = scored_df.head(3)

    companies = []
    for _, row in top_n.iterrows():
        d = row.to_dict()
        d['thesis'] = generate_thesis(d)
        companies.append(d)
        print(f"  {row['ticker']:6s}  score={int(row['vulnerability_score'])}/100  [{row['vulnerability_label']}]")

    print()

    # ── Output: PDF ──
    date_str    = datetime.today().strftime('%Y-%m-%d')
    output_path = f'activist_vulnerability_screen_{date_str}.pdf'
    print(f"GENERATING TEARSHEET → {output_path}...")
    build_tearsheet(companies, scored_df, output_path)

    # Also save scored CSV
    scored_df.to_csv(f'scored_universe_{date_str}.csv', index=False)
    print(f"Full scored universe → scored_universe_{date_str}.csv")

    print("\n" + "="*60)
    print(f"  DONE — {len(companies)} companies flagged")
    print(f"  PDF: {output_path}")
    print("="*60 + "\n")

    return scored_df, companies


if __name__ == '__main__':
    import sys
    fast   = '--fast' in sys.argv       # skip sentiment
    small  = '--test' in sys.argv       # only 10 tickers
    run_screener(
        max_tickers   = 10 if small else None,
        skip_sentiment= fast,
    )
