import os
import tempfile

from fastapi.testclient import TestClient


class TestDashboardAPI:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.tmp.close()
        self.db_path = self.tmp.name

        from alpaca_training.config import DB_PATH as orig_path
        import alpaca_training.config as cfg
        self._orig_db_path = cfg.DB_PATH
        cfg.DB_PATH = self.db_path

        from alpaca_training.db import init_db, log_trade, update_position, log_risk_decision, save_daily_snapshot
        init_db(self.db_path)
        log_trade(self.db_path, "strat1", "AAPL", "BUY", 50, 150.0)
        update_position(self.db_path, "strat1", "AAPL", 50, 150.0, 155.0, 250.0)
        log_risk_decision(self.db_path, "strat1", "trade_allowed", "within_limits")
        save_daily_snapshot(self.db_path, "2026-05-09", 250.0, 1, "strat1")

        from alpaca_training.dashboard.server import app
        self.client = TestClient(app)

    def teardown_method(self):
        import alpaca_training.config as cfg
        cfg.DB_PATH = self._orig_db_path
        try:
            os.unlink(self.db_path)
        except (OSError, PermissionError):
            pass

    def test_get_positions(self):
        response = self.client.get("/api/positions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"

    def test_get_trades(self):
        response = self.client.get("/api/trades")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"

    def test_get_pnl(self):
        response = self.client.get("/api/pnl")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["total_pnl"] == 250.0

    def test_get_risk_log(self):
        response = self.client.get("/api/risk-log")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_strategies(self):
        response = self.client.get("/api/strategies")
        assert response.status_code == 200
