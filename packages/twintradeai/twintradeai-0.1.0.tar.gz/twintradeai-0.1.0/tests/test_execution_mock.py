from twintradeai import execution


def test_execute_order_buy_mock():
    result = execution.execute_order("XAUUSDc", "BUY", lot=0.1,
                                     entry=100, sl=99, tp1=101, tp2=102, tp3=103)
    assert result["success"] is True
    assert len(result["orders"]) > 0


def test_execute_order_sell_mock():
    result = execution.execute_order("BTCUSDc", "SELL", lot=0.2,
                                     entry=200, sl=205, tp1=195, tp2=190, tp3=185)
    assert result["success"] is True
    assert len(result["orders"]) > 0
