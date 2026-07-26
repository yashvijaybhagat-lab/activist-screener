# tearsheet.py — PDF tearsheet generator, bank advisory format

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime

# ── Color palette ──
NAVY    = colors.HexColor('#0d1b2a')
TEAL    = colors.HexColor('#1F4E5F')
AMBER   = colors.HexColor('#e8a020')
RED     = colors.HexColor('#c0392b')
ORANGE  = colors.HexColor('#e67e22')
GREEN   = colors.HexColor('#27ae60')
BLUE    = colors.HexColor('#2980b9')
LGRAY   = colors.HexColor('#f5f6fa')
MGRAY   = colors.HexColor('#dcdde1')
DGRAY   = colors.HexColor('#636e72')
WHITE   = colors.white
BLACK   = colors.black

def build_styles():
    base = getSampleStyleSheet()
    styles = {
        'cover_title': ParagraphStyle('cover_title',
            fontName='Helvetica-Bold', fontSize=22,
            textColor=WHITE, leading=28, alignment=TA_LEFT),
        'cover_sub': ParagraphStyle('cover_sub',
            fontName='Helvetica', fontSize=11,
            textColor=colors.HexColor('#b2bec3'), leading=16, alignment=TA_LEFT),
        'cover_label': ParagraphStyle('cover_label',
            fontName='Helvetica-Bold', fontSize=8,
            textColor=AMBER, leading=12, alignment=TA_LEFT,
            spaceAfter=2, spaceBefore=10),
        'section_header': ParagraphStyle('section_header',
            fontName='Helvetica-Bold', fontSize=10,
            textColor=TEAL, leading=14, spaceBefore=14, spaceAfter=4),
        'body': ParagraphStyle('body',
            fontName='Helvetica', fontSize=9,
            textColor=colors.HexColor('#2d3436'), leading=14,
            spaceBefore=4, spaceAfter=4),
        'body_small': ParagraphStyle('body_small',
            fontName='Helvetica', fontSize=8,
            textColor=DGRAY, leading=12),
        'company_name': ParagraphStyle('company_name',
            fontName='Helvetica-Bold', fontSize=16,
            textColor=NAVY, leading=20, spaceBefore=6, spaceAfter=2),
        'company_ticker': ParagraphStyle('company_ticker',
            fontName='Helvetica-Bold', fontSize=10,
            textColor=TEAL, leading=14),
        'thesis': ParagraphStyle('thesis',
            fontName='Helvetica', fontSize=9,
            textColor=colors.HexColor('#2d3436'), leading=15,
            spaceBefore=6, spaceAfter=6,
            borderPad=8),
        'footer': ParagraphStyle('footer',
            fontName='Helvetica', fontSize=7,
            textColor=DGRAY, leading=10, alignment=TA_CENTER),
        'metric_label': ParagraphStyle('metric_label',
            fontName='Helvetica', fontSize=8,
            textColor=DGRAY, leading=12),
        'metric_value': ParagraphStyle('metric_value',
            fontName='Helvetica-Bold', fontSize=13,
            textColor=NAVY, leading=16),
        'disclaimer': ParagraphStyle('disclaimer',
            fontName='Helvetica-Oblique', fontSize=7,
            textColor=DGRAY, leading=10, alignment=TA_CENTER),
    }
    return styles

def fmt_m(val):
    if val is None: return '—'
    if abs(val) >= 1e9: return f'${val/1e9:.2f}B'
    if abs(val) >= 1e6: return f'${val/1e6:.0f}M'
    return f'${val:,.0f}'

def fmt_pct(val):
    if val is None: return '—'
    return f'{val*100:.1f}%'

def fmt_x(val):
    if val is None: return '—'
    return f'{val:.1f}x'

def vuln_color(label):
    return {'HIGH': RED, 'MEDIUM': ORANGE, 'LOW': GREEN, 'UNDERVALUED': BLUE}.get(label, DGRAY)


