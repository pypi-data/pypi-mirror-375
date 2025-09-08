import logging
import time
import json
from datetime import datetime
import os

import MetaTrader5 as mt5
import zmq

from twintradeai.engine import get_tf_data, build_signal, SYM_CFG
from twintradeai.risk_guard import RiskGuard
from twintradeai.execution import execute_order

# ========= CONFIG =========
SYMBOLS = ["BTCUSDc", "XAUUSDc", "EURUSDc"]
ENGINE_STATUS_FILE = "engine_status.json"

ZMQ_PUB_URL = os.getenv("ZMQ_PUB_URL", "tcp://127.0.0.1:7000")  # ✅ connect to API publisher
ZMQ_TOPIC = os.getenv("ZMQ_TOPIC", "signals")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RUNNER][%(levelname)s] %(message)s"
)


# ========= Helpers =========
def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        logging.error(f"[RUNNER] write_json error: {e}")


def publish_zmq(pub, topic, data):
    try:
        msg = json.dumps(data, ensure_ascii=False, default=str)
        pub.send_string(f"{topic} {msg}")
        logging.info(f"[ZMQ] Published {len(data.get('signals', []))} signals to {topic}")
    except Exception as e:
        logging.error(f"[ZMQ] publish error: {e}")


# ========= MAIN =========
if __name__ == "__main__":
    logging.info("🔧 Booting TwinTradeAi runner (Hybrid config) ...")

    if not mt5.initialize():
        code, msg = mt5.last_error()
        logging.error(f"❌ MT5 initialize failed: code={code}, msg={msg}")
        exit(1)

    risk_guard = RiskGuard()

    # --- setup ZMQ publisher ---
    zmq_ctx = zmq.Context()
    zmq_pub = zmq_ctx.socket(zmq.PUB)
    zmq_pub.connect(ZMQ_PUB_URL)  # ✅ connect to API

    while True:
        all_signals = []
        for sym in SYMBOLS:
            tick = mt5.symbol_info_tick(sym)
            if not tick:
                logging.warning(f"[{sym}] No tick data")
                continue

            # --- get indicators from multiple timeframes ---
            m5 = get_tf_data(sym, mt5.TIMEFRAME_M5)
            h1 = get_tf_data(sym, mt5.TIMEFRAME_H1)
            h4 = get_tf_data(sym, mt5.TIMEFRAME_H4)
            if not (m5 is not None and h1 is not None and h4 is not None):
                continue

            # --- build trading signal ---
            cfg = SYM_CFG.get(sym, {})
            sig = build_signal(sym, tick, m5, h1, h4, cfg=cfg, lot=0.01, risk_guard=risk_guard)

            # --- pretty log ---
            logging.info(
                f"[{sym}] final={sig['final_decision']} "
                f"entry={sig['entry']} sl={sig['sl']} "
                f"tp1={sig['tp1']} tp2={sig['tp2']} tp3={sig['tp3']} "
                f"atr={sig['atr']:.5f} ema20={sig['ema20']:.5f} ema50={sig['ema50']:.5f} "
                f"rsi={sig['rsi']:.2f} spread={sig['spread_pts']:.1f} pts "
                f"(limit={sig['spread_limit']}) reason={','.join(sig['reasons']) if sig.get('reasons') else 'ok'}"
            )

            # --- RiskGuard check ---
            allowed, reasons, metrics = risk_guard.check(
                sym, sig["atr"], sig["spread_pts"], account=mt5.account_info()
            )
            if not allowed:
                logging.warning(f"[RISK BLOCK] {sym} reasons={reasons}")
                sig["final_decision"] = "BLOCKED"
                sig["reasons"].extend(reasons)

            # --- Execute order if allowed ---
            if sig["final_decision"] in ("BUY", "SELL") and allowed:
                execute_order(
                    sym, sig["final_decision"], sig["lot"],
                    sig["entry"], sig["sl"], sig["tp1"], sig["tp2"], sig["tp3"]
                )

            all_signals.append(sig)

        # --- write signals to engine_status.json ---
        engine_status = {
            "last_update": datetime.utcnow().isoformat(),
            "count": len(all_signals),
            "signals": all_signals,
        }
        write_json(ENGINE_STATUS_FILE, engine_status)
        logging.info(f"[RUNNER] Updated {ENGINE_STATUS_FILE} with {len(all_signals)} signals")

        # --- publish via ZMQ ---
        publish_zmq(zmq_pub, ZMQ_TOPIC, engine_status)

        # wait until next cycle
        time.sleep(60)
