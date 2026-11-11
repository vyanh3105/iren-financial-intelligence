"""Value-at-Risk, Expected Shortfall and VaR backtests.

Convention: returns are decimals; VaR and ES are reported as POSITIVE loss
numbers (VaR = 0.08 means "lose more than 8% on 1 day in 20" at 95%).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def var_historical(r: pd.Series, alpha: float = 0.95) -> float:
    return float(-np.quantile(r.dropna(), 1 - alpha))


def var_normal(r: pd.Series, alpha: float = 0.95) -> float:
    r = r.dropna()
    return float(-(r.mean() + r.std(ddof=1) * stats.norm.ppf(1 - alpha)))


def var_cornish_fisher(r: pd.Series, alpha: float = 0.95) -> float:
    """Normal VaR with the quantile adjusted for skewness (S) and excess kurtosis (K)."""
    r = r.dropna()
    z = stats.norm.ppf(1 - alpha)
    s, k = stats.skew(r), stats.kurtosis(r)  # kurtosis() is already excess
    z_cf = (z + (z**2 - 1) * s / 6 + (z**3 - 3 * z) * k / 24
            - (2 * z**3 - 5 * z) * s**2 / 36)
    return float(-(r.mean() + r.std(ddof=1) * z_cf))


def es_historical(r: pd.Series, alpha: float = 0.95) -> float:
    """Expected Shortfall: average loss on the days worse than VaR."""
    r = r.dropna()
    cutoff = np.quantile(r, 1 - alpha)
    return float(-r[r <= cutoff].mean())


def var_table(r: pd.Series, alphas=(0.95, 0.99)) -> pd.DataFrame:
    """Compare the unconditional methods side by side."""
    rows = {}
    for a in alphas:
        rows[f"{int(a*100)}%"] = {
            "historical": var_historical(r, a),
            "normal": var_normal(r, a),
            "cornish_fisher": var_cornish_fisher(r, a),
            "ES_historical": es_historical(r, a),
        }
    return pd.DataFrame(rows).T


# ----------------------------------------------------------------------------
# Backtests
# ----------------------------------------------------------------------------
def kupiec_pof(violations: pd.Series, alpha: float = 0.95) -> dict:
    """Kupiec (1995) proportion-of-failures test.

    H0: the violation rate equals 1 - alpha. Small p-value -> VaR model rejected.
    violations: boolean Series, True when the realised loss exceeded VaR.
    """
    v = violations.dropna().astype(bool)
    n, x = len(v), int(v.sum())
    p = 1 - alpha
    phat = x / n if n else np.nan
    # log-likelihoods; guard log(0)
    ll0 = (n - x) * np.log(1 - p) + x * np.log(p)
    ll1 = ((n - x) * np.log(1 - phat) if phat < 1 else 0) + (x * np.log(phat) if phat > 0 else 0)
    lr = max(-2 * (ll0 - ll1), 0.0)  # clamp tiny negative rounding error
    return {"n": n, "violations": x, "expected": n * p, "rate": phat,
            "LR_pof": lr, "p_value": 1 - stats.chi2.cdf(lr, df=1)}


def christoffersen_independence(violations: pd.Series) -> dict:
    """Christoffersen (1998) test that violations do not cluster.

    H0: today's violation is independent of yesterday's.
    """
    v = violations.dropna().astype(int).to_numpy()
    prev, curr = v[:-1], v[1:]
    n00 = np.sum((prev == 0) & (curr == 0)); n01 = np.sum((prev == 0) & (curr == 1))
    n10 = np.sum((prev == 1) & (curr == 0)); n11 = np.sum((prev == 1) & (curr == 1))
    pi0 = n01 / (n00 + n01) if (n00 + n01) else 0
    pi1 = n11 / (n10 + n11) if (n10 + n11) else 0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)

    def _ll(a, b, p):
        return (a * np.log(1 - p) if p < 1 else 0) + (b * np.log(p) if p > 0 else 0)

    lr = max(-2 * (_ll(n00 + n10, n01 + n11, pi) - (_ll(n00, n01, pi0) + _ll(n10, n11, pi1))), 0.0)
    return {"n01": int(n01), "n11": int(n11), "LR_ind": lr,
            "p_value": 1 - stats.chi2.cdf(lr, df=1)}
