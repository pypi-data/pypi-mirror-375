import pandas as pd
import numpy as np
import logging

# ================== ATR ==================
def compute_atr(df: pd.DataFrame, period: int = 14, symbol: str = None) -> pd.Series:
    """คำนวณ ATR (Wilder's EMA) พร้อม safe fallback"""
    try:
        prev_close = df["close"].shift(1)
        tr = pd.concat([
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs()
        ], axis=1).max(axis=1)

        atr = tr.ewm(alpha=1/period, min_periods=period).mean()

        # Replace invalids
        atr = atr.replace([np.inf, -np.inf], np.nan).fillna(method="ffill").fillna(method="bfill")

        # Symbol-specific safety floor
        if symbol:
            if "XAU" in symbol:   # Gold
                atr = atr.clip(lower=0.1)
            elif "BTC" in symbol:  # Crypto
                atr = atr.clip(lower=10.0)
            elif "EUR" in symbol or "USD" in symbol:  # Forex majors
                atr = atr.clip(lower=0.0001)

        return atr

    except Exception as e:
        logging.error(f"[ATR] calc error: {e}")
        return pd.Series([1.0] * len(df), index=df.index)  # safe default


# ================== Indicators ==================
def add_indicators(df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
    """เพิ่ม indicators หลัก พร้อม safe fallback"""
    try:
        # EMA
        df["ema20"] = df["close"].ewm(span=20, min_periods=20).mean()
        df["ema50"] = df["close"].ewm(span=50, min_periods=50).mean()

        # ATR (safe)
        df["atr"] = compute_atr(df, 14, symbol=symbol)

        # RSI (safe)
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        df["rsi"] = rsi.replace([np.inf, -np.inf], np.nan).fillna(50).clip(0, 100)

        # MACD (safe)
        ema12 = df["close"].ewm(span=12, min_periods=12).mean()
        ema26 = df["close"].ewm(span=26, min_periods=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, min_periods=9).mean()
        df["macd"] = macd.fillna(0)
        df["macd_signal"] = signal.fillna(0)
        df["macd_hist"] = (macd - signal).fillna(0)

        # Bollinger Bands (safe)
        df["bb_mid"] = df["close"].rolling(20, min_periods=20).mean()
        df["bb_std"] = df["close"].rolling(20, min_periods=20).std().fillna(0.0)
        df["bb_up"] = df["bb_mid"] + 2 * df["bb_std"]
        df["bb_lo"] = df["bb_mid"] - 2 * df["bb_std"]

        return df

    except Exception as e:
        logging.error(f"[INDICATORS] error: {e}")
        return df

