# tests/test_config.py
import os
import importlib
from alpaca_training import config


class TestConfig:
    def test_defaults_when_no_env_vars(self, monkeypatch):
        monkeypatch.delenv("ALPACA_API_KEY", raising=False)
        monkeypatch.delenv("ALPACA_API_SECRET", raising=False)
        monkeypatch.delenv("ALPACA_MODE", raising=False)
        monkeypatch.delenv("MAX_POSITION_SIZE_PCT", raising=False)
        monkeypatch.delenv("MAX_CONCURRENT_POSITIONS", raising=False)
        monkeypatch.delenv("DAILY_STOP_LOSS_PCT", raising=False)
        monkeypatch.delenv("DASHBOARD_PORT", raising=False)
        monkeypatch.delenv("DB_PATH", raising=False)

        reloaded = importlib.reload(config)
        assert reloaded.ALPACA_API_KEY == ""
        assert reloaded.ALPACA_API_SECRET == ""
        assert reloaded.ALPACA_MODE == "paper"
        assert reloaded.MAX_POSITION_SIZE_PCT == 0.10
        assert reloaded.MAX_CONCURRENT_POSITIONS == 5
        assert reloaded.DAILY_STOP_LOSS_PCT == -0.05
        assert reloaded.DASHBOARD_PORT == 8000
        assert reloaded.DB_PATH.endswith("alpaca_training.db")

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("ALPACA_API_KEY", "test-key")
        monkeypatch.setenv("ALPACA_API_SECRET", "test-secret")
        monkeypatch.setenv("ALPACA_MODE", "live")
        monkeypatch.setenv("MAX_POSITION_SIZE_PCT", "0.15")
        monkeypatch.setenv("MAX_CONCURRENT_POSITIONS", "3")
        monkeypatch.setenv("DAILY_STOP_LOSS_PCT", "-0.10")
        monkeypatch.setenv("DASHBOARD_PORT", "9999")
        monkeypatch.setenv("DB_PATH", "/tmp/test.db")

        reloaded = importlib.reload(config)
        assert reloaded.ALPACA_API_KEY == "test-key"
        assert reloaded.ALPACA_API_SECRET == "test-secret"
        assert reloaded.ALPACA_MODE == "live"
        assert reloaded.MAX_POSITION_SIZE_PCT == 0.15
        assert reloaded.MAX_CONCURRENT_POSITIONS == 3
        assert reloaded.DAILY_STOP_LOSS_PCT == -0.10
        assert reloaded.DASHBOARD_PORT == 9999
        assert reloaded.DB_PATH == "/tmp/test.db"

    def test_alpaca_config_returns_dict(self):
        cfg = config.get_alpaca_config()
        assert "API_KEY" in cfg
        assert "API_SECRET" in cfg
        assert "PAPER" in cfg

    def test_risk_params_returns_dict(self):
        params = config.get_risk_params()
        assert "max_position_size_pct" in params
        assert "max_concurrent_positions" in params
        assert "daily_stop_loss_pct" in params
