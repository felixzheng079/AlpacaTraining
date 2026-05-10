import subprocess
import sys

import click
from lumibot.brokers import Alpaca
from lumibot.traders import Trader

from alpaca_training import config
from alpaca_training.config import (
    get_alpaca_config,
    get_risk_params,
    DASHBOARD_PORT,
)
from alpaca_training.db import init_db
from alpaca_training.risk import RiskManager
from alpaca_training.strategies import discover_strategies


@click.group()
def cli():
    init_db(config.DB_PATH)


@cli.command()
def list():
    strategies = discover_strategies()
    if not strategies:
        click.echo("No strategies found in strategies/ directory.")
        return
    click.echo("Available strategies:")
    for s in strategies:
        click.echo(f"  - {s['name']} ({s['module']})")


@cli.command()
@click.argument("strategy_name")
def run(strategy_name):
    strategies = discover_strategies()
    match = next((s for s in strategies if s["name"] == strategy_name), None)
    if match is None:
        click.echo(f"Strategy '{strategy_name}' not found. Run 'list' to see available strategies.")
        raise SystemExit(1)

    alpaca_config = get_alpaca_config()
    if not alpaca_config["API_KEY"] or not alpaca_config["API_SECRET"]:
        click.echo("ALPACA_API_KEY and ALPACA_API_SECRET must be set in environment.")
        raise SystemExit(1)

    broker = Alpaca(alpaca_config)
    risk_params = get_risk_params()
    risk_manager = RiskManager(**risk_params)

    strategy_cls = match["cls"]
    strategy = strategy_cls(
        broker=broker,
        parameters={
            "risk_manager": risk_manager,
            "symbol": "SPY",
        },
    )

    trader = Trader()
    trader.add_strategy(strategy)
    click.echo(f"Running strategy '{strategy_name}' in {alpaca_config['PAPER'] and 'paper' or 'live'} mode...")
    trader.run_all()


@cli.command()
@click.argument("strategy_name")
@click.option("--from", "from_date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", required=True, help="End date (YYYY-MM-DD)")
def backtest(strategy_name, from_date, to_date):
    from datetime import datetime
    from lumibot.backtesting import YahooDataBacktesting

    strategies = discover_strategies()
    match = next((s for s in strategies if s["name"] == strategy_name), None)
    if match is None:
        click.echo(f"Strategy '{strategy_name}' not found.")
        raise SystemExit(1)

    click.echo(f"Backtesting '{strategy_name}' from {from_date} to {to_date}...")
    strategy_cls = match["cls"]
    strategy_cls.backtest(
        YahooDataBacktesting,
        datetime.fromisoformat(from_date),
        datetime.fromisoformat(to_date),
        parameters={"symbol": "SPY"},
    )


@cli.command()
@click.argument("strategy_name")
def resume(strategy_name):
    click.echo(f"Resuming strategy '{strategy_name}'...")
    click.echo("Pause/resume is handled via SIGSTOP/SIGCONT. Use 'status' to check current state.")


@cli.command()
@click.argument("strategy_name")
def pause(strategy_name):
    click.echo(f"Pausing strategy '{strategy_name}'...")
    click.echo("Pause/resume is handled via SIGSTOP/SIGCONT. Use 'status' to check current state.")


@cli.command()
def status():
    from alpaca_training.db import get_positions, get_daily_snapshots, get_trades

    positions = get_positions(config.DB_PATH)
    snapshots = get_daily_snapshots(config.DB_PATH, limit=1)
    trades = get_trades(config.DB_PATH, limit=10)

    click.echo("=== Open Positions ===")
    if not positions:
        click.echo("  No open positions.")
    for pos in positions:
        click.echo(f"  {pos[1]}: {pos[2]} shares @ ${pos[3]:.2f} avg, P&L ${pos[5]:.2f}")

    click.echo("\n=== Daily Snapshot ===")
    if snapshots:
        s = snapshots[0]
        click.echo(f"  Date: {s[0]}, P&L: ${s[1]:.2f}, Trades: {s[2]}, Strategies: {s[3]}")

    click.echo("\n=== Recent Trades ===")
    if not trades:
        click.echo("  No recent trades.")
    for t in trades:
        click.echo(f"  {t[6]} | {t[1]} | {t[3]} {t[2]} {t[4]} @ ${t[5]:.2f}")


@cli.command()
def dashboard():
    click.echo(f"Starting dashboard on http://localhost:{DASHBOARD_PORT}")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "alpaca_training.dashboard.server:app", "--host", "0.0.0.0", "--port", str(DASHBOARD_PORT)]
    )
