# =========================
# General model settings
# =========================

TICKER = "AAPL"
PERIOD = "5y"

FEATURES = [
    "Return",
    "SMA_10",
    "SMA_50",
    "Volatility",
    "RSI",
    "MACD",
    "Signal",
]

MODEL_DIR = "Models"
REPORT_DIR = "Reports"
DATA_DIR = "Data"


# =========================
# Data files
# =========================

NASDAQ_SYMBOLS_PATH = "Data/nasdaq100_latest_symbols.csv"
SP500_SYMBOLS_PATH = "Data/sp500_Historical_Data.csv"

MARKET_SIGNALS_PATH = "Reports/market_signals.csv"
TRADE_LOG_PATH = "Reports/trade_log.csv"


# =========================
# Account / risk settings
# =========================

PAPER = True

ACCOUNT_EQUITY = 10000
RISK_PER_TRADE = 0.01
MAX_LEVERAGE = 1.0
MAX_TRADES_PER_DAY = 3


# =========================
# Entry rules
# =========================

MIN_ENTRY_SCORE = 5
MIN_RETURN_20D = 0.03

MIN_RSI = 45
MAX_RSI = 68

MAX_VOLATILITY = 0.06


# =========================
# Exit rules
# =========================

STOP_PERCENT = 0.03
ATR_MULTIPLIER = 2.0
REWARD_RISK_RATIO = 2.0