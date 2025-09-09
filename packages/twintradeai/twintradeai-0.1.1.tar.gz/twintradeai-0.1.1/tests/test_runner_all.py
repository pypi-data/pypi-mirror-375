import json
import pytest
from twintradeai.runner import publish_zmq, write_json, zmq_pub


@pytest.fixture(autouse=True)
def clear_pub():
    zmq_pub.sent.clear()
    yield
    zmq_pub.sent.clear()


# ------------------------------
# Unit-level publish tests
# ------------------------------
def test_runner_publish_signal():
    data = {"signals": [{"symbol": "BTCUSDc", "final_decision": "BUY"}]}
    publish_zmq(zmq_pub, "signals", data)

    assert zmq_pub.sent
    msg = zmq_pub.sent[0]
    assert msg["type"] == "json"
    data_out = msg["data"]
    assert data_out["signals"][0]["symbol"] == "BTCUSDc"
    assert data_out["signals"][0]["final_decision"] == "BUY"


def test_runner_publish_empty_signals():
    data = {"signals": []}
    publish_zmq(zmq_pub, "signals", data)

    assert zmq_pub.sent
    msg = zmq_pub.sent[0]
    assert msg["type"] == "json"
    data_out = msg["data"]
    assert data_out["signals"] == []


# ------------------------------
# Integration-style tests
# ------------------------------
def test_runner_one_cycle(tmp_path, monkeypatch):
    status_file = tmp_path / "engine_status.json"
    monkeypatch.setattr("twintradeai.runner.ENGINE_STATUS_FILE", str(status_file))

    signals = {"signals": [{"symbol": "XAUUSDc", "final_decision": "SELL"}]}
    write_json(status_file, signals)
    publish_zmq(zmq_pub, "signals", signals)

    assert status_file.exists()
    data = json.loads(status_file.read_text(encoding="utf-8"))
    assert "signals" in data

    assert zmq_pub.sent
    msg = zmq_pub.sent[-1]
    assert msg["type"] == "json"
    data_out = msg["data"]
    assert data_out["signals"][0]["symbol"] == "XAUUSDc"


def test_runner_blocked_case():
    signals = {
        "signals": [
            {"symbol": "EURUSDc", "final_decision": "BLOCKED", "reasons": ["Spread too high"]}
        ]
    }
    publish_zmq(zmq_pub, "signals", signals)

    assert zmq_pub.sent
    msg = zmq_pub.sent[-1]
    assert msg["type"] == "json"
    data_out = msg["data"]
    assert data_out["signals"][0]["final_decision"] == "BLOCKED"
    assert "Spread too high" in data_out["signals"][0]["reasons"]


# ------------------------------
# Publish helper tests
# ------------------------------
def test_publish_zmq_adds_message():
    data = {"signals": [{"symbol": "GBPUSDc", "final_decision": "BUY"}]}
    publish_zmq(zmq_pub, "signals", data)

    assert zmq_pub.sent
    msg = zmq_pub.sent[0]
    assert msg["type"] == "json"
    assert "signals" in msg["data"]


def test_write_json_creates_file(tmp_path):
    fpath = tmp_path / "sample.json"
    data = {"signals": [{"symbol": "BTCUSDc"}]}
    write_json(fpath, data)

    assert fpath.exists()
    loaded = json.loads(fpath.read_text(encoding="utf-8"))
    assert loaded == data
