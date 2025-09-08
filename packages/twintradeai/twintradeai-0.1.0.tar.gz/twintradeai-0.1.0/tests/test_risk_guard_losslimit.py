import pytest
from twintradeai.risk_guard import RiskGuard


@pytest.fixture
def rg(tmp_path):
    """สร้าง RiskGuard ใหม่ พร้อมไฟล์ status ชั่วคราว"""
    rg = RiskGuard(status_file=tmp_path / "rg.json")
    # กำหนด per-symbol loss limits เอง (แทนการอ่านจาก ENV)
    rg.per_symbol_loss = {"BTCUSDc": -200, "XAUUSDc": -100}
    return rg


def test_btc_loss_limit_trigger(rg):
    # ปิด order BTC -201 → ควร block
    rg.record_close("BTCUSDc", -201)

    allowed, reasons, _ = rg.check("BTCUSDc", atr=5.0, spread_pts=10)
    assert allowed is False
    assert any("Per-symbol loss limit reached" in r for r in reasons)


def test_xau_loss_limit_not_trigger(rg):
    # ปิด order XAU -50 → ยังไม่ถึง limit
    rg.record_close("XAUUSDc", -50)

    allowed, reasons, _ = rg.check("XAUUSDc", atr=5.0, spread_pts=10)
    assert allowed is True
    assert not any("Per-symbol loss limit reached" in r for r in reasons)


def test_xau_loss_limit_trigger(rg):
    # ปิด order XAU -120 → เกิน limit
    rg.record_close("XAUUSDc", -120)

    allowed, reasons, _ = rg.check("XAUUSDc", atr=5.0, spread_pts=10)
    assert allowed is False
    assert any("Per-symbol loss limit reached" in r for r in reasons)
