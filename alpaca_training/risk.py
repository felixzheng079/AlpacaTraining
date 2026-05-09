class RiskManager:
    def __init__(
        self,
        max_position_size_pct: float = 0.10,
        max_concurrent_positions: int = 5,
        daily_stop_loss_pct: float = -0.05,
    ):
        self.max_position_size_pct = max_position_size_pct
        self.max_concurrent_positions = max_concurrent_positions
        self.daily_stop_loss_pct = daily_stop_loss_pct
        self._positions: dict[str, dict] = {}
        self._daily_pnl: float = 0.0

    def can_trade(self, portfolio_value: float) -> bool:
        if portfolio_value <= 0:
            return False
        pnl_pct = self._daily_pnl / portfolio_value
        return pnl_pct > self.daily_stop_loss_pct

    def calculate_quantity(self, portfolio_value: float, price: float) -> int:
        if price <= 0:
            return 0
        max_investment = portfolio_value * self.max_position_size_pct
        return int(max_investment / price)

    def check(self, portfolio_value: float, symbol: str, price: float, direction: str) -> int:
        if direction == "BUY" and not self.can_trade(portfolio_value):
            return 0

        qty = self.calculate_quantity(portfolio_value, price)
        if qty <= 0:
            return 0

        if direction == "BUY":
            already_held = symbol in self._positions
            if not already_held and len(self._positions) >= self.max_concurrent_positions:
                return 0

        return qty

    def update_position(self, symbol: str, quantity: int, price: float):
        if symbol in self._positions:
            old = self._positions[symbol]
            old_qty = old["quantity"]
            old_price = old["entry_price"]
            new_qty = old_qty + quantity
            if new_qty == 0:
                new_entry = 0.0
            else:
                new_entry = (old_qty * old_price + quantity * price) / new_qty
            self._positions[symbol] = {"quantity": new_qty, "entry_price": new_entry}
        else:
            self._positions[symbol] = {"quantity": quantity, "entry_price": price}

    def update_pnl(self, amount: float):
        self._daily_pnl += amount

    def reset_daily(self):
        self._positions.clear()
        self._daily_pnl = 0.0
