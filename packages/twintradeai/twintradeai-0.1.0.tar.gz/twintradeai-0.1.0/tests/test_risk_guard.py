from twintradeai.risk_guard import RiskGuard


def test_spread_limit_and_rules(tmp_path):
    rg = RiskGuard(status_file=tmp_path / "rg.json")
    limit = rg.get_spread_limit("XAUUSDc")
    assert isinstance(limit, (int, float))

    allowed, reasons, metrics = rg.check("XAUUSDc", atr=5.0, spread_pts=1.0)
    assert isinstance(allowed, bool)
    assert isinstance(reasons, list)
    assert isinstance(metrics, dict)
