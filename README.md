# Alpaca Training

Pluggable automated trading system for practicing quantitative trading with Alpaca.

## Setup

```bash
pip install -e ".[dev]"
```

Set environment variables:

```bash
export ALPACA_API_KEY="your-paper-key"
export ALPACA_API_SECRET="your-paper-secret"
```

## Usage

```bash
# List available strategies
alpaca-training list

# Run a strategy in paper trading mode
alpaca-training run SMACrossover

# Backtest a strategy
alpaca-training backtest SMACrossover --from 2024-01-01 --to 2024-12-31

# Pause or resume a running strategy
alpaca-training pause SMACrossover
alpaca-training resume SMACrossover

# Check status
alpaca-training status

# Start web dashboard
alpaca-training dashboard
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `ALPACA_API_KEY` | (required) | Alpaca API key |
| `ALPACA_API_SECRET` | (required) | Alpaca API secret |
| `ALPACA_MODE` | `paper` | `paper` or `live` |
| `MAX_POSITION_SIZE_PCT` | `0.10` | Max % of portfolio per trade |
| `MAX_CONCURRENT_POSITIONS` | `5` | Max open positions at once |
| `DAILY_STOP_LOSS_PCT` | `-0.05` | Daily P&L floor (-5%) |
| `DASHBOARD_PORT` | `8000` | Dashboard web port |
| `DB_PATH` | auto | SQLite database path |

## Adding a Strategy

Create a file in `alpaca_training/strategies/`:

```python
from lumibot.strategies.strategy import Strategy

class MyStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1H"

    def on_trading_iteration(self):
        # Your trading logic here
        pass
```

The CLI auto-discovers all Strategy subclasses in that directory.