def build_tearsheet(top_companies, universe_df, output_path='activist_vulnerability_screen.pdf'):
    today = datetime.today().strftime('%B %d, %Y')
    doc   = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.65*inch, rightMargin=0.65*inch,
        topMargin=0.65*inch,  bottomMargin=0.65*inch,
    )
    S = build_styles()
    story = []

    # ══════════════════════════════════════════════
    # PAGE 1 — COVER + EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════

    # Header bar
    cover_header = Table(
        [[Paragraph('STRATEGIC VULNERABILITY SCREEN', S['cover_title']),
          Paragraph(f'CONFIDENTIAL  ·  {today}', ParagraphStyle('r',
              fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#636e72'),
              alignment=TA_RIGHT))]],
        colWidths=[5*inch, 2.2*inch]
    )
    cover_header.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), NAVY),
        ('TOPPADDING',   (0,0), (-1,-1), 18),
        ('BOTTOMPADDING',(0,0), (-1,-1), 18),
        ('LEFTPADDING',  (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(cover_header)
    story.append(Spacer(1, 0.12*inch))

    # Subtitle block
    story.append(Paragraph(
        'U.S. Mid-Cap SaaS — Activist Vulnerability Analysis',
        ParagraphStyle('sub2', fontName='Helvetica-Bold', fontSize=13,
                       textColor=NAVY, leading=18)
    ))
    story.append(Paragraph(
        'Reverse DCF + NLP Sentiment Screening  ·  Yash Bhagat  ·  Round Rock High School',
        ParagraphStyle('sub3', fontName='Helvetica', fontSize=9,
                       textColor=DGRAY, leading=14, spaceAfter=10)
    ))
    story.append(HRFlowable(width='100%', thickness=1.5, color=TEAL, spaceAfter=10))

    # Executive summary
    story.append(Paragraph('EXECUTIVE SUMMARY', S['section_header']))
    story.append(Paragraph(
        f'This screen applies a two-factor model across {len(universe_df)} U.S. mid-cap SaaS '
        f'companies to identify names where (1) the market-implied revenue growth rate '
        f'materially exceeds the company\'s historical track record, and (2) management '
        f'language in recent SEC filings exhibits a deteriorating sentiment trend. '
        f'The combination of valuation stretch and deteriorating management tone has historically '
        f'preceded activist campaigns by firms such as Elliott Management, Starboard Value, '
        f'and Engaged Capital. The model flags {sum(1 for c in top_companies if c.get("vulnerability_label") == "HIGH")} '
        f'companies as HIGH vulnerability and {sum(1 for c in top_companies if c.get("vulnerability_label") == "MEDIUM")} '
        f'as MEDIUM vulnerability.',
        S['body']
    ))

    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph('TOP FLAGGED COMPANIES', S['section_header']))

    # Summary table
    tbl_data = [['COMPANY', 'TICKER', 'MKT CAP', 'IMPLIED GROWTH', 'HIST. GROWTH', 'GAP', 'SENTIMENT', 'SCORE']]
    for c in top_companies:
        gap   = c.get('growth_gap')
        gap_s = f"+{gap*100:.0f}pp" if gap and gap > 0 else (f"{gap*100:.0f}pp" if gap else '—')
        tbl_data.append([
            c.get('name', '')[:22],
            c.get('ticker', ''),
            fmt_m(c.get('market_cap')),
            fmt_pct(c.get('implied_growth_rate')),
            fmt_pct(c.get('hist_rev_growth_3yr') or c.get('rev_growth_yoy')),
            gap_s,
            c.get('latest_sentiment_label', '—'),
            str(int(c.get('vulnerability_score', 0))),
        ])

    tbl = Table(tbl_data, colWidths=[1.7*inch, 0.6*inch, 0.75*inch, 0.85*inch, 0.85*inch, 0.6*inch, 0.75*inch, 0.55*inch])
    tbl_style = [
        ('BACKGROUND',    (0,0), (-1,0),  NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('TEXTCOLOR',     (0,1), (-1,-1), NAVY),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LGRAY]),
        ('GRID',          (0,0), (-1,-1), 0.3, MGRAY),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('ALIGN',         (2,0), (-1,-1), 'RIGHT'),
    ]
    # Color the score column by vulnerability
    for i, c in enumerate(top_companies, 1):
        col = vuln_color(c.get('vulnerability_label', ''))
        tbl_style.append(('TEXTCOLOR', (7,i), (7,i), col))
        tbl_style.append(('FONTNAME',  (7,i), (7,i), 'Helvetica-Bold'))
    tbl.setStyle(TableStyle(tbl_style))
    story.append(tbl)

    story.append(PageBreak())

    # ══════════════════════════════════════════════
    # PAGE 2 — METHODOLOGY
    # ══════════════════════════════════════════════

    story.append(Paragraph('METHODOLOGY', S['section_header']))
    story.append(HRFlowable(width='100%', thickness=0.5, color=MGRAY, spaceAfter=8))

    meth_sections = [
        ('Step 1 — Reverse DCF Engine',
         'For each company, the model solves for the revenue growth rate that, when applied to a '
         '7-year DCF using a 10% WACC and 3% terminal growth rate, exactly reproduces the '
         'observed enterprise value. This isolates the market\'s implicit growth assumption — '
         'the exact rate of expansion the current stock price requires to be justified. '
         'FCF is proxied as EBITDA × (1 − 22% tax rate) − 5% of revenue (SaaS capex assumption).'),

        ('Step 2 — Historical Reality Check',
         'The market-implied growth rate is benchmarked against the company\'s 3-year historical '
         'revenue CAGR, sourced from SEC financial statements. The delta — "expectation gap" — '
         'measures how far the market\'s implicit assumption exceeds (or lags) actual performance. '
         'A large positive gap signals valuation stretch; the company must accelerate materially '
         'beyond its own history to justify the current price.'),

        ('Step 3 — NLP Sentiment Analysis (FinBERT)',
         'The MD&A sections of the three most recent 10-Q filings are extracted from SEC EDGAR '
         'and processed through FinBERT, a BERT-based model fine-tuned on financial text '
         '(Araci, 2019). Each filing receives a sentiment score from −1.0 (negative) to +1.0 '
         '(positive). The trend — the change from oldest to newest filing — captures whether '
         'management tone is deteriorating. A negative trend combined with valuation stretch '
         'is the core vulnerability signal.'),

        ('Step 4 — Composite Vulnerability Score',
         'A 0–100 composite score is computed from four weighted components: '
         'Growth Gap (40 pts), Sentiment Trend (25 pts), Valuation Premium vs. growth rate (20 pts), '
         'and Operating Margin compression (15 pts). '
         'Scores ≥70 are classified HIGH; 45–69 MEDIUM; 20–44 LOW; <20 UNDERVALUED.'),
    ]

    for title, text in meth_sections:
        story.append(Paragraph(title, ParagraphStyle('meth_title',
            fontName='Helvetica-Bold', fontSize=9, textColor=TEAL,
            spaceBefore=10, spaceAfter=3)))
        story.append(Paragraph(text, S['body']))

    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph('LIMITATIONS',
        ParagraphStyle('lim', fontName='Helvetica-Bold', fontSize=9,
                       textColor=NAVY, spaceBefore=8, spaceAfter=3)))
    story.append(Paragraph(
        'This screen is a first-pass quantitative filter, not a definitive activist prediction. '
        'The reverse DCF assumes constant WACC and does not model debt structure changes. '
        'FinBERT sentiment on SEC filings captures tone but cannot assess strategic context. '
        'Market cap filters exclude micro-cap and mega-cap situations. '
        'Results should be interpreted as a prioritization tool for further fundamental analysis.',
        S['body_small']
    ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════
    # PAGES 3+ — ONE PAGE PER FLAGGED COMPANY
    # ══════════════════════════════════════════════

    for c in top_companies:
        vuln_label = c.get('vulnerability_label', '—')
        vuln_col   = vuln_color(vuln_label)
        ticker     = c.get('ticker', '')
        name       = c.get('name', ticker)

        # Company header
        hdr = Table(
            [[
                Paragraph(name, S['company_name']),
                Table([[
                    Paragraph(vuln_label, ParagraphStyle('vl',
                        fontName='Helvetica-Bold', fontSize=11,
                        textColor=WHITE, alignment=TA_CENTER))
                ]], colWidths=[1.1*inch])
            ]],
            colWidths=[5.5*inch, 1.2*inch]
        )
        hdr.setStyle(TableStyle([
            ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND',   (1,0), (1,0),   vuln_col),
            ('TOPPADDING',   (1,0), (1,0),   8),
            ('BOTTOMPADDING',(1,0), (1,0),   8),
            ('LEFTPADDING',  (1,0), (1,0),   4),
            ('RIGHTPADDING', (1,0), (1,0),   4),
        ]))
        story.append(hdr)

        story.append(Paragraph(
            f'{ticker}  ·  {c.get("industry", "Software")}  ·  '
            f'Score: {int(c.get("vulnerability_score",0))}/100',
            S['company_ticker']
        ))
        story.append(HRFlowable(width='100%', thickness=1, color=TEAL, spaceAfter=8))

        # Key metrics grid
        metrics = [
            ('Market Cap',       fmt_m(c.get('market_cap'))),
            ('Enterprise Value', fmt_m(c.get('enterprise_value'))),
            ('Revenue (TTM)',    fmt_m(c.get('revenue_ttm'))),
            ('EV / Revenue',     fmt_x(c.get('ev_revenue'))),
            ('Gross Margin',     fmt_pct(c.get('gross_margin'))),
            ('Op. Margin',       fmt_pct(c.get('op_margin'))),
            ('Rev Growth YoY',   fmt_pct(c.get('rev_growth_yoy'))),
            ('3Yr Hist. Growth', fmt_pct(c.get('hist_rev_growth_3yr'))),
        ]

        m_rows = []
        for i in range(0, len(metrics), 4):
            chunk = metrics[i:i+4]
            label_row = [Paragraph(m[0], S['metric_label']) for m in chunk]
            value_row = [Paragraph(m[1], S['metric_value']) for m in chunk]
            m_rows.append(label_row)
            m_rows.append(value_row)

        m_tbl = Table(m_rows, colWidths=[1.7*inch]*4)
        m_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), LGRAY),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
            ('LINEBELOW',     (0,1), (-1,1),  0.3, MGRAY),
        ]))
        story.append(m_tbl)
        story.append(Spacer(1, 0.12*inch))

        # Reverse DCF finding
        story.append(Paragraph('REVERSE DCF FINDING', S['section_header']))
        implied = c.get('implied_growth_rate')
        hist    = c.get('hist_rev_growth_3yr') or c.get('rev_growth_yoy')
        gap     = c.get('growth_gap')

        dcf_rows = [
            ['METRIC', 'VALUE', 'INTERPRETATION'],
            ['Market-Implied Growth Rate',
             fmt_pct(implied),
             'Annual revenue CAGR required to justify current EV'],
            ['3-Year Historical CAGR',
             fmt_pct(hist),
             'Actual growth company has delivered'],
            ['Expectation Gap',
             f"+{gap*100:.0f}pp" if gap and gap > 0 else (fmt_pct(gap) if gap else '—'),
             'Market expects this much MORE than history supports'],
        ]

        dcf_tbl = Table(dcf_rows, colWidths=[1.9*inch, 1.0*inch, 3.8*inch])
        dcf_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0),  NAVY),
            ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
            ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',      (0,0), (-1,-1), 8),
            ('TEXTCOLOR',     (0,1), (-1,-1), NAVY),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LGRAY]),
            ('GRID',          (0,0), (-1,-1), 0.3, MGRAY),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ('RIGHTPADDING',  (0,0), (-1,-1), 6),
            ('FONTNAME',      (1,3), (1,3),   'Helvetica-Bold'),
            ('TEXTCOLOR',     (1,3), (1,3),   RED),
        ]))
        story.append(dcf_tbl)
        story.append(Spacer(1, 0.1*inch))

        # Sentiment
        story.append(Paragraph('MANAGEMENT SENTIMENT TREND', S['section_header']))
        sent_label = c.get('latest_sentiment_label', '—')
        sent_trend = c.get('sentiment_trend')
        trend_str  = ('DETERIORATING ↓' if sent_trend and sent_trend < -0.05
                      else 'IMPROVING ↑' if sent_trend and sent_trend > 0.05
                      else 'STABLE →')
        trend_col  = RED if 'DETERIORATING' in trend_str else (GREEN if 'IMPROVING' in trend_str else DGRAY)

        sent_data = [
            ['LATEST FILING TONE', 'TREND', 'SCORE'],
            [sent_label, trend_str, f'{c.get("avg_sentiment") or 0:.3f}'],
        ]
        s_tbl = Table(sent_data, colWidths=[2.2*inch, 2.2*inch, 2.3*inch])
        s_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0),  NAVY),
            ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
            ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTNAME',      (0,1), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,-1), 8),
            ('TEXTCOLOR',     (0,1), (0,1),
             RED if sent_label == 'NEGATIVE' else (GREEN if sent_label == 'POSITIVE' else DGRAY)),
            ('TEXTCOLOR',     (1,1), (1,1),   trend_col),
            ('GRID',          (0,0), (-1,-1), 0.3, MGRAY),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('BACKGROUND',    (0,1), (-1,1),  LGRAY),
        ]))
        story.append(s_tbl)
        story.append(Spacer(1, 0.12*inch))

        # Investment thesis
        story.append(Paragraph('ACTIVIST INVESTMENT THESIS', S['section_header']))
        thesis = c.get('thesis', '')
        thesis_tbl = Table(
            [[Paragraph(thesis, S['thesis'])]],
            colWidths=[7.2*inch]
        )
        thesis_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#fef9f0')),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ('RIGHTPADDING',  (0,0), (-1,-1), 10),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('BOX',           (0,0), (-1,-1), 1, AMBER),
        ]))
        story.append(thesis_tbl)

        # Footer
        story.append(Spacer(1, 0.15*inch))
        story.append(HRFlowable(width='100%', thickness=0.5, color=MGRAY))
        story.append(Paragraph(
            f'Activist Vulnerability Screen  ·  Yash Bhagat  ·  Round Rock High School  ·  {today}  ·  '
            f'github.com/yashvijaybhagat-lab/ib-research-terminal',
            S['footer']
        ))

        if c != top_companies[-1]:
            story.append(PageBreak())

    # Final disclaimer
    story.append(PageBreak())
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(
        'DISCLAIMER',
        ParagraphStyle('disc_h', fontName='Helvetica-Bold', fontSize=9,
                       textColor=NAVY, alignment=TA_CENTER, spaceAfter=8)
    ))
    story.append(Paragraph(
        'This document is produced for academic and portfolio purposes only. '
        'It does not constitute investment advice, a solicitation to buy or sell securities, '
        'or a recommendation to engage in any activist campaign. '
        'All data sourced from public filings (SEC EDGAR) and publicly available market data. '
        'Past performance of activist campaigns does not guarantee future results. '
        'The author holds no position in any of the securities mentioned.',
        S['disclaimer']
    ))

    doc.build(story)
    print(f"Tearsheet saved: {output_path}")
    return output_path


if __name__ == '__main__':
    # Test with dummy data
    test_companies = [{
        'name': 'TestCo Inc.', 'ticker': 'TEST',
        'industry': 'Application Software',
        'market_cap': 2.1e9, 'enterprise_value': 2.3e9,
        'revenue_ttm': 280e6, 'ebitda_ttm': -14e6,
        'gross_margin': 0.71, 'op_margin': -0.05,
        'ev_revenue': 8.2, 'ev_ebitda': None,
        'rev_growth_yoy': 0.14, 'hist_rev_growth_3yr': 0.12,
        'implied_growth_rate': 0.31, 'growth_gap': 0.19,
        'vulnerability_score': 74, 'vulnerability_label': 'HIGH',
        'latest_sentiment_label': 'NEGATIVE',
        'avg_sentiment': -0.12, 'sentiment_trend': -0.18,
        'thesis': 'TestCo trades at 8.2x trailing revenue, implying 31% annual revenue CAGR over seven years against a 12% historical track record. Management tone has deteriorated across the last three quarters. The combination of valuation stretch and defensive language creates conditions for activist intervention.',
    }]
    build_tearsheet(test_companies, pd.DataFrame(test_companies))

import pandas as pd
