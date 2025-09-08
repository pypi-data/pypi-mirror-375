import os
import json
import csv
import logging
from datetime import datetime, date
from dotenv import load_dotenv
import MetaTrader5 as mt5  # ✅ สำหรับ account info

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

STATUS_JSON_FILE = "risk_guard_status.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RISK_GUARD][%(levelname)s] %(message)s"
)


# ========= Safe parsers =========
def safe_float(val, default=None):
    try:
        if val is None or val == "":
            return default
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


# ========= RiskGuard =========
class RiskGuard:
    def __init__(self, status_file="risk_guard.json"):
        load_dotenv()

        self.status_file = status_file
        self.status_json_file = STATUS_JSON_FILE

        # === Global rules ===
        self.rules = {
            "max_spread": safe_float(os.getenv("RISK_MAX_SPREAD"), 100),
            "max_loss_day": safe_float(os.getenv("RISK_MAX_LOSS_DAY"), -100.0),
            "max_orders": safe_int(os.getenv("RISK_MAX_ORDERS"), 10),
            "min_margin_level": safe_float(os.getenv("RISK_MIN_MARGIN_LEVEL"), 150.0),
        }

        # === Per-symbol daily loss ===
        self.per_symbol_loss = {}
        for sym in os.getenv("SYMBOLS", "").split(","):
            if not sym:
                continue
            key = f"LOSS_LIMIT_{sym}"
            val = safe_float(os.getenv(key))
            if val is not None:
                self.per_symbol_loss[sym] = val

        logging.info(f"[RISK_GUARD] Per-symbol loss limits: {self.per_symbol_loss}")

        # === Spread limits ===
        self.spread_limits = {}
        for sym in os.getenv("SYMBOLS", "").split(","):
            if not sym:
                continue
            used_key, val = None, None
            env_key_full = f"SPREAD_LIMIT_{sym}"
            val = os.getenv(env_key_full)
            if val:
                used_key = env_key_full

            if not val:
                base = sym[:-1] if sym.endswith(("c", "m")) else sym
                env_key_base = f"SPREAD_LIMIT_{base}"
                val = os.getenv(env_key_base)
                if val:
                    used_key = env_key_base

            fval = safe_float(val)
            if fval is not None:
                self.spread_limits[sym] = fval
                logging.info(f"[RISK_GUARD] Spread limit for {sym}: {fval} (from {used_key})")

        logging.info(f"[RISK_GUARD] Final spread_limits: {self.spread_limits}")

        # === Daily status ===
        self.status = {"today_pnl": 0.0, "orders": 0, "date": str(date.today()), "pnl_per_symbol": {}}
        self.load_status()
        self.save_status_json()

    # ========= JSON Status =========
    def save_status_json(self):
        try:
            acc_info = mt5.account_info()
            account_metrics = {}
            if acc_info:
                account_metrics = {
                    "balance": acc_info.balance,
                    "equity": acc_info.equity,
                    "margin": acc_info.margin,
                    "margin_free": acc_info.margin_free,
                    "margin_level": getattr(acc_info, "margin_level", None),
                    "currency": acc_info.currency,
                }

            data = {
                "spread_limits": self.spread_limits,
                "rules": self.rules,
                "per_symbol_loss": self.per_symbol_loss,
                "status": self.status,
                "account": account_metrics,
                "last_update": datetime.utcnow().isoformat(),
            }
            with open(self.status_json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"[RISK_GUARD] Status JSON updated: {self.status_json_file}")
        except Exception as e:
            logging.error(f"[RISK_GUARD] save_status_json error: {e}")

    # ========= Spread limit getter =========
    def get_spread_limit(self, symbol: str) -> float:
        return self.spread_limits.get(symbol, self.rules.get("max_spread", 999999))

    # ========= Status persistence =========
    def load_status(self):
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.status.update(data)
            except Exception as e:
                logging.error(f"[RISK_GUARD] Load status error: {e}")

    def save_status(self):
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(self.status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"[RISK_GUARD] Save status error: {e}")
        self.save_status_json()

    # ========= Daily reset =========
    def reset_if_new_day(self):
        today_str = str(date.today())
        if self.status.get("date") != today_str:
            logging.info("[RISK_GUARD] New day detected → reset daily counters")
            self.status = {"today_pnl": 0.0, "orders": 0, "date": today_str, "pnl_per_symbol": {}}
            self.save_status()

    # ========= Logging blocked trades =========
    def log_block(self, symbol, reasons):
        log_file = os.path.join(LOG_DIR, f"{symbol}_log.csv")
        exists = os.path.isfile(log_file)
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "action": "BLOCK",
            "decision": None,
            "lot": None,
            "entry": None,
            "sl": None,
            "tp": None,
            "tp_tag": "N/A",
            "order_id": None,
            "deal_id": None,
            "profit": None,
            "reasons": ", ".join(reasons) if reasons else None,
        }
        try:
            with open(log_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                if not exists:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            logging.error(f"[RISK_GUARD] log_block error: {e}")

    # ========= Recorders =========
    def record_open(self, symbol):
        self.reset_if_new_day()
        self.status["orders"] += 1
        self.save_status()
        logging.info(f"[RISK_GUARD] record_open: {symbol}, total_orders={self.status['orders']}")

    def record_close(self, symbol, profit: float):
        self.reset_if_new_day()
        try:
            self.status["today_pnl"] += float(profit)
            self.status["pnl_per_symbol"].setdefault(symbol, 0.0)
            self.status["pnl_per_symbol"][symbol] += float(profit)
        except Exception as e:
            logging.error(f"[RISK_GUARD] record_close error: {e}")
        self.save_status()
        logging.info(
            f"[RISK_GUARD] record_close: {symbol}, profit={profit}, "
            f"today_pnl={self.status['today_pnl']}, {symbol}_pnl={self.status['pnl_per_symbol'].get(symbol)}"
        )

    # ========= Main check =========
    def check(self, symbol, atr, spread_pts, account=None, daily_pnl=None):
        try:
            self.reset_if_new_day()
            reasons, allowed = [], True

            spread_limit = self.get_spread_limit(symbol)
            if spread_limit and spread_pts is not None and spread_pts > spread_limit:
                reasons.append(f"Spread too high ({spread_pts:.1f} > {spread_limit})")
                allowed = False

            # === Global daily loss ===
            if daily_pnl is not None and daily_pnl <= self.rules["max_loss_day"]:
                reasons.append("Daily loss limit reached")
                allowed = False
            elif self.status["today_pnl"] <= self.rules["max_loss_day"]:
                reasons.append("Internal daily loss reached")
                allowed = False

            # === Per-symbol daily loss ===
            sym_loss_limit = self.per_symbol_loss.get(symbol)
            if sym_loss_limit is not None:
                sym_pnl = self.status["pnl_per_symbol"].get(symbol, 0.0)
                if sym_pnl <= sym_loss_limit:
                    reasons.append(
                        f"Per-symbol loss limit reached: {symbol} {sym_pnl} <= {sym_loss_limit}"
                    )
                    allowed = False

            # === Margin level check ===
            acc_info = account or mt5.account_info()
            if acc_info and hasattr(acc_info, "margin_level"):
                min_margin = self.rules.get("min_margin_level", 0)
                if acc_info.margin_level and acc_info.margin_level < min_margin:
                    reasons.append(f"Margin level too low ({acc_info.margin_level:.2f}% < {min_margin}%)")
                    allowed = False

            # === Max orders check ===
            if self.status["orders"] >= self.rules["max_orders"]:
                reasons.append("Max orders exceeded")
                allowed = False

            if not allowed:
                logging.warning(f"[RISK_GUARD] {symbol} blocked: {', '.join(reasons)}")
                self.log_block(symbol, reasons)

            self.save_status_json()

            metrics = {
                "spread_limit": spread_limit,
                "orders_today": self.status["orders"],
                "today_pnl": self.status["today_pnl"],
                "rules": self.rules,
                "pnl_per_symbol": self.status.get("pnl_per_symbol", {}),
                "balance": acc_info.balance if acc_info else None,
                "equity": acc_info.equity if acc_info else None,
                "margin": acc_info.margin if acc_info else None,
                "margin_free": acc_info.margin_free if acc_info else None,
                "margin_level": getattr(acc_info, "margin_level", None),
            }

            return allowed, reasons, metrics

        except Exception as e:
            logging.error(f"[RISK_GUARD] check() error: {e}")
            return False, [f"RiskGuard internal error: {e}"], {}
