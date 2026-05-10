import logging

from lumibot.strategies.strategy import Strategy

from alpaca_training.config import DB_PATH
from alpaca_training.db import log_trade, update_position, log_risk_decision

logger = logging.getLogger(__name__)


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

        logger.info(f"{symbol} price=${price:.2f} short_sma={short_sma:.2f} long_sma={long_sma:.2f} position={position_qty}")

        if short_sma > long_sma and position_qty == 0:
            risk_mgr = self.parameters.get("risk_manager")
            if risk_mgr:
                qty = risk_mgr.check(self.portfolio_value, symbol, price, "BUY")
            else:
                qty = 10

            if qty > 0:
                logger.info(f"BUY SIGNAL: {symbol} x{qty} @ ${price:.2f}")
                order = self.create_order(symbol, qty, "buy")
                self.submit_order(order)
                log_trade(DB_PATH, self.__class__.__name__, symbol, "BUY", qty, price)
                update_position(
                    DB_PATH, self.__class__.__name__, symbol, qty, price, price, 0.0
                )
            elif risk_mgr:
                logger.warning(f"BUY REJECTED by risk manager (qty={qty})")
                log_risk_decision(
                    DB_PATH, self.__class__.__name__, "buy_rejected", "risk_manager"
                )

        elif short_sma < long_sma and position_qty > 0:
            logger.info(f"SELL SIGNAL: {symbol} x{position_qty} @ ${price:.2f}")
            self.sell_all()
            log_trade(DB_PATH, self.__class__.__name__, symbol, "SELL", position_qty, price)
            update_position(DB_PATH, self.__class__.__name__, symbol, 0, 0.0, 0.0, 0.0)

    def on_filled_order(self, position, order, price, quantity, multiplier):
        symbol = order.symbol if order else position.asset
        strategy_name = self.__class__.__name__
        pnl = position.unrealized_profit_loss if position and hasattr(position, 'unrealized_profit_loss') else 0.0
        qty = int(position.quantity) if position else quantity
        avg_price = position.avg_fill_price if position and hasattr(position, 'avg_fill_price') else price
        logger.info(f"FILLED: {symbol} x{qty} @ ${price:.2f} avg=${avg_price:.2f} P&L=${pnl:.2f}")
        update_position(
            DB_PATH, strategy_name, symbol, qty, avg_price, price, pnl
        )
