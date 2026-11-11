# IREN equity analysis: performance, financial health and growth potential

> Can financial data, operating metrics and quantitative analysis tell us how IREN (NASDAQ: IREN) is performing, how healthy its finances are and how much it can grow? And what is the investment recommendation?

**Status:** 🚧 in progress · **As-of date:** 10 Nov 2026 close · **Author:** Hong Hai Pham

## Executive summary

*(Written last, from notebook 09.)* One paragraph covering the recommendation, its value range, the three findings that drive it, and the main risk.

| Recommendation | Value per share (bear / base / bull) | Probability-weighted value | Price at as-of date | Expected return |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

## Why IREN?

IREN is changing from a Bitcoin miner into an AI cloud provider. AI cloud was about 88% of revenue in fiscal Q1 FY27 (Jul–Sep 2026), and the company has a $20.3bn revenue backlog led by a ~$9.7bn Microsoft contract. It also reports GAAP losses, plans ~$15bn of capex with $6bn still unfunded, and its stock has a beta around 4. That mix makes it a strong test case for quantitative methods: structural breaks, fat tails, volatility clustering and a valuation that depends on execution.

## Research design

| Sub-question | Notebook | Methods |
|---|---|---|
| Q1 Is the pivot showing up in revenue, margins and unit economics? | 03 | Ratio analysis, revenue per MW, ARR conversion |
| Q2 Can IREN fund its build-out without hurting shareholders? | 03 | Liquidity, leverage, coverage, Altman Z'', convertible dilution |
| Q3 What drives the stock and how risky is it? | 04, 05, 06 | OLS + HAC, Chow test, ridge/lasso + time-series CV, ARIMA-GARCH, VaR/ES + backtests, event study |
| Q4 What is a share worth? | 07, 08 | Driver-based forecast, DCF, Monte Carlo, peer multiples |

**Hypotheses:** H1 the link to Bitcoin weakened after the pivot · H2 the link to AI-infrastructure stocks strengthened · H3 contracts, results and raises produce abnormal returns · H4 returns have fat tails and clustered volatility, so a normal VaR understates risk.

**Decision rule (fixed before the analysis):** Buy if the probability-weighted 12-month expected return is above +25%, the bear-case value is at least 50% of the price and the cash runway is at least 4 quarters. Sell if it is below −10%. Otherwise Hold.

## Repository structure

```
├── notebooks/        01_data_collection … 09_recommendation (run in order)
├── src/iren/         reusable code: config, data loaders, metrics, risk, plotting
├── data/
│   ├── raw/          API downloads (git-ignored; rebuilt by notebook 01)
│   ├── processed/    clean CSVs used by notebooks 02-09
│   └── manual/       hand-collected KPIs, convertible notes, event dates (with sources)
├── docs/             data dictionary, notes
└── reports/figures/  charts saved by the notebooks
```

## How to reproduce

```bash
git clone https://github.com/<your-username>/iren-equity-analysis.git
cd iren-equity-analysis
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

1. Put your name and email in `SEC_USER_AGENT` in `src/iren/config.py` (the SEC requires it).
2. Open the folder in VS Code, choose the `.venv` kernel, and run the notebooks in order.

## Data sources

Yahoo Finance (prices) · SEC EDGAR XBRL API (financial statements) · FRED (Treasury yields) · Kenneth French Data Library (factors) · IREN quarterly results releases and 10-K/10-Q filings (operating KPIs, debt terms). Every hand-collected row has a `source_url`.

## Disclaimer

This is an academic project, not investment advice.
