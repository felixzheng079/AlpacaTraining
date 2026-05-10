from lumibot.strategies.strategy import Strategy


class SMACrossover(Strategy):
    parameters = {
        "symbol": "SPY",
        "short_window": 10,
        "long_window": 30,
    }

    def initialize(self):
        self.sleeptime = "1H"
        self.vars.signal = None

    def on_trading_iteration(self):
        symbol = self.parameters["symbol"]
        short_w = self.parameters["short_window"]
        long_w = self.parameters["long_window"]

        bars = self.get_historical_prices(symbol, length=long_w + 1, timestep="hour")
        if bars is None or len(bars.df) < long_w + 1:
            return

        df = bars.df
        short_sma = df["close"].rolling(window=short_w).mean().iloc[-1]
        long_sma = df["close"].rolling(window=long_w).mean().iloc[-1]

        positions = self.get_position(symbol)
        position_qty = int(positions.quantity) if positions else 0
        price = self.get_last_price(symbol)

        if short_sma > long_sma and position_qty == 0:
            qty = self.parameters.get("risk_manager").check(
                self.portfolio_value, symbol, price, "BUY"
            ) if self.parameters.get("risk_manager") else 10
            if qty > 0:
                self.buy(symbol, qty)

        elif short_sma < long_sma and position_qty > 0:
            self.sell_all()
