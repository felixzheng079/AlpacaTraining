import os
import tempfile
from datetime import datetime

import pytest


@pytest.mark.slow
class TestSMACrossoverBacktest:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.tmp.close()
        self.db_path = self.tmp.name

    def teardown_method(self):
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def test_backtest_runs_without_error(self, monkeypatch):
        monkeypatch.setattr("alpaca_training.config.DB_PATH", self.db_path)
        monkeypatch.setattr("alpaca_training.strategies.example_strategy.DB_PATH", self.db_path)

        from alpaca_training.db import init_db, get_trades
        init_db(self.db_path)

        try:
            from lumibot.backtesting import YahooDataBacktesting
        except ImportError:
            pytest.skip("Lumibot not installed")

        from alpaca_training.strategies.example_strategy import SMACrossover

        start = datetime(2024, 10, 1)
        end = datetime(2024, 10, 31)

        SMACrossover.backtest(
            YahooDataBacktesting,
            start,
            end,
            parameters={"symbol": "SPY"},
        )

        trades = get_trades(self.db_path)
        assert len(trades) > 0, "Expected at least one trade from backtest"
