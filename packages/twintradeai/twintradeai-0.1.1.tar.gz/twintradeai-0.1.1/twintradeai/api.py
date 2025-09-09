import os
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from twintradeai.engine import build_signal, get_tf_data, load_symbol_cfg
from twintradeai.risk_guard import RiskGuard
from twintradeai.execution import execute_order
import MetaTrader5 as mt5
from datetime import datetime
import zmq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [API][%(levelname)s] %(message)s"
)

app = FastAPI(title="TwinTradeAi API", version="1.1")

# === Global state ===
SYM_CFG = load_symbol_cfg()
risk_guard = RiskGuard()
ENGINE_STATUS_FILE = "engine_status.json"
RISK_STATUS_FILE = "risk_guard_status.json"

# === ZMQ Publisher setup ===
ZMQ_PUB_URL = os.getenv("ZMQ_PUB_URL", "tcp://*:7000")
ZMQ_TOPIC = os.getenv("ZMQ_TOPIC", "signals")
ZMQ_MODE = os.getenv("ZMQ_MODE", "bind")

zmq_ctx = zmq.Context()
zmq_pub = zmq_ctx.socket(zmq.PUB)

@app.on_event("startup")
async def startup_event():
    if ZMQ_MODE == "bind":
        try:
            zmq_pub.bind(ZMQ_PUB_URL)
            logging.info(f"[ZMQ] Publisher started at {ZMQ_PUB_URL} (mode=bind, topic={ZMQ_TOPIC})")
        except Exception as e:
            logging.error(f"[ZMQ] Failed to bind {ZMQ_PUB_URL}: {e}")
    else:
        zmq_pub.connect(ZMQ_PUB_URL)
        logging.info(f"[ZMQ] Publisher connected to {ZMQ_PUB_URL} (mode=connect, topic={ZMQ_TOPIC})")


# === Endpoints ===
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/signals")
async def signals():
    try:
        if os.path.exists(ENGINE_STATUS_FILE):
            with open(ENGINE_STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                publish_signal(data)
                return {"status": "ok", "data": data}
        return {"status": "error", "error": "No engine_status.json"}
    except Exception as e:
        logging.error(f"[API] signals error: {e}")
        return {"status": "error", "error": str(e)}


@app.get("/risk")
async def risk():
    try:
        return {"status": "ok", "data": risk_guard.get_status()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/risk_status")
async def risk_status():
    """อ่าน risk_guard_status.json โดยตรง"""
    try:
        if os.path.exists(RISK_STATUS_FILE):
            with open(RISK_STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {"status": "ok", "data": data}
        return {"status": "error", "error": "No risk_guard_status.json"}
    except Exception as e:
        logging.error(f"[API] risk_status error: {e}")
        return {"status": "error", "error": str(e)}


@app.post("/execute")
async def execute(request: Request):
    """
    Manual execution endpoint
    mode=signal → แค่ publish signal ผ่าน ZMQ
    mode=trade  → ส่ง order จริงด้วย execute_order
    """
    try:
        body = await request.json()
        symbol = body.get("symbol")
        decision = body.get("decision")
        lot = float(body.get("lot", 0.01))
        mode = body.get("mode", "signal")  # ✅ default=signal

        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return {"status": "error", "error": f"No tick for {symbol}"}

        m5 = get_tf_data(symbol, mt5.TIMEFRAME_M5)
        h1 = get_tf_data(symbol, mt5.TIMEFRAME_H1)
        h4 = get_tf_data(symbol, mt5.TIMEFRAME_H4)
        if not all([m5, h1, h4]):
            return {"status": "error", "error": "Indicators not available"}

        cfg = SYM_CFG.get(symbol, {})
        sig = build_signal(symbol, tick, m5, h1, h4, cfg=cfg, lot=lot)

        allowed, reasons, metrics = risk_guard.check(symbol, sig["atr"], sig.get("spread_pts"))
        if not allowed:
            return {"status": "blocked", "reasons": reasons, "metrics": metrics}

        if mode == "signal":
            publish_signal({"timestamp": datetime.utcnow().isoformat(), "signals": [sig]})
            return {"status": "ok", "mode": "signal", "signal": sig, "metrics": metrics}

        elif mode == "trade":
            if sig["final_decision"] in ("BUY", "SELL"):
                result = execute_order(
                    symbol, sig["final_decision"], lot,
                    sig["entry"], sig["sl"], sig["tp1"], sig["tp2"], sig["tp3"]
                )
                publish_signal({"timestamp": datetime.utcnow().isoformat(), "signals": [sig]})
                return {"status": "executed", "mode": "trade", "signal": sig, "result": str(result), "metrics": metrics}
            else:
                return {"status": "hold", "mode": "trade", "signal": sig, "metrics": metrics}

        else:
            return {"status": "error", "error": f"Unknown mode {mode}"}

    except Exception as e:
        logging.error(f"[API] execute error: {e}")
        return {"status": "error", "error": str(e)}
