# reverse_dcf.py — Solve for market-implied growth rate and EBITDA margin

import numpy as np
from scipy.optimize import brentq


def reverse_dcf(enterprise_value, revenue_ttm, ebitda_margin_current,
                wacc=0.10, terminal_growth=0.03, projection_years=7,
                target_ebitda_margin=None):
    """
    Given an observed enterprise value, solve for the revenue growth rate
    the market is implicitly pricing in.

    Parameters:
    - enterprise_value: current EV ($)
    - revenue_ttm: trailing 12m revenue ($)
    - ebitda_margin_current: current EBITDA / revenue (0-1)
    - wacc: discount rate (default 10%)
    - terminal_growth: perpetual growth rate after year N (default 3%)
    - projection_years: DCF horizon (default 7)
    - target_ebitda_margin: if None, holds current margin flat

    Returns dict with:
    - implied_growth_rate: annual revenue CAGR the market prices in
    - implied_ebitda_margin: EBITDA margin in terminal year
    - dcf_at_implied: DCF value at implied growth (should ≈ EV)
    """
    if not all([enterprise_value, revenue_ttm]) or enterprise_value <= 0 or revenue_ttm <= 0:
        return None

    margin = ebitda_margin_current if ebitda_margin_current else 0.10
    if target_ebitda_margin is None:
        target_ebitda_margin = min(margin + 0.05, 0.35)  # assume slight margin expansion

    def dcf_value(growth_rate):
        """Compute DCF enterprise value at a given growth rate."""
        pv = 0
        rev = revenue_ttm
        for yr in range(1, projection_years + 1):
            rev *= (1 + growth_rate)
            # Margin expands linearly from current to target
            t_margin = margin + (target_ebitda_margin - margin) * (yr / projection_years)
            ebitda   = rev * t_margin
            # Simple FCF proxy: EBITDA × (1 - tax) - capex (assume 5% of rev for SaaS)
            fcf = ebitda * 0.78 - rev * 0.05
            pv += fcf / (1 + wacc) ** yr

        # Terminal value (Gordon Growth)
        terminal_ebitda = rev * target_ebitda_margin
        terminal_fcf    = terminal_ebitda * 0.78 - rev * 0.05
        tv              = terminal_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
        pv             += tv / (1 + wacc) ** projection_years

        return pv

    # Solve: find growth_rate such that dcf_value(g) == enterprise_value
    try:
        # Search between -20% and +60% growth
        implied_growth = brentq(
            lambda g: dcf_value(g) - enterprise_value,
            -0.20, 0.60,
            xtol=1e-6, maxiter=200
        )
    except ValueError:
        # If no solution in range, clamp
        try:
            implied_growth = brentq(
                lambda g: dcf_value(g) - enterprise_value,
                -0.50, 1.50,
                xtol=1e-6, maxiter=200
            )
        except:
            return None

    return {
        'implied_growth_rate':    implied_growth,
        'target_ebitda_margin':   target_ebitda_margin,
        'dcf_at_implied':         dcf_value(implied_growth),
        'enterprise_value_actual': enterprise_value,
    }


def compute_vulnerability_delta(implied_growth, hist_growth_3yr, rev_growth_yoy):
    """
    Delta between what market implies vs. what company has actually done.
    Positive = market overly optimistic (vulnerable to disappointment)
    Negative = market overly pessimistic (potential undervaluation)
    """
    # Use best available historical benchmark
    hist = hist_growth_3yr if hist_growth_3yr is not None else rev_growth_yoy
    if hist is None or implied_growth is None:
        return None
    return implied_growth - hist  # positive = market expects MORE than history


if __name__ == '__main__':
    # Quick test
    result = reverse_dcf(
        enterprise_value=5e9,    # $5B EV
        revenue_ttm=500e6,       # $500M revenue
        ebitda_margin_current=0.08,
    )
    print("Test reverse DCF:")
    print(f"  Implied growth rate:  {result['implied_growth_rate']*100:.1f}%")
    print(f"  Target EBITDA margin: {result['target_ebitda_margin']*100:.1f}%")
    print(f"  DCF value at implied: ${result['dcf_at_implied']/1e9:.2f}B")
    print(f"  Actual EV:            ${result['enterprise_value_actual']/1e9:.2f}B")
