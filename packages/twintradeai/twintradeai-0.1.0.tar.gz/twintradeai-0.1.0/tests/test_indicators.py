import pandas as pd
from twintradeai import indicators


def make_dummy_df(n=30):
    data = {
        "open": [100 + i for i in range(n)],
        "high": [101 + i for i in range(n)],
        "low": [99 + i for i in range(n)],
        "close": [100 + i for i in range(n)],
    }
    return pd.DataFrame(data)


def test_add_indicators_has_columns():
    df = make_dummy_df(50)
    df = indicators.add_indicators(df, symbol="XAUUSDc")

    for col in ["ema20", "ema50", "atr", "rsi", "macd", "macd_signal", "bb_mid", "bb_up", "bb_lo"]:
        assert col in df.columns
