from alpaca_training.risk import RiskManager


class TestRiskManager:
    def test_initial_state_allows_trading(self):
        rm = RiskManager()
        assert rm.can_trade(100000.0) is True

    def test_calculate_quantity_default_position_size(self):
        rm = RiskManager(max_position_size_pct=0.10)
        qty = rm.calculate_quantity(portfolio_value=100000.0, price=100.0)
        assert qty == 100

    def test_calculate_quantity_rounds_down(self):
        rm = RiskManager(max_position_size_pct=0.10)
        qty = rm.calculate_quantity(portfolio_value=10000.0, price=30.0)
        assert qty == 33

    def test_calculate_quantity_zero_price(self):
        rm = RiskManager()
        qty = rm.calculate_quantity(portfolio_value=100000.0, price=0.0)
        assert qty == 0

    def test_check_accepts_valid_buy(self):
        rm = RiskManager(max_position_size_pct=0.10, max_concurrent_positions=5)
        qty = rm.check(portfolio_value=100000.0, symbol="AAPL", price=100.0, direction="BUY")
        assert qty == 100

    def test_check_rejects_when_daily_stop_loss_hit(self):
        rm = RiskManager(daily_stop_loss_pct=-0.05)
        rm.update_pnl(-6000.0)
        qty = rm.check(portfolio_value=100000.0, symbol="AAPL", price=100.0, direction="BUY")
        assert qty == 0

    def test_check_rejects_when_max_positions_reached(self):
        rm = RiskManager(max_concurrent_positions=2)
        rm.update_position("AAPL", 100, 150.0)
        rm.update_position("GOOG", 50, 140.0)
        qty = rm.check(portfolio_value=100000.0, symbol="MSFT", price=300.0, direction="BUY")
        assert qty == 0

    def test_check_allows_sell_when_max_positions_reached(self):
        rm = RiskManager(max_concurrent_positions=2)
        rm.update_position("AAPL", 100, 150.0)
        rm.update_position("GOOG", 50, 140.0)
        qty = rm.check(portfolio_value=100000.0, symbol="AAPL", price=150.0, direction="SELL")
        assert qty > 0

    def test_check_allows_entry_at_max_capacity_for_same_symbol(self):
        rm = RiskManager(max_concurrent_positions=2)
        rm.update_position("AAPL", 100, 150.0)
        rm.update_position("GOOG", 50, 140.0)
        qty = rm.check(portfolio_value=100000.0, symbol="AAPL", price=150.0, direction="BUY")
        assert qty > 0

    def test_reset_daily_clears_state(self):
        rm = RiskManager(max_concurrent_positions=3)
        rm.update_position("AAPL", 100, 150.0)
        rm.update_pnl(-5000.0)
        rm.reset_daily()
        assert rm.can_trade(100000.0) is True
        qty = rm.check(portfolio_value=100000.0, symbol="MSFT", price=300.0, direction="BUY")
        assert qty > 0

    def test_update_pnl_accumulates(self):
        rm = RiskManager()
        rm.update_pnl(500.0)
        rm.update_pnl(-200.0)
        assert rm._daily_pnl == 300.0

    def test_update_position_tracks_entry(self):
        rm = RiskManager()
        rm.update_position("AAPL", 100, 150.0)
        assert rm._positions["AAPL"]["quantity"] == 100
        assert rm._positions["AAPL"]["entry_price"] == 150.0
