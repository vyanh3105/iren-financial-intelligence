"""Data loaders. Every function returns a tidy pandas object and never prints.

Sources
-------
- Yahoo Finance via `yfinance`  -> prices
- FRED CSV endpoint             -> risk-free rates
- Ken French data library       -> Fama-French 5 factors + momentum
- SEC EDGAR XBRL API            -> reported financial statement facts
"""
from __future__ import annotations

import io
import time
import zipfile

import pandas as pd
import requests

from . import config


# ----------------------------------------------------------------------------
# Prices
# ----------------------------------------------------------------------------
def download_prices(tickers: list[str], start: str = config.START,
                    end: str = config.AS_OF) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Download adjusted close prices and volumes.

    Returns (close, volume), each a wide DataFrame (dates x tickers).
    `end` is inclusive: one day is added because yfinance treats it as exclusive.
    """
    import yfinance as yf

    end_excl = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    raw = yf.download(tickers, start=start, end=end_excl, auto_adjust=True,
                      progress=False, group_by="column", threads=True)
    close = raw["Close"].copy()
    volume = raw["Volume"].copy()
    close.index = pd.to_datetime(close.index).tz_localize(None)
    volume.index = close.index
    return close.sort_index(), volume.sort_index()


def align_to_trading_days(prices: pd.DataFrame, anchor: str = config.TARGET) -> pd.DataFrame:
    """Keep only days when the anchor stock traded.

    BTC trades 7 days a week; using the stock's calendar means a Monday BTC
    return covers Fri->Mon, matching the stock's Monday return.
    """
    days = prices[anchor].dropna().index
    return prices.reindex(days).ffill(limit=3)


# ----------------------------------------------------------------------------
# Risk-free rate (FRED)
# ----------------------------------------------------------------------------
def fetch_fred(series: dict[str, str] = config.FRED_SERIES, start: str = config.START,
               end: str = config.AS_OF) -> pd.DataFrame:
    """Download FRED series as decimals (4.25% -> 0.0425)."""
    frames = []
    for code, name in series.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}"
        df = pd.read_csv(url, na_values=".")
        df.columns = ["date", name]
        df["date"] = pd.to_datetime(df["date"])
        frames.append(df.set_index("date"))
    out = pd.concat(frames, axis=1).loc[start:end] / 100.0
    return out.ffill()


# ----------------------------------------------------------------------------
# Fama-French factors
# ----------------------------------------------------------------------------
_FF_BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
_FF_FILES = {
    "ff5": "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip",
    "mom": "F-F_Momentum_Factor_daily_CSV.zip",
}


def _read_french_zip(url: str) -> pd.DataFrame:
    """Parse a Ken French daily CSV: skip text header, stop at first blank row."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip()[:8].isdigit()) - 1
    body = []
    for line in lines[start:]:
        if body and not line.strip():
            break
        body.append(line)
    df = pd.read_csv(io.StringIO("\n".join(body)), index_col=0)
    df.index = pd.to_datetime(df.index.astype(str).str.strip(), format="%Y%m%d")
    df.columns = [c.strip() for c in df.columns]
    return df.apply(pd.to_numeric, errors="coerce") / 100.0  # percent -> decimal


def fetch_fama_french(start: str = config.START, end: str = config.AS_OF) -> pd.DataFrame:
    """Daily Mkt-RF, SMB, HML, RMW, CMA, RF and Mom (decimals).

    Note: the library is updated with a lag of 1-2 months, so the last weeks
    before AS_OF may be missing. That is normal - say so in the notebook.
    """
    ff5 = _read_french_zip(_FF_BASE + _FF_FILES["ff5"])
    mom = _read_french_zip(_FF_BASE + _FF_FILES["mom"])
    mom.columns = ["Mom"]
    return ff5.join(mom, how="left").loc[start:end]


