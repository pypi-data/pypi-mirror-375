import json
import csv
import pytest
from types import SimpleNamespace
from datetime import date, timedelta

from twintradeai.risk_guard import RiskGuard


@pytest.fixture
def rg(tmp_path, monkeypatch):
    monkeypatch.setattr("twintradeai.risk_guard.LOG_DIR", str(tmp_path))
    return RiskGuard(status_file=tmp_path / "status.json")


# ------------------------------
# Parametrized blocking conditions
# ------------------------------
@pytest.mark.parametrize(
    "setup_func, symbol, reason_match",
    [
        # Spread too high
        (lambda rg: rg.spread_limits.__setitem__("BTCUSDc", 5), "BTCUSDc", "Spread too high"),
        # Global daily loss (allow any 'loss' wording)
        (lambda rg: rg.status.update(today_pnl=-100) or rg.global_cfg.update(max_loss_day=-50),
         "XAUUSDc", "loss"),
        # Per-symbol loss
        (lambda rg: (rg.per_symbol_loss.__setitem__("BTCUSDc", -50),
                     rg.status["pnl_per_symbol"].__setitem__("BTCUSDc", -60)),
         "BTCUSDc", "Per-symbol loss"),
        # Max orders
        (lambda rg: (rg.global_cfg.update(max_orders=1), rg.status.update(orders=2)),
         "XAUUSDc", "Max orders exceeded"),
    ],
)
def test_blocking_conditions_parametrized(rg, setup_func, symbol, reason_match):
    setup_func(rg)
    result = rg.check(symbol, atr=0.1, spread_pts=10)
    assert result["allowed"] is False
    assert any(reason_match in r for r in result["reasons"])
    assert "metrics" in result


# ------------------------------
# Margin Level
# ------------------------------
def test_block_on_margin_level(rg):
    rg.global_cfg["min_margin_level"] = 150
    account = SimpleNamespace(margin_level=120)
    result = rg.check("BTCUSDc", atr=0.1, spread_pts=1, account=account)
    assert result["allowed"] is False
    assert any("Margin level too low" in r for r in result["reasons"])


def test_margin_level_ok_allows(rg):
    rg.global_cfg["min_margin_level"] = 100
    account = SimpleNamespace(margin_level=200)
    result = rg.check("XAUUSDc", atr=0.2, spread_pts=1, account=account)
    assert result["allowed"] is True
    assert result["reasons"] == []


# ------------------------------
# Logging & Status
# ------------------------------
def test_log_block_creates_csv(rg, tmp_path):
    rg.spread_limits["BTCUSDc"] = 1
    _ = rg.check("BTCUSDc", atr=0.1, spread_pts=10)
    log_file = tmp_path / "BTCUSDc_log.csv"
    assert log_file.exists()
    with open(log_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        assert any("Spread too high" in rows[0]["reasons"] for _ in rows)


def test_status_json_updated(rg, tmp_path):
    rg.spread_limits["BTCUSDc"] = 1
    _ = rg.check("BTCUSDc", atr=0.1, spread_pts=10)
    json_file = tmp_path / "risk_guard_status.json"
    assert json_file.exists()
    data = json.loads(json_file.read_text(encoding="utf-8"))

    assert "spread_limits" in data
    assert "rules" in data
    assert "status" in data
    # ✅ account key may exist but value can be None/dict
    assert "account" in data


# ------------------------------
# Positive Case
# ------------------------------
def test_allowed_when_all_conditions_pass(rg):
    rg.spread_limits["BTCUSDc"] = 10
    rg.global_cfg["max_loss_day"] = -500
    rg.per_symbol_loss["BTCUSDc"] = -500
    rg.global_cfg["max_orders"] = 10
    rg.global_cfg["min_margin_level"] = 50
    account = SimpleNamespace(margin_level=200)

    result = rg.check("BTCUSDc", atr=0.1, spread_pts=1, account=account)

    assert result["allowed"] is True
    assert result["reasons"] == []

    metrics = result["metrics"]
    assert metrics["spread_limit"] == 10
    assert metrics["spread_pts"] == 1
    assert metrics["atr"] == 0.1
    assert isinstance(metrics["orders_today"], int)
    assert isinstance(metrics["today_pnl"], (int, float))
    assert isinstance(metrics["pnl_per_symbol"], dict)
    assert metrics["rules"] == rg.global_cfg


# ------------------------------
# Reset daily
# ------------------------------
def test_reset_if_new_day_resets_status(rg, tmp_path):
    yesterday = str(date.today() - timedelta(days=1))
    rg.status = {
        "today_pnl": -200,
        "orders": 5,
        "date": yesterday,
        "pnl_per_symbol": {"BTCUSDc": -100},
    }

    rg.reset_if_new_day()

    assert rg.status["date"] == str(date.today())
    assert rg.status["today_pnl"] == 0.0
    assert rg.status["orders"] == 0
    assert rg.status["pnl_per_symbol"] == {}

    status_file = tmp_path / "status.json"
    assert status_file.exists()
    data = json.loads(status_file.read_text(encoding="utf-8"))
    assert data["date"] == str(date.today())
