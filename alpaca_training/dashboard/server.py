from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from alpaca_training.config import DB_PATH
from alpaca_training.db import (
    get_positions,
    get_trades,
    get_daily_snapshots,
    get_risk_log,
)
from alpaca_training.strategies import discover_strategies

app = FastAPI(title="Alpaca Training Dashboard")


@app.get("/api/positions")
def api_positions():
    rows = get_positions(DB_PATH)
    return [
        {
            "strategy": r[0],
            "symbol": r[1],
            "quantity": r[2],
            "avg_price": r[3],
            "current_price": r[4],
            "pnl": r[5],
        }
        for r in rows
    ]


@app.get("/api/trades")
def api_trades():
    rows = get_trades(DB_PATH)
    return [
        {
            "id": r[0],
            "strategy": r[1],
            "symbol": r[2],
            "side": r[3],
            "quantity": r[4],
            "price": r[5],
            "timestamp": r[6],
        }
        for r in rows
    ]


@app.get("/api/pnl")
def api_pnl():
    rows = get_daily_snapshots(DB_PATH)
    return [
        {
            "date": r[0],
            "total_pnl": r[1],
            "num_trades": r[2],
            "strategies_active": r[3],
        }
        for r in rows
    ]


@app.get("/api/risk-log")
def api_risk_log():
    rows = get_risk_log(DB_PATH)
    return [
        {
            "id": r[0],
            "timestamp": r[1],
            "strategy": r[2],
            "decision": r[3],
            "reason": r[4],
        }
        for r in rows
    ]


@app.get("/api/strategies")
def api_strategies():
    strategies = discover_strategies()
    return [{"name": s["name"], "module": s["module"]} for s in strategies]


static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Alpaca Training Dashboard"}
