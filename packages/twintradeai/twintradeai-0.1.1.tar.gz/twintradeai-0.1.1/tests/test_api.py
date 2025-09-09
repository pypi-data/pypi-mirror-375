import json
import pytest
import twintradeai.runner as runner


@pytest.fixture(autouse=True)
def clear_pub():
    """ล้าง state zmq_pub ก่อนและหลังแต่ละ test"""
    runner.zmq_pub.sent.clear()
    yield
    runner.zmq_pub.sent.clear()


def test_signals_file_exists(tmp_path, monkeypatch):
    signals_file = tmp_path / "engine_status.json"
    signals_data = {"signals": [{"symbol": "BTCUSDc", "final_decision": "BUY"}]}
    signals_file.write_text(json.dumps(signals_data), encoding="utf-8")

    monkeypatch.setattr(runner, "ENGINE_STATUS_FILE", str(signals_file))

    data = json.loads(signals_file.read_text(encoding="utf-8"))
    runner.publish_zmq(runner.zmq_pub, "signals", data)

    assert runner.zmq_pub.sent
    msg = runner.zmq_pub.sent[0]
    assert msg["type"] == "json"
    assert "signals" in msg["data"]
    assert msg["data"]["signals"][0]["symbol"] == "BTCUSDc"


def test_signals_file_missing(tmp_path, monkeypatch):
    signals_file = tmp_path / "missing.json"
    monkeypatch.setattr(runner, "ENGINE_STATUS_FILE", str(signals_file))

    data = {"signals": []}
    runner.publish_zmq(runner.zmq_pub, "signals", data)

    assert runner.zmq_pub.sent
    msg = runner.zmq_pub.sent[0]
    assert msg["type"] == "json"
    assert "signals" in msg["data"]
    assert msg["data"]["signals"] == []


def test_execute_signal_mode():
    data = {"signals": [{"symbol": "XAUUSDc", "final_decision": "SELL"}]}
    runner.publish_zmq(runner.zmq_pub, "signals", data)

    assert runner.zmq_pub.sent
    msg = runner.zmq_pub.sent[-1]
    assert msg["type"] == "json"
    signals = msg["data"]["signals"]
    assert signals[0]["symbol"] == "XAUUSDc"
    assert signals[0]["final_decision"] == "SELL"


def test_execute_trade_mode():
    data = {"signals": [{"symbol": "EURUSDc", "final_decision": "BLOCKED"}]}
    runner.publish_zmq(runner.zmq_pub, "signals", data)

    assert runner.zmq_pub.sent
    msg = runner.zmq_pub.sent[-1]
    assert msg["type"] == "json"
    signals = msg["data"]["signals"]
    assert signals[0]["symbol"] == "EURUSDc"
    assert signals[0]["final_decision"] == "BLOCKED"
