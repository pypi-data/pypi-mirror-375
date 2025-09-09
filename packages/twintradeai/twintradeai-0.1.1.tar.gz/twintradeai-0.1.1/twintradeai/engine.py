import os
import yaml
import logging
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd

from twintradeai.indicators import add_indicators
from twintradeai.risk_guard import RiskGuard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ENGINE][%(levelname)s] %(message)s"
)

CONFIG_FILE = "config.symbols.yaml"

# ========= Load symbol config =========
def load_symbol_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logging.error(f"[ENGINE] load_symbol_cfg error: {e}")
            return {}
    return {}

SYM_CFG = load_symbol_cfg()

# ========= Init RiskGuard =========
risk_guard = RiskGuard()

# ========= Helpers =========
def round_to_point(symbol, price: float):
    try:
        info = mt5.symbol_info(symbol)
        if not info:
            return float(price)
        p = info.point
        return round(round(float(price) / p) * p, info.digits)
    except Exception:
        return float(price)

# ========= Candle Patterns =========
def bullish_engulfing(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    a, b = df.iloc[-2], df.iloc[-1]
    return (a["close"] < a["open"]) and (b["close"] > b["open"]) and (b["close"] >= a["open"]) and (b["open"] <= a["close"])

def bearish_engulfing(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    a, b = df.iloc[-2], df.iloc[-1]
    return (a["close"] > a["open"]) and (b["close"] < b["open"]) and (b["close"] <= a["open"]) and (b["open"] >= a["close"])

def hammer_like(row):
    rng = row["high"] - row["low"]
    if rng <= 0:
        return False, False
    body = abs(row["close"] - row["open"])
    lower = min(row["open"], row["close"]) - row["low"]
    upper = row["high"] - max(row["open"], row["close"])
    bullish = (lower > 2 * body) and (upper < body) and (row["close"] >= row["low"] + 0.7 * rng)
    bearish = (upper > 2 * body) and (lower < body) and (row["close"] <= row["low"] + 0.3 * rng)
    return bullish, bearish

# ========= BOS Detection =========
def detect_bos(df: pd.DataFrame, swing_bars: int = 20):
    """ตรวจสอบ Break of Structure (BOS) จาก swing high/low"""
    recent_high = df["high"].iloc[-swing_bars:].max()
    recent_low = df["low"].iloc[-swing_bars:].min()
    close = df["close"].iloc[-1]
    if close > recent_high:
        return "BOS_UP"
    elif close < recent_low:
        return "BOS_DOWN"
    return None

# ========= Get timeframe data =========
def get_tf_data(symbol: str, timeframe, bars: int = 200):
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        if rates is None or len(rates) < 50:
            logging.warning(f"[ENGINE] Not enough bars for {symbol} tf={timeframe}")
            return None
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = add_indicators(df, symbol)
        return df
    except Exception as e:
        logging.error(f"[ENGINE] get_tf_data error {symbol}: {e}")
        return None

# ========= Confidence & Reversal Helpers =========
def compute_confidence(cfg, checks_passed):
    """คำนวณ confidence score 0–100"""
    enabled = cfg.get("enabled_strategies", {})
    weights = cfg.get("confidence_weights", {})

    score, total = 0.0, 0.0
    for strat, passed in checks_passed.items():
        if not enabled.get(strat, False):
            continue
        w = float(weights.get(strat, 1.0))
        total += w
        if passed:
            score += w

    if total == 0:
        return 0.0
    return round(100 * score / total, 2)

def check_reversal(m5: pd.DataFrame, cfg: dict) -> (str, float, list):
    """ตรวจสอบ reversal signal คืนค่า (direction, score, reasons)"""
    rev_cfg = cfg.get("rev", {})
    reasons = []
    score = 0.0
    direction = None

    last = m5.iloc[-1]
    atr = float(m5["atr"].iloc[-1])

    # --- RSI extreme ---
    rsi_val = last["rsi"]
    if rsi_val >= rev_cfg.get("rsi_ob", 70):
        score += rev_cfg.get("weights", {}).get("rsi_extreme", 0.6)
        reasons.append(f"RSI overbought {rsi_val:.2f}")
        direction = "SELL"
    elif rsi_val <= rev_cfg.get("rsi_os", 30):
        score += rev_cfg.get("weights", {}).get("rsi_extreme", 0.6)
        reasons.append(f"RSI oversold {rsi_val:.2f}")
        direction = "BUY"

    # --- BB extreme ---
    if "bb_up" in last and last["close"] >= last["bb_up"]:
        score += rev_cfg.get("weights", {}).get("bb", 0.8)
        reasons.append("Close near BB upper")
        direction = "SELL"
    elif "bb_lo" in last and last["close"] <= last["bb_lo"]:
        score += rev_cfg.get("weights", {}).get("bb", 0.8)
        reasons.append("Close near BB lower")
        direction = "BUY"

    # --- Distance from EMA ---
    if "ema20" in last:
        dist = abs(last["close"] - last["ema20"])
        if dist >= rev_cfg.get("dist_ema_k_atr", 2.0) * atr:
            score += rev_cfg.get("weights", {}).get("dist_ema", 0.6)
            reasons.append(f"Price far from EMA20 ({dist:.2f})")
            direction = "SELL" if last["close"] > last["ema20"] else "BUY"

    # --- Divergence check (RSI/MACD) ---
    div_lookback = rev_cfg.get("div_lookback", 60)
    lookback = min(div_lookback, len(m5))
    if lookback >= 3:
        recent = m5.iloc[-lookback:]

        price_first, price_last = recent["close"].iloc[0], recent["close"].iloc[-1]
        rsi_first, rsi_last = recent["rsi"].iloc[0], recent["rsi"].iloc[-1]
        macd_first, macd_last = recent["macd"].iloc[0], recent["macd"].iloc[-1]

        # RSI divergence
        if price_last > price_first and rsi_last < rsi_first:
            score += rev_cfg.get("weights", {}).get("div", 1.3)
            reasons.append("Bearish RSI divergence")
            direction = "SELL"
        elif price_last < price_first and rsi_last > rsi_first:
            score += rev_cfg.get("weights", {}).get("div", 1.3)
            reasons.append("Bullish RSI divergence")
            direction = "BUY"

        # MACD divergence
        if price_last > price_first and macd_last < macd_first:
            score += rev_cfg.get("weights", {}).get("div", 1.3)
            reasons.append("Bearish MACD divergence")
            direction = "SELL"
        elif price_last < price_first and macd_last > macd_first:
            score += rev_cfg.get("weights", {}).get("div", 1.3)
            reasons.append("Bullish MACD divergence")
            direction = "BUY"

    return direction, score, reasons

# ========= Build trading signal =========
def build_signal(symbol, tick, m5, h1, h4, cfg=None, lot=0.01, risk_guard: RiskGuard = None):
    cfg = cfg or SYM_CFG.get(symbol, {})
    reasons = []
    decision = "HOLD"
# ... imports
# ... ฟังก์ชันอื่นๆ เช่น get_tf_data, build_signal


# ========= Pattern Detection =========

def is_bullish_engulfing(candles):
    """
    ตรวจ Bullish Engulfing:
    - candle[-2] = แท่งแดง (open > close)
    - candle[-1] = แท่งเขียว (close > open)
    - body ของแท่งล่าสุดครอบ body ของแท่งก่อนหน้า
    """
    if len(candles) < 2:
        return False
    prev, curr = candles[-2], candles[-1]

    # red → green
    if prev["open"] <= prev["close"]:
        return False
    if curr["close"] <= curr["open"]:
        return False

    return (curr["open"] < prev["close"]) and (curr["close"] > prev["open"])


def is_bearish_engulfing(candles):
    """
    ตรวจ Bearish Engulfing:
    - candle[-2] = เขียว
    - candle[-1] = แดง
    - body ล่าสุดครอบ body ก่อนหน้า
    """
    if len(candles) < 2:
        return False
    prev, curr = candles[-2], candles[-1]

    if prev["close"] <= prev["open"]:
        return False
    if curr["close"] >= curr["open"]:
        return False

    return (curr["open"] > prev["close"]) and (curr["close"] < prev["open"])


def is_hammer(candle):
    """
    ตรวจ Hammer:
    - lower shadow ยาว ≥ 2 เท่าของ body
    - upper shadow สั้น
    """
    body = abs(candle["close"] - candle["open"])
    upper_shadow = candle["high"] - max(candle["close"], candle["open"])
    lower_shadow = min(candle["close"], candle["open"]) - candle["low"]

    if body == 0:
        return False
    return (lower_shadow >= 2 * body) and (upper_shadow <= body)


def is_inverted_hammer(candle):
    """
    ตรวจ Inverted Hammer:
    - upper shadow ยาว ≥ 2 เท่าของ body
    - lower shadow สั้น
    """
    body = abs(candle["close"] - candle["open"])
    upper_shadow = candle["high"] - max(candle["close"], candle["open"])
    lower_shadow = min(candle["close"], candle["open"]) - candle["low"]

    if body == 0:
        return False
    return (upper_shadow >= 2 * body) and (lower_shadow <= body)


    # === Tracking strategies ===
    checks = {"ema": False, "macd": False, "rsi": False, "bb": False, "reversal": False}

    # === Base EMA decision ===
    if m5["ema20"].iloc[-1] > m5["ema50"].iloc[-1]:
        decision = "BUY"; reasons.append("EMA20>EMA50 base trend BUY"); checks["ema"] = True
    elif m5["ema20"].iloc[-1] < m5["ema50"].iloc[-1]:
        decision = "SELL"; reasons.append("EMA20<EMA50 base trend SELL"); checks["ema"] = True

    # === BB confirm ===
    if decision == "BUY" and m5["close"].iloc[-1] < m5["bb_mid"].iloc[-1]:
        reasons.append("BB not confirm BUY"); decision = "HOLD"
    elif decision == "SELL" and m5["close"].iloc[-1] > m5["bb_mid"].iloc[-1]:
        reasons.append("BB not confirm SELL"); decision = "HOLD"
    else:
        checks["bb"] = True

    # === MACD confirm ===
    if decision == "BUY" and m5["macd"].iloc[-1] <= m5["macd_signal"].iloc[-1]:
        reasons.append("MACD not confirm BUY"); decision = "HOLD"
    elif decision == "SELL" and m5["macd"].iloc[-1] >= m5["macd_signal"].iloc[-1]:
        reasons.append("MACD not confirm SELL"); decision = "HOLD"
    else:
        checks["macd"] = True

    # === RSI flat zone ===
    rlo, rhi = cfg.get("rsi_flat", [45, 55])
    if rlo < m5["rsi"].iloc[-1] < rhi:
        reasons.append("RSI flat zone"); decision = "SIDEWAY"
    else:
        checks["rsi"] = True

    # === ATR too low check ===
    atr_val = float(m5["atr"].iloc[-1])
    mid = (tick.ask + tick.bid) / 2.0
    min_atr_ratio = cfg.get("min_atr_ratio", 0.0005)
    atr_floor = cfg.get("atr_floor", 0.0)
    if atr_val < min_atr_ratio * mid or atr_val < atr_floor:
        reasons.append("ATR too low"); decision = "SIDEWAY"

    # === Multi-timeframe confirm ===
    if decision in ("BUY", "SELL"):
        c1 = "BUY" if h1["ema20"].iloc[-1] > h1["ema50"].iloc[-1] else "SELL"
        c2 = "BUY" if h4["ema20"].iloc[-1] > h4["ema50"].iloc[-1] else "SELL"
        reasons.append(f"MTF confirm H1={c1}, H4={c2}")
        if not (c1 == decision and c2 == decision):
            decision = "HOLD"

    # === BOS confirm ===
    bos = detect_bos(m5, cfg.get("swing_bars", 20))
    if decision == "BUY" and bos != "BOS_UP":
        reasons.append("No BOS confirm"); decision = "HOLD"
    elif decision == "SELL" and bos != "BOS_DOWN":
        reasons.append("No BOS confirm"); decision = "HOLD"

    # === Candle patterns filter ===
    if bullish_engulfing(m5) and decision == "SELL":
        decision = "HOLD"; reasons.append("Block SELL")
    if bearish_engulfing(m5) and decision == "BUY":
        decision = "HOLD"; reasons.append("Block BUY")
    hb, hs = hammer_like(m5.iloc[-1])
    if hb and decision == "SELL": decision = "HOLD"; reasons.append("hammer")
    if hs and decision == "BUY": decision = "HOLD"; reasons.append("shooting star")

    # === Reversal strategy ===
    rev_dir, rev_score, rev_reasons = check_reversal(m5, cfg)
    if rev_dir and cfg.get("enable_reversal", False):
        if rev_score >= cfg.get("reversal_min_score", 2.0):
            checks["reversal"] = True
            reasons.extend(rev_reasons)
            if decision == "HOLD" and cfg.get("prefer_reversal_when_hold", False):
                decision = rev_dir
                reasons.append(f"Reversal used → {rev_dir} (score {rev_score:.2f})")


    # === Confidence ===
    confidence = compute_confidence(cfg, checks)

    # === SL/TP calculation ===
    atr = float(m5["atr"].iloc[-1])
    entry = sl = tp1 = tp2 = tp3 = None
    if decision in ("BUY", "SELL"):
        entry = tick.ask if decision == "BUY" else tick.bid
        sl_mult = cfg.get("sl_atr", 2.0)
        tp_mults = cfg.get("tp_atr", [1.0, 2.0, 3.0])
        swing_bars = cfg.get("swing_bars", 20)
        recent_low = m5["low"].iloc[-swing_bars:].min()
        recent_high = m5["high"].iloc[-swing_bars:].max()

        if decision == "BUY":
            sl_atr = entry - atr * sl_mult
            sl = min(sl_atr, recent_low)
            tps = [entry + atr * m for m in tp_mults]
            tps[0] = max(tps[0], recent_high)
        else:
            sl_atr = entry + atr * sl_mult
            sl = max(sl_atr, recent_high)
            tps = [entry - atr * m for m in tp_mults]
            tps[0] = min(tps[0], recent_low)

        entry = round_to_point(symbol, entry)
        sl = round_to_point(symbol, sl)
        tp1, tp2, tp3 = [round_to_point(symbol, t) for t in tps]

    # === Spread limit check ===
    spread_pts = (tick.ask - tick.bid) / mt5.symbol_info(symbol).point
    spread_limit = risk_guard.get_spread_limit(symbol) if risk_guard else None

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "decision": decision,
        "final_decision": decision,
        "confidence": confidence,
        "reasons": reasons,
        "entry": entry,
        "sl": sl,
        "tp1": tp1, "tp2": tp2, "tp3": tp3,
        "atr": atr,
        "ema20": float(m5["ema20"].iloc[-1]),
        "ema50": float(m5["ema50"].iloc[-1]),
        "rsi": float(m5["rsi"].iloc[-1]),
        "macd": float(m5["macd"].iloc[-1]),
        "macd_signal": float(m5["macd_signal"].iloc[-1]),
        "spread_pts": spread_pts,
        "spread_limit": spread_limit,
        "lot": lot,
    }
