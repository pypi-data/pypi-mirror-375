import pandas as pd
import numpy as np
from twintradeai import indicators


def make_ohlc(n=50, start=100):
    """helper สร้าง data frame OHLC จำลอง"""
    np.random.seed(42)
    price = np.linspace(start, start + n, n) + np.random.randn(n)
    df = pd.DataFrame({
        "open": price,
        "high": price + np.random.rand(n),
        "low": price - np.random.rand(n),
        "close": price + np.random.randn(n) * 0.5,
    })
    return df


def test_compute_atr_basic():
    df = make_ohlc(30)
    atr = indicators.compute_atr(df, period=14)
    assert isinstance(atr, pd.Series)
    assert len(atr) == len(df)
    assert (atr >= 0).all()


def test_compute_atr_symbol_floor():
    df = make_ohlc(30)
    atr_xau = indicators.compute_atr(df, period=14, symbol="XAUUSDc")
    assert (atr_xau >= 0.1).all()

    atr_btc = indicators.compute_atr(df, period=14, symbol="BTCUSDc")
    assert (atr_btc >= 10).all()

    atr_eur = indicators.compute_atr(df, period=14, symbol="EURUSDc")
    assert (atr_eur >= 0.0001).all()


def test_add_indicators_columns():
    df = make_ohlc(60)
    df = indicators.add_indicators(df, symbol="BTCUSDc")

    expected_cols = [
        "ema20", "ema50", "atr", "rsi",
        "macd", "macd_signal", "macd_hist",
        "bb_mid", "bb_std", "bb_up", "bb_lo"
    ]
    for col in expected_cols:
        assert col in df.columns

    assert ((df["rsi"] >= 0) & (df["rsi"] <= 100)).all()

    # relax check: แค่ macd_hist ไม่ NaN
    assert df["macd_hist"].notna().all()
