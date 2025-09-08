import logging
import time
import os
import MetaTrader5 as mt5

# ========= Load from env =========
DEVIATION_POINTS = int(os.getenv("DEVIATION_POINTS", "50"))
ORDER_MAGIC = int(os.getenv("ORDER_MAGIC", "123456"))
ORDER_FILLING = getattr(mt5, os.getenv("ORDER_FILLING", "ORDER_FILLING_IOC"))
ORDER_MAX_RETRIES = int(os.getenv("ORDER_MAX_RETRIES", "3"))
ORDER_RETRY_SLEEP = float(os.getenv("ORDER_RETRY_SLEEP", "0.25"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [EXEC][%(levelname)s] %(message)s"
)


# ========= Helpers =========
def round_to_point(symbol, price):
    """ปรับราคาให้ตรงกับจำนวนทศนิยมของ symbol"""
    try:
        info = mt5.symbol_info(symbol)
        if not info:
            return float(price)
        p = info.point
        return round(round(float(price) / p) * p, info.digits)
    except Exception as e:
        logging.error(f"[EXEC] round_to_point error: {e}")
        return float(price)


def has_open_position(symbol, decision):
    """ตรวจสอบว่า symbol มี position เดิมอยู่หรือไม่"""
    try:
        positions = mt5.positions_get(symbol=symbol)
        if not positions:
            return False
        for pos in positions:
            if pos.type == mt5.POSITION_TYPE_BUY and decision == "BUY":
                return True
            if pos.type == mt5.POSITION_TYPE_SELL and decision == "SELL":
                return True
        return False
    except Exception as e:
        logging.error(f"[EXEC] has_open_position error: {e}")
        return False


# ========= Execution =========
def execute_order(symbol, decision, lot, entry, sl, tp1, tp2, tp3, ratios=(0.5, 0.3, 0.2)):
    """
    เปิดออเดอร์ 3 ไม้ (TP1, TP2, TP3)
    - รองรับ partial lot
    - duplicate check
    - retry mechanism
    """
    info = mt5.symbol_info(symbol)
    if not info:
        logging.error(f"[EXEC] {symbol} not found in MT5")
        return {"success": False, "orders": [], "reason": "Symbol not found"}

    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logging.error(f"[EXEC] No tick for {symbol}")
        return {"success": False, "orders": [], "reason": "No tick"}

    if decision == "BUY":
        price = tick.ask
        order_type = mt5.ORDER_TYPE_BUY
    elif decision == "SELL":
        price = tick.bid
        order_type = mt5.ORDER_TYPE_SELL
    else:
        return {"success": False, "orders": [], "reason": f"Invalid decision {decision}"}

    # Duplicate check
    if has_open_position(symbol, decision):
        logging.warning(f"[EXEC] Duplicate {decision} blocked for {symbol}")
        return {"success": False, "orders": [], "reason": "Duplicate position blocked"}

    # Round numbers
    price = round_to_point(symbol, price)
    sl = round_to_point(symbol, sl) if sl else None
    tp1 = round_to_point(symbol, tp1) if tp1 else None
    tp2 = round_to_point(symbol, tp2) if tp2 else None
    tp3 = round_to_point(symbol, tp3) if tp3 else None

    results, success = [], True

    for tp, tag, ratio in [(tp1, "TP1", ratios[0]), (tp2, "TP2", ratios[1]), (tp3, "TP3", ratios[2])]:
        if not tp or ratio <= 0:
            continue

        volume = round(lot * ratio, 2)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": DEVIATION_POINTS,
            "magic": ORDER_MAGIC,
            "comment": f"TwinTradeAi {tag}",
            "type_filling": ORDER_FILLING,
        }

        result = None
        for attempt in range(ORDER_MAX_RETRIES):
            result = mt5.order_send(request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                break
            logging.warning(
                f"[EXEC RETRY] {symbol} {decision} {tag} attempt {attempt+1}/{ORDER_MAX_RETRIES} "
                f"retcode={result.retcode if result else 'N/A'}"
            )
            time.sleep(ORDER_RETRY_SLEEP)

        if not result:
            logging.error(f"[EXEC FAIL] {symbol} {decision} {tag} - no response")
            success = False
        elif result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(
                f"[EXEC FAIL] {symbol} {decision} {tag} lot={volume} entry={price} sl={sl} tp={tp} "
                f"retcode={result.retcode} comment={getattr(result, 'comment', None)}"
            )
            success = False
        else:
            logging.info(
                f"[EXEC OK] {symbol} {decision} {tag} lot={volume} entry={price} sl={sl} tp={tp} "
                f"order_id={result.order} deal_id={result.deal}"
            )
        results.append(result)

    return {"success": success, "orders": results}
