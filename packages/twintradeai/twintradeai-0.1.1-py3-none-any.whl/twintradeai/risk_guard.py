import os
import json
import csv
import logging
from datetime import datetime, date
from dotenv import load_dotenv
import MetaTrader5 as mt5  # ✅ สำหรับ account info

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

STATUS_FILE = "status.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RISK_GUARD][%(levelname)s] %(message)s"
)


# ========= Safe parsers =========
def safe_float(val, default=None):
    try:
        if val is None or val == "":
            return default
        if isinstance(val, str) and val.endswith("%"):
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


# ========= Helper: load env symbols =========
def load_env_symbols():
    load_dotenv()

    global_cfg = {
        "max_spread": safe_float(os.getenv("RISK_MAX_SPREAD"), 200),
        "max_loss_day": safe_float(os.getenv("RISK_MAX_LOSS_DAY"), -100.0),
        "max_orders": safe_int(os.getenv("RISK_MAX_ORDERS"), 10),
        "min_margin_level": safe_float(os.getenv("RISK_MIN_MARGIN_LEVEL"), 150.0),
        "risk_percent": safe_float(os.getenv("RISK_PERCENT"), 1.0),
        "loss_limit_default": safe_float(os.getenv("LOSS_LIMIT_DEFAULT"), -100.0),
    }

    symbols = [s.strip() for s in os.getenv("SYMBOLS", "").split(",") if s.strip()]

    symbol_cfgs = {}
    for sym in symbols:
        spread = safe_float(os.getenv(f"SPREAD_LIMIT_{sym}"), global_cfg["max_spread"])
        loss_limit = safe_float(os.getenv(f"LOSS_LIMIT_{sym}"), global_cfg["loss_limit_default"])
        risk_percent = safe_float(os.getenv(f"RISK_PERCENT_{sym}"), global_cfg["risk_percent"])

        symbol_cfgs[sym] = {
            "spread_limit": spread,
            "loss_limit": loss_limit,
            "risk_percent": risk_percent,
        }

    return symbols, global_cfg, symbol_cfgs


# ========= RiskGuard =========
class RiskGuard:
    def __init__(self, status_file=STATUS_FILE):
        self.status_file = str(status_file)
        self.status_full_file = os.path.join(
            os.path.dirname(self.status_file),
            "risk_guard_status.json"
        )

        # โหลดค่า env
        self.symbols, self.global_cfg, self.symbol_cfgs = load_env_symbols()

        logging.info(f"[RISK_GUARD] Loaded symbols: {self.symbols}")
        logging.info(f"[RISK_GUARD] Global rules: {self.global_cfg}")
        logging.info(f"[RISK_GUARD] Per-symbol cfg: {self.symbol_cfgs}")

        # Map config
        self.spread_limits = {s: cfg["spread_limit"] for s, cfg in self.symbol_cfgs.items()}
        self.per_symbol_loss = {s: cfg["loss_limit"] for s, cfg in self.symbol_cfgs.items()}

        self.status = {
            "today_pnl": 0.0,
            "orders": 0,
            "date": str(date.today()),
            "pnl_per_symbol": {}
        }
        self.load_status()
        self.save_status()

    # ---------- File Ops ----------
    def save_status(self):
        try:
            # --- save minimal status (legacy) ---
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(self.status, f, indent=2, ensure_ascii=False)

            # --- save full status ---
            acc_info = mt5.account_info()
            account_metrics = {}
            if acc_info:
                account_metrics = {
                    "balance": getattr(acc_info, "balance", None),
                    "equity": getattr(acc_info, "equity", None),
                    "margin": getattr(acc_info, "margin", None),
                    "margin_free": getattr(acc_info, "margin_free", None),
                    "margin_level": getattr(acc_info, "margin_level", None),
                    "currency": getattr(acc_info, "currency", None),
                }

            data = {
                "spread_limits": self.spread_limits,
                "rules": self.global_cfg,
                "per_symbol_loss": self.per_symbol_loss,
                "status": self.status,
                "account": account_metrics,
                "last_update": datetime.utcnow().isoformat(),
            }
            with open(self.status_full_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logging.error(f"[RISK_GUARD] save_status error: {e}")

    def get_spread_limit(self, symbol):
        return self.spread_limits.get(symbol, self.global_cfg.get("max_spread", 999999))

    def load_status(self):
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, "r", encoding="utf-8") as f:
                    self.status.update(json.load(f))
            except Exception as e:
                logging.error(f"[RISK_GUARD] load_status error: {e}")

    def reset_if_new_day(self):
        today = str(date.today())
        if self.status.get("date") != today:
            self.status = {
                "today_pnl": 0.0,
                "orders": 0,
                "date": today,
                "pnl_per_symbol": {}
            }
            self.save_status()

    # ---------- Logging ----------
    def log_block(self, symbol, reasons, metrics=None):
        log_file = os.path.join(LOG_DIR, f"{symbol}_log.csv")
        exists = os.path.isfile(log_file)
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "action": "BLOCK",
            "reasons": ", ".join(reasons),
        }
        if metrics:
            row.update({f"m_{k}": v for k, v in metrics.items()})

        try:
            with open(log_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                if not exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            logging.error(f"[RISK_GUARD] log_block error: {e}")

    # ---------- Core Check ----------
    def check(self, symbol, atr, spread_pts, account=None, daily_pnl=None):
        self.reset_if_new_day()
        reasons, allowed = [], True

        # Spread limit
        spread_limit = self.get_spread_limit(symbol)
        if spread_limit and spread_pts is not None and spread_pts > spread_limit:
            reasons.append(f"Spread too high ({spread_pts} > {spread_limit})")
            allowed = False

        # Daily loss
        if daily_pnl is not None and daily_pnl <= self.global_cfg["max_loss_day"]:
            reasons.append("Daily loss limit reached")
            allowed = False
        elif self.status["today_pnl"] <= self.global_cfg["max_loss_day"]:
            reasons.append("Internal daily loss reached")
            allowed = False

        # Per-symbol loss
        sym_loss = self.per_symbol_loss.get(symbol)
        if sym_loss is not None and self.status["pnl_per_symbol"].get(symbol, 0) <= sym_loss:
            reasons.append(f"Per-symbol loss limit reached {symbol}")
            allowed = False

        # Margin check
        acc_info = account or mt5.account_info()
        if acc_info:
            margin_level = getattr(acc_info, "margin_level", None)
            if margin_level is not None:
                min_margin = self.global_cfg.get("min_margin_level", 0)
                if margin_level < min_margin:
                    reasons.append(f"Margin level too low {margin_level:.2f}% < {min_margin}%")
                    allowed = False

        # Max orders
        if self.status["orders"] >= self.global_cfg["max_orders"]:
            reasons.append("Max orders exceeded")
            allowed = False

        metrics = {
            "spread_limit": spread_limit,
            "orders_today": self.status["orders"],
            "today_pnl": self.status["today_pnl"],
            "pnl_per_symbol": self.status.get("pnl_per_symbol", {}),
            "rules": self.global_cfg,
            "atr": atr,
            "spread_pts": spread_pts,
            "loss_limit_symbol": sym_loss,
        }

        if not allowed:
            logging.warning(
                f"[RISK_GUARD] BLOCK {symbol}: {', '.join(reasons)} "
                f"(spread={spread_pts}, orders={self.status['orders']}, pnl={self.status['today_pnl']})"
            )
            self.log_block(symbol, reasons, metrics)

        self.save_status()

        return {
            "allowed": allowed,
            "reasons": reasons,
            "metrics": metrics,
        }
