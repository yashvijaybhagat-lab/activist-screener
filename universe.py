# universe.py — Mid-cap SaaS universe + financial data pull

import yfinance as yf
import pandas as pd
import json
import time

# ── Mid-cap SaaS universe ($500M–$5B market cap) ──
# Hand-curated set of pure-play SaaS companies in the target range
SAAS_UNIVERSE = [
    "APPF", "AVLR", "BAND", "BIGC", "BILL", "BRZE", "CWAN",
    "DDOG", "DOCN", "DUOL", "ESTC", "FROG", "GTLB", "HUBS",
    "JAMF", "LPSN", "MNDY", "NCNO", "NNOX", "NTNX", "PCTY",
    "PEGA", "PLTR", "POWI", "PRGS", "PSFE", "PWSC", "RXST",
    "SEMR", "SMAR", "SPSC", "SPRK", "TASK", "TENB", "TOST",
    "TRMK", "TTGT", "TWLO", "VEEV", "VRNS", "WDAY", "WEX",
    "XMTR", "YEXT", "ZI",   "ZETA", "ZS",   "ZUO",  "ZYXI"
]

def pull_financials(ticker):
    """Pull all financials needed for reverse DCF + screening."""
    try:
        tk   = yf.Ticker(ticker)
        info = tk.info

        # Market data
        price     = info.get('currentPrice') or info.get('regularMarketPrice')
        mkt_cap   = info.get('marketCap')
        ev        = info.get('enterpriseValue')
        shares    = info.get('sharesOutstanding')

        # Skip if outside $500M–$10B market cap (wider net, filter later)
        if not mkt_cap or mkt_cap < 400e6 or mkt_cap > 12e6:
            if not mkt_cap or not (400e6 <= mkt_cap <= 12e9):
                return None

        # Income statement
        revenue_ttm  = info.get('totalRevenue')
        ebitda_ttm   = info.get('ebitda')
        gross_margin = info.get('grossMargins')
        op_margin    = info.get('operatingMargins')
        net_income   = info.get('netIncomeToCommon')

        # Growth
        rev_growth_yoy = info.get('revenueGrowth')       # trailing 12m YoY
        earnings_growth= info.get('earningsGrowth')

        # Balance sheet
        cash         = info.get('totalCash')
        total_debt   = info.get('totalDebt')
        net_debt     = (total_debt or 0) - (cash or 0)

        # Analyst estimates (forward)
        fwd_eps      = info.get('forwardEps')
        fwd_pe       = info.get('forwardPE')
        peg          = info.get('pegRatio')
        ps_ratio     = info.get('priceToSalesTrailing12Months')
        ev_revenue   = info.get('enterpriseToRevenue')
        ev_ebitda    = info.get('enterpriseToEbitda')

        # Historical revenue growth (3yr average from financials)
        try:
            fin = tk.financials
            if fin is not None and not fin.empty and 'Total Revenue' in fin.index:
                rev_hist = fin.loc['Total Revenue'].dropna().sort_index()
                if len(rev_hist) >= 2:
                    rev_list = rev_hist.tolist()
                    growths  = [(rev_list[i]/rev_list[i-1])-1
                                for i in range(1, len(rev_list))
                                if rev_list[i-1] > 0]
                    hist_rev_growth_3yr = sum(growths)/len(growths) if growths else None
                else:
                    hist_rev_growth_3yr = None
            else:
                hist_rev_growth_3yr = None
        except:
            hist_rev_growth_3yr = None

        return {
            'ticker':              ticker,
            'name':                info.get('longName') or info.get('shortName', ticker),
            'sector':              info.get('sector', 'Technology'),
            'industry':            info.get('industry', ''),
            'price':               price,
            'market_cap':          mkt_cap,
            'enterprise_value':    ev,
            'shares_outstanding':  shares,
            'revenue_ttm':         revenue_ttm,
            'ebitda_ttm':          ebitda_ttm,
            'gross_margin':        gross_margin,
            'op_margin':           op_margin,
            'net_income':          net_income,
            'net_debt':            net_debt,
            'rev_growth_yoy':      rev_growth_yoy,
            'hist_rev_growth_3yr': hist_rev_growth_3yr,
            'earnings_growth':     earnings_growth,
            'fwd_eps':             fwd_eps,
            'fwd_pe':              fwd_pe,
            'peg_ratio':           peg,
            'ps_ratio':            ps_ratio,
            'ev_revenue':          ev_revenue,
            'ev_ebitda':           ev_ebitda,
            'cash':                cash,
            'total_debt':          total_debt,
        }
    except Exception as e:
        print(f"  ERR {ticker}: {e}")
        return None


def build_universe():
    print(f"Pulling financials for {len(SAAS_UNIVERSE)} tickers...")
    rows = []
    for i, ticker in enumerate(SAAS_UNIVERSE):
        print(f"  [{i+1}/{len(SAAS_UNIVERSE)}] {ticker}", end=' ')
        data = pull_financials(ticker)
        if data:
            rows.append(data)
            print(f"✓  mktcap=${data['market_cap']/1e9:.2f}B")
        else:
            print("skipped")
        time.sleep(0.3)  # rate limit

    df = pd.DataFrame(rows)
    df.to_csv('universe_raw.csv', index=False)
    print(f"\nUniverse: {len(df)} companies saved to universe_raw.csv")
    return df


if __name__ == '__main__':
    build_universe()
