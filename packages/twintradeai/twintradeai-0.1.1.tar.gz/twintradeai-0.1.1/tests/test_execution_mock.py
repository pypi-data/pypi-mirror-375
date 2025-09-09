import types
from unittest.mock import MagicMock
import twintradeai.execution as execution


class DummyInfo:
    def __init__(self):
        self.point = 0.01
        self.digits = 2


class DummyTick:
    def __init__(self, bid=100.0, ask=100.1):
        self.bid = bid
        self.ask = ask


class DummyOrderResult:
    def __init__(self, retcode=0, order=1, deal=1, comment="ok"):
        self.retcode = retcode
        self.order = order
        self.deal = deal
        self.comment = comment


def test_round_to_point(monkeypatch):
    monkeypatch.setattr(execution, "mt5", types.SimpleNamespace(
        symbol_info=lambda s: DummyInfo()
    ))
    assert execution.round_to_point("BTCUSDc", 100.123) == 100.12


def test_has_open_position(monkeypatch):
    # mock มี BUY position
    class Pos:
        type = execution.mt5.POSITION_TYPE_BUY
    monkeypatch.setattr(execution, "mt5", types.SimpleNamespace(
        positions_get=lambda symbol=None: [Pos()],
        POSITION_TYPE_BUY=0,
        POSITION_TYPE_SELL=1
    ))
    assert execution.has_open_position("BTCUSDc", "BUY") is True
    assert execution.has_open_position("BTCUSDc", "SELL") is False


def test_execute_order_success(monkeypatch):
    dummy_info = DummyInfo()
    dummy_tick = DummyTick()

    # mock mt5 object
    mock_mt5 = types.SimpleNamespace()
    mock_mt5.symbol_info = lambda s: dummy_info
    mock_mt5.symbol_info_tick = lambda s: dummy_tick
    mock_mt5.ORDER_TYPE_BUY = 0
    mock_mt5.ORDER_TYPE_SELL = 1
    mock_mt5.TRADE_ACTION_DEAL = 1
    mock_mt5.TRADE_RETCODE_DONE = 0

    # mock order_send ให้ success
    mock_mt5.order_send = lambda req: DummyOrderResult(retcode=0, order=123, deal=456)

    monkeypatch.setattr(execution, "mt5", mock_mt5)
    monkeypatch.setattr(execution, "has_open_position", lambda s, d: False)

    result = execution.execute_order(
        "BTCUSDc", "BUY", lot=0.1,
        entry=100.1, sl=99.0, tp1=101.0, tp2=102.0, tp3=103.0
    )

    assert result["success"] is True
    assert len(result["orders"]) > 0
    assert isinstance(result["orders"][0], DummyOrderResult)


def test_execute_order_duplicate(monkeypatch):
    dummy_info = DummyInfo()
    dummy_tick = DummyTick()

    mock_mt5 = types.SimpleNamespace()
    mock_mt5.symbol_info = lambda s: dummy_info
    mock_mt5.symbol_info_tick = lambda s: dummy_tick
    mock_mt5.ORDER_TYPE_BUY = 0
    mock_mt5.ORDER_TYPE_SELL = 1
    mock_mt5.TRADE_ACTION_DEAL = 1
    mock_mt5.TRADE_RETCODE_DONE = 0
    mock_mt5.order_send = lambda req: DummyOrderResult(retcode=0)

    monkeypatch.setattr(execution, "mt5", mock_mt5)
    monkeypatch.setattr(execution, "has_open_position", lambda s, d: True)

    result = execution.execute_order(
        "BTCUSDc", "BUY", lot=0.1,
        entry=100.1, sl=99.0, tp1=101.0, tp2=102.0, tp3=103.0
    )

    assert result["success"] is False
    assert "Duplicate" in result["reason"]
