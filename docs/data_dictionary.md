# Data dictionary

Fill this in during notebook 01. One row per column that later notebooks use.

## data/processed/prices.csv
| Column | Meaning | Unit | Source |
|---|---|---|---|
| IREN, peers, ETFs | Adjusted close on IREN trading days | USD | Yahoo Finance via yfinance |
| BTC-USD | Bitcoin close, aligned to IREN trading days | USD | Yahoo Finance |
| ^VIX | CBOE volatility index | index points | Yahoo Finance |

## data/processed/risk_free.csv
| Column | Meaning | Unit | Source |
|---|---|---|---|
| ust10y | 10-year Treasury yield (DGS10) | decimal p.a. | FRED |
| tbill3m | 3-month T-bill (DTB3) | decimal p.a. | FRED |
| rf_daily | tbill3m / 252 | decimal per day | derived |

## data/processed/fundamentals_quarterly.csv
| Column | XBRL concept used | Unit | Notes |
|---|---|---|---|
| revenue | TODO | USD | |
| net_income | TODO | USD | |
| … | | | |

## data/manual/kpis.csv
| Column | Meaning | Unit |
|---|---|---|
| fiscal_q | IREN fiscal quarter (FY ends 30 June; Q1 = Jul–Sep) | label |
| *_usdm | Amounts in US$ millions | USD m |
| *_usdbn | Amounts in US$ billions | USD bn |
| ai_segment_gross_margin | AI cloud segment gross margin (non-GAAP, before D&A) | decimal |
| contracted_arr_usdbn / operating_arr_usdbn | Company-defined annualised run-rate revenue (not GAAP) | USD bn |
| operating_mw_ai / operating_mw_btc | Operating capacity by use | MW |

## Reconciliation notes
Record every difference between EDGAR and the press releases, and why it exists.
