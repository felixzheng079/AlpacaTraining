# alpaca_training/config.py
import os

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET", "")
ALPACA_MODE = os.getenv("ALPACA_MODE", "paper")

MAX_POSITION_SIZE_PCT = float(os.getenv("MAX_POSITION_SIZE_PCT", "0.10"))
MAX_CONCURRENT_POSITIONS = int(os.getenv("MAX_CONCURRENT_POSITIONS", "5"))
DAILY_STOP_LOSS_PCT = float(os.getenv("DAILY_STOP_LOSS_PCT", "-0.05"))

DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8000"))
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "alpaca_training.db"))


def get_alpaca_config():
    return {
        "API_KEY": ALPACA_API_KEY,
        "API_SECRET": ALPACA_API_SECRET,
        "PAPER": ALPACA_MODE != "live",
    }


def get_risk_params():
    return {
        "max_position_size_pct": MAX_POSITION_SIZE_PCT,
        "max_concurrent_positions": MAX_CONCURRENT_POSITIONS,
        "daily_stop_loss_pct": DAILY_STOP_LOSS_PCT,
    }
