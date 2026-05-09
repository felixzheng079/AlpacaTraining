import sqlite3
from datetime import datetime, timezone


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str):
    conn = _connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS positions (
            strategy TEXT NOT NULL,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            avg_price REAL NOT NULL,
            current_price REAL NOT NULL DEFAULT 0.0,
            pnl REAL NOT NULL DEFAULT 0.0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            PRIMARY KEY (strategy, symbol)
        );

        CREATE TABLE IF NOT EXISTS risk_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            strategy TEXT NOT NULL,
            decision TEXT NOT NULL,
            reason TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_snapshots (
            date TEXT PRIMARY KEY,
            total_pnl REAL NOT NULL DEFAULT 0.0,
            num_trades INTEGER NOT NULL DEFAULT 0,
            strategies_active TEXT NOT NULL DEFAULT ''
        );
    """)
    conn.commit()
    conn.close()


def log_trade(db_path: str, strategy: str, symbol: str, side: str, quantity: int, price: float):
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO trades (strategy, symbol, side, quantity, price) VALUES (?, ?, ?, ?, ?)",
        (strategy, symbol, side, quantity, price),
    )
    conn.commit()
    conn.close()


def get_trades(db_path: str, limit: int = 100):
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, strategy, symbol, side, quantity, price, timestamp FROM trades ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def update_position(db_path: str, strategy: str, symbol: str, quantity: int, avg_price: float, current_price: float, pnl: float):
    conn = _connect(db_path)
    conn.execute(
        """
        INSERT INTO positions (strategy, symbol, quantity, avg_price, current_price, pnl, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(strategy, symbol) DO UPDATE SET
            quantity = excluded.quantity,
            avg_price = excluded.avg_price,
            current_price = excluded.current_price,
            pnl = excluded.pnl,
            updated_at = datetime('now')
        """,
        (strategy, symbol, quantity, avg_price, current_price, pnl),
    )
    conn.commit()
    conn.close()


def get_positions(db_path: str):
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT strategy, symbol, quantity, avg_price, current_price, pnl FROM positions WHERE quantity > 0"
    ).fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def log_risk_decision(db_path: str, strategy: str, decision: str, reason: str):
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO risk_log (strategy, decision, reason) VALUES (?, ?, ?)",
        (strategy, decision, reason),
    )
    conn.commit()
    conn.close()


def get_risk_log(db_path: str, limit: int = 100):
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, timestamp, strategy, decision, reason FROM risk_log ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def save_daily_snapshot(db_path: str, date: str, total_pnl: float, num_trades: int, strategies_active: str):
    conn = _connect(db_path)
    conn.execute(
        """
        INSERT INTO daily_snapshots (date, total_pnl, num_trades, strategies_active)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            total_pnl = excluded.total_pnl,
            num_trades = excluded.num_trades,
            strategies_active = excluded.strategies_active
        """,
        (date, total_pnl, num_trades, strategies_active),
    )
    conn.commit()
    conn.close()


def get_daily_snapshots(db_path: str, limit: int = 30):
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT date, total_pnl, num_trades, strategies_active FROM daily_snapshots ORDER BY date DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [tuple(r) for r in rows]
