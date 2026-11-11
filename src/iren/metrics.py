"""Return and performance metrics used across notebooks."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import TRADING_DAYS


def log_returns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """r_t = ln(P_t / P_{t-1}). Log returns add up over time, so a 5-day
    return is the sum of five daily ones."""
    return np.log(prices / prices.shift(1)).dropna(how="all")


def simple_returns(prices):
    """R_t = P_t / P_{t-1} - 1. Use these for portfolio weights and VaR in $."""
    return prices.pct_change().dropna(how="all")


def max_drawdown(prices: pd.Series) -> tuple[float, pd.Timestamp, pd.Timestamp]:
    """Largest peak-to-trough fall. Returns (drawdown, peak date, trough date)."""
    p = prices.dropna()
    running_peak = p.cummax()
    dd = p / running_peak - 1
    trough = dd.idxmin()
    peak = p.loc[:trough].idxmax()
    return float(dd.min()), peak, trough


def drawdown_series(prices: pd.Series) -> pd.Series:
    p = prices.dropna()
    return p / p.cummax() - 1


def summary_stats(log_ret: pd.DataFrame, rf_daily: pd.Series | float = 0.0,
                  prices: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per asset: annualised return/vol, Sharpe, Sortino, skew,
    excess kurtosis, max drawdown.

    rf_daily: daily risk-free rate (decimal), a Series aligned to log_ret or a scalar.
    """
    out = {}
    for col in log_ret.columns:
        r = log_ret[col].dropna()
        rf = rf_daily.reindex(r.index).fillna(0) if isinstance(rf_daily, pd.Series) else rf_daily
        ex = r - rf
        ann_ret = r.mean() * TRADING_DAYS
        ann_vol = r.std(ddof=1) * np.sqrt(TRADING_DAYS)
        downside = ex[ex < 0].std(ddof=1) * np.sqrt(TRADING_DAYS)
        row = {
            "obs": len(r),
            "ann_return": ann_ret,
            "ann_vol": ann_vol,
            "sharpe": ex.mean() * TRADING_DAYS / ann_vol if ann_vol > 0 else np.nan,
            "sortino": ex.mean() * TRADING_DAYS / downside if downside > 0 else np.nan,
            "skew": r.skew(),
            "excess_kurtosis": r.kurt(),
        }
        if prices is not None and col in prices:
            row["max_drawdown"] = max_drawdown(prices[col])[0]
        out[col] = row
    return pd.DataFrame(out).T


def rolling_vol(log_ret: pd.Series | pd.DataFrame, window: int = 63):
    """Annualised rolling volatility (63 trading days ~ one quarter)."""
    return log_ret.rolling(window).std() * np.sqrt(TRADING_DAYS)


def rolling_beta(y: pd.Series, x: pd.Series, window: int = 252) -> pd.Series:
    """beta_t = Cov(y, x) / Var(x) over a rolling window."""
    df = pd.concat([y, x], axis=1).dropna()
    cov = df.iloc[:, 0].rolling(window).cov(df.iloc[:, 1])
    var = df.iloc[:, 1].rolling(window).var()
    return (cov / var).rename(f"beta_{y.name}_on_{x.name}")
