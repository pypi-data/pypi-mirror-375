import os
from dotenv import load_dotenv

load_dotenv()  # โหลด .env เข้ามาเป็น environment variables


def safe_float(val, default=None):
    try:
        if val is None or val == "":
            return default
        if isinstance(val, str) and val.endswith("%"):
            # support % เช่น "-5%"
            return float(val.strip("%")) / 100.0
        return float(val)
    except Exception:
        return default


def safe_int(val, default=None):
    try:
        if val is None or val == "":
            return default
        return int(val)
    except Exception:
        return default


def load_env_symbols():
    """โหลด SYMBOLS ทั้งหมด พร้อม config per-symbol และ fallback default"""

    # --- Global defaults ---
    global_cfg = {
        "max_spread": safe_float(os.getenv("RISK_MAX_SPREAD"), 9999),
        "max_loss_day": safe_float(os.getenv("RISK_MAX_LOSS_DAY"), -100.0),
        "max_orders": safe_int(os.getenv("RISK_MAX_ORDERS"), 10),
        "risk_percent": safe_float(os.getenv("RISK_PERCENT"), 0.01),
        "loss_limit_default": safe_float(os.getenv("LOSS_LIMIT_DEFAULT"), -100),
    }

    # --- Symbols list ---
    symbols = [s.strip() for s in os.getenv("SYMBOLS", "").split(",") if s.strip()]

    symbol_cfgs = {}
    for sym in symbols:
        # override keys
        spread = safe_float(os.getenv(f"SPREAD_LIMIT_{sym}"), global_cfg["max_spread"])
        loss_limit = safe_float(os.getenv(f"LOSS_LIMIT_{sym}"), global_cfg["loss_limit_default"])
        risk_percent = safe_float(os.getenv(f"RISK_PERCENT_{sym}"), global_cfg["risk_percent"])

        symbol_cfgs[sym] = {
            "spread_limit": spread,
            "loss_limit": loss_limit,
            "risk_percent": risk_percent,
        }

    return symbols, global_cfg, symbol_cfgs
