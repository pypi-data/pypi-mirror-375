import types
import pytest
from twintradeai.risk_guard import RiskGuard


class DummyAccount:
    def __init__(self, margin_level):
        self.balance = 1000
        self.equity = 1000
        self.margin = 100
        self.margin_free = 900
        self.margin_level = margin_level
        self.currency = "USD"


@pytest.fixture
def rg(tmp_path):
    """สร้าง RiskGuard ใหม่ พร้อม status ชั่วคราว"""
    rg = RiskGuard(status_file=tmp_path / "rg.json")
    # ตั้ง margin threshold = 150%
    rg.rules["min_margin_level"] = 150.0
    return rg


def test_margin_level_blocked(rg):
    """ควร block ถ้า margin level ต่ำกว่า threshold"""
    low_margin_acc = DummyAccount(120.0)
    allowed, reasons, metrics = rg.check("XAUUSDc", atr=5.0, spread_pts=10, account=low_margin_acc)

    assert allowed is False
    assert any("Margin level too low" in r for r in reasons)
    assert metrics["margin_level"] == 120.0


def test_margin_level_allowed(rg):
    """ควรอนุญาต ถ้า margin level สูงกว่า threshold"""
    safe_margin_acc = DummyAccount(200.0)
    allowed, reasons, metrics = rg.check("XAUUSDc", atr=5.0, spread_pts=10, account=safe_margin_acc)

    assert allowed is True
    assert not any("Margin level too low" in r for r in reasons)
    assert metrics["margin_level"] == 200.0
