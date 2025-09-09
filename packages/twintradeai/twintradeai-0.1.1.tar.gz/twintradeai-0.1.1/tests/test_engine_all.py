import pytest
import twintradeai.engine as engine


# ------------------------------
# Engulfing pattern tests
# ------------------------------
def test_bullish_engulfing():
    # candle[-2] = red (open > close), candle[-1] = green (open < close) engulfing
    candles = [
        {"open": 105, "close": 100, "high": 106, "low": 99},  # red
        {"open": 99, "close": 110, "high": 111, "low": 98},   # green engulf
    ]
    result = engine.is_bullish_engulfing(candles)
    assert result is True


def test_bearish_engulfing():
    # candle[-2] = green, candle[-1] = red engulfing
    candles = [
        {"open": 100, "close": 110, "high": 112, "low": 99},  # green
        {"open": 111, "close": 95, "high": 112, "low": 94},   # red engulf
    ]
    result = engine.is_bearish_engulfing(candles)
    assert result is True


# ------------------------------
# Hammer pattern tests
# ------------------------------
def test_hammer_pattern_blocks_sell():
    # long lower shadow → hammer
    candle = {"open": 100, "close": 101, "high": 102, "low": 90}
    result = engine.is_hammer(candle)
    assert result is True


def test_hammer_pattern_blocks_buy():
    # inverted hammer → long upper shadow
    candle = {"open": 100, "close": 99, "high": 110, "low": 98}
    result = engine.is_inverted_hammer(candle)
    assert result is True