# ----------------------------------------------------------------------------
# SEC EDGAR XBRL
# ----------------------------------------------------------------------------
def fetch_companyfacts(cik: str = config.IREN_CIK,
                       user_agent: str = config.SEC_USER_AGENT) -> dict:
    """Raw JSON of every XBRL fact the company has filed."""
    if "example.com" in user_agent:
        raise ValueError("Set SEC_USER_AGENT in src/iren/config.py to your name + email first.")
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    resp = requests.get(url, headers={"User-Agent": user_agent}, timeout=60)
    resp.raise_for_status()
    time.sleep(0.2)  # SEC fair-access: max 10 requests/second
    return resp.json()


def companyfacts_to_long(facts: dict) -> pd.DataFrame:
    """Flatten companyfacts JSON into one row per (concept, period, filing).

    Both taxonomies are kept: `us-gaap` (10-K/10-Q era) and `ifrs-full`
    (earlier 20-F/6-K era), so you can see where the labels change.
    """
    rows = []
    for taxonomy, concepts in facts.get("facts", {}).items():
        for concept, payload in concepts.items():
            label = payload.get("label")
            for unit, items in payload.get("units", {}).items():
                for it in items:
                    rows.append({
                        "taxonomy": taxonomy, "concept": concept, "label": label,
                        "unit": unit, "value": it.get("val"),
                        "start": it.get("start"), "end": it.get("end"),
                        "fy": it.get("fy"), "fp": it.get("fp"), "form": it.get("form"),
                        "filed": it.get("filed"), "frame": it.get("frame"),
                    })
    df = pd.DataFrame(rows)
    for c in ["start", "end", "filed"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df["days"] = (df["end"] - df["start"]).dt.days
    return df


def quarterly_series(long: pd.DataFrame, concept: str, kind: str = "flow") -> pd.Series:
    """Pick one value per fiscal quarter for a concept.

    kind="instant" -> balance-sheet items: no start date, value at `end`.
    kind="flow"    -> income / cash-flow items. 10-Qs often report cash flows
                      year-to-date (3, 6, 9 months) and the 10-K a full year,
                      so a missing 3-month value is derived by subtraction:
                      Q2 = 6M YTD - 3M, Q4 = 12M - 9M YTD.
    The latest filing wins when a number was restated.
    """
    d = long[long["concept"] == concept]
    if kind == "instant":
        d = d[d["start"].isna()].sort_values("filed").drop_duplicates("end", keep="last")
        s = d.set_index("end")["value"].sort_index()
        s.name = concept
        return s

    d = d[d["days"].between(80, 370)]
    d = d.sort_values("filed").drop_duplicates(["start", "end"], keep="last")
    quarters = {r.end: r.value for r in d[d["days"].between(80, 100)].itertuples()}
    # Derive the rest from cumulative (YTD) values sharing one fiscal-year start date
    for _, g in d.groupby("start"):
        g = g.sort_values("end")
        prev_end, prev_val = None, None
        for r in g.itertuples():
            if prev_end is not None and r.end not in quarters:
                gap = (r.end - prev_end).days
                if 80 <= gap <= 100:
                    quarters[r.end] = r.value - prev_val
            prev_end, prev_val = r.end, r.value
    s = pd.Series(quarters, name=concept, dtype="float64").sort_index()
    return s


def first_available(long: pd.DataFrame, candidates: list[str], kind: str = "flow") -> pd.Series:
    """Try several XBRL concept names (companies change labels over time) and
    combine them: earlier names fill gaps left by later ones."""
    out = pd.Series(dtype="float64")
    for concept in candidates:
        s = quarterly_series(long, concept, kind)
        if not s.empty:
            out = s if out.empty else out.combine_first(s)
    return out


def fiscal_quarter_label(date: pd.Timestamp) -> str:
    """Map a quarter-end date to IREN's fiscal label (FY ends 30 June).

    2026-09-30 -> 'FY27Q1', 2026-06-30 -> 'FY26Q4'.
    """
    fy = date.year + 1 if date.month > config.FISCAL_YEAR_END_MONTH else date.year
    q = ((date.month - config.FISCAL_YEAR_END_MONTH - 1) % 12) // 3 + 1
    return f"FY{str(fy)[-2:]}Q{q}"
