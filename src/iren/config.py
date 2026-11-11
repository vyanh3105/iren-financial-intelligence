"""Project-wide settings: dates, tickers, paths.

Change values HERE, never inside notebooks, so every notebook uses the same
inputs. Commit any change with a message that explains why (e.g.
"chore: move as-of date to 2026-11-10 close").
"""
from pathlib import Path

# --- Paths -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_MANUAL = ROOT / "data" / "manual"
FIGURES = ROOT / "reports" / "figures"

# --- Dates -------------------------------------------------------------------
START = "2021-11-17"          # IREN Nasdaq listing (IPO) date
AS_OF = "2026-11-10"          # freeze date: all data is pulled up to this close
PIVOT_DATE = "2025-11-03"     # Microsoft ~$9.7bn AI cloud contract announced
FISCAL_YEAR_END_MONTH = 6     # IREN fiscal year ends 30 June (Q1 = Jul-Sep)

# --- Tickers -----------------------------------------------------------------
TARGET = "IREN"
BTC = "BTC-USD"
MARKET = ["QQQ", "SPY", "SMH", "^VIX"]
PEERS_AI_CLOUD = ["CRWV", "NBIS", "APLD"]          # neoclouds / AI data centres
PEERS_PIVOT_MINERS = ["CIFR", "WULF", "CORZ", "HUT"]  # miners pivoting to AI/HPC
PEERS_PURE_MINERS = ["MARA", "RIOT", "CLSK"]          # mostly Bitcoin mining
PEERS = PEERS_AI_CLOUD + PEERS_PIVOT_MINERS + PEERS_PURE_MINERS
ALL_TICKERS = [TARGET, BTC] + MARKET + PEERS

# FRED series (daily, percent): 10-year Treasury yield, 3-month T-bill
FRED_SERIES = {"DGS10": "ust10y", "DTB3": "tbill3m"}

# --- SEC EDGAR ---------------------------------------------------------------
IREN_CIK = "0001878848"
# The SEC requires a User-Agent with your name and email. Put your own here
# (it is sent only to sec.gov). Example: "Jane Doe jane@example.com"
SEC_USER_AGENT = "YOUR NAME your_email@example.com"

TRADING_DAYS = 252
