import os
import tempfile
from alpaca_training.db import init_db, log_trade, log_risk_decision, get_trades, get_positions, get_risk_log, update_position, get_daily_snapshots, save_daily_snapshot


class TestDatabase:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.tmp.close()
        self.db_path = self.tmp.name

    def teardown_method(self):
        os.unlink(self.db_path)

    def test_init_db_creates_tables(self):
        init_db(self.db_path)
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        assert "trades" in table_names
        assert "positions" in table_names
        assert "risk_log" in table_names
        assert "daily_snapshots" in table_names
        conn.close()

    def test_log_trade_and_get_trades(self):
        init_db(self.db_path)
        log_trade(self.db_path, "my_strategy", "AAPL", "BUY", 50, 150.0)
        log_trade(self.db_path, "my_strategy", "GOOG", "SELL", 10, 140.0)
        trades = get_trades(self.db_path)
        assert len(trades) == 2
        assert trades[0][1] == "my_strategy"
        assert trades[0][2] == "GOOG"
        assert trades[1][1] == "my_strategy"
        assert trades[1][2] == "AAPL"

    def test_update_position_and_get_positions(self):
        init_db(self.db_path)
        update_position(self.db_path, "my_strategy", "AAPL", 100, 150.0, 155.0, 500.0)
        positions = get_positions(self.db_path)
        assert len(positions) == 1
        assert positions[0][0] == "my_strategy"
        assert positions[0][1] == "AAPL"
        assert positions[0][2] == 100

    def test_log_risk_decision_and_get_risk_log(self):
        init_db(self.db_path)
        log_risk_decision(self.db_path, "my_strategy", "buy_rejected", "max_positions")
        log_risk_decision(self.db_path, "my_strategy", "sell_allowed", "within_limits")
        entries = get_risk_log(self.db_path)
        assert len(entries) == 2

    def test_save_and_get_daily_snapshots(self):
        init_db(self.db_path)
        save_daily_snapshot(self.db_path, "2026-05-09", 1500.0, 12, "active")
        snapshots = get_daily_snapshots(self.db_path)
        assert len(snapshots) == 1
        assert snapshots[0][0] == "2026-05-09"
        assert snapshots[0][1] == 1500.0
