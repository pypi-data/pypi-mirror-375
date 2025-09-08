import MetaTrader5 as mt5
import pandas as pd
import yaml
from datetime import datetime, timedelta
from indicators import add_indicators
import argparse
import matplotlib.pyplot as plt
import os


# ========== CONFIG ==========
SYMBOLS = {
    "BTCUSDc": mt5.TIMEFRAME_H1,
    "XAUUSDc": mt5.TIMEFRAME_H1,
    "EURUSDc": mt5.TIMEFRAME_M15,
}
CONFIG_FILE = "config.symbols.yaml"


# ========== HELPERS ==========
def round_val(x, ndigits=5):
    """safe rounding"""
    try:
        return round(float(x), ndigits)
    except Exception:
        return x


def get_distribution(series: pd.Series):
    """คืนค่าสถิติพื้นฐาน"""
    return {
        "mean": series.mean(),
        "median": series.median(),
        "p5": series.quantile(0.05),
        "p10": series.quantile(0.10),
        "p25": series.quantile(0.25),
        "p75": series.quantile(0.75),
        "min": series.min(),
        "max": series.max(),
    }


# ========== SCANNER ==========
def scan_symbol(symbol, timeframe, days=180):
    rates = mt5.copy_rates_from(
        symbol, timeframe, datetime.utcnow() - timedelta(days=days), days * 24
    )
    if rates is None:
        print(f"[ERROR] No data for {symbol} ({days} days)")
        return None, None

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = add_indicators(df, symbol)

    atr_stats = get_distribution(df["atr"].dropna())
    rsi_stats = get_distribution(df["rsi"].dropna())
    bb_width = (df["bb_up"] - df["bb_lo"]) / df["bb_mid"]
    bb_stats = get_distribution(bb_width.dropna())
    spread_ratio = (df["ema20"] - df["ema50"]).abs() / df["atr"]
    spread_stats = get_distribution(spread_ratio.dropna())

    return {
        "symbol": symbol,
        "atr_p10": atr_stats["p10"],
        "rsi_flat_low": rsi_stats["p25"],
        "rsi_flat_high": rsi_stats["p75"],
        "bb_width_thr": bb_stats["p10"],
        "ema_squeeze_k": spread_stats["p10"],
    }, {"df": df, "bb_width": bb_width}


# ========== MODES ==========
def compare_mode(symbols, compare_days, outdir="plots_compare"):
    os.makedirs(outdir, exist_ok=True)
    all_rows = []

    for days in compare_days:
        for sym, tf in symbols.items():
            stats, _ = scan_symbol(sym, tf, days=days)
            if stats:
                row = {"lookback": days}
                row.update({k: round_val(v, 5) for k, v in stats.items()})
                all_rows.append(row)

    df_compare = pd.DataFrame(all_rows)
    print("\n=== Compare Mode Results ===")
    print(df_compare)

    for sym in df_compare["symbol"].unique():
        subset = df_compare[df_compare["symbol"] == sym]
        plt.figure(figsize=(6, 4))
        plt.plot(subset["lookback"], subset["atr_p10"], marker="o", label="ATR p10")
        plt.plot(subset["lookback"], subset["bb_width_thr"], marker="s", label="BB width p10")
        plt.plot(subset["lookback"], subset["ema_squeeze_k"], marker="^", label="EMA squeeze p10")
        plt.title(f"{sym} Indicator Floors vs Lookback")
        plt.xlabel("Lookback days")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.savefig(os.path.join(outdir, f"{sym}_compare.png"))
        plt.close()

    print(f"[INFO] Compare plots saved under {outdir}/")
    export_file = f"indicator_floor_compare_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    df_compare.to_csv(export_file, index=False)
    print(f"[INFO] Exported → {export_file}")


def auto_tune(symbols, lookbacks, outdir="plots_autotune"):
    os.makedirs(outdir, exist_ok=True)
    results_by_sym = {}

    for sym, tf in symbols.items():
        all_stats = []
        for days in lookbacks:
            stats, _ = scan_symbol(sym, tf, days=days)
            if stats:
                stats["lookback"] = days
                all_stats.append(stats)

        if not all_stats:
            print(f"[WARN] No stats for {sym}, skipping auto-tune")
            continue

        df_stats = pd.DataFrame(all_stats)

        # คำนวณ median เฉพาะ parameter ที่ต้องใช้ (exclude lookback/symbol)
        params_to_plot = ["atr_p10", "rsi_flat_low", "rsi_flat_high", "bb_width_thr", "ema_squeeze_k"]
        median_stats = df_stats[params_to_plot].median().to_dict()
        median_stats["symbol"] = sym
        results_by_sym[sym] = median_stats

        print(f"\n=== Auto-tune {sym} ===")
        print(df_stats)
        print("→ median:", {k: round_val(v, 5) for k, v in median_stats.items()})

        # === Boxplot stability ===
        plt.figure(figsize=(8, 5))
        ax = df_stats[params_to_plot].boxplot()
        plt.title(f"{sym} Stability across lookbacks {lookbacks}")
        plt.ylabel("Value")
        plt.grid(True, linestyle="--", alpha=0.6)

        # วาดเส้น median ของแต่ละ parameter
        for i, param in enumerate(params_to_plot, start=1):
            med_val = median_stats.get(param, None)
            if med_val is not None:
                plt.hlines(y=med_val, xmin=i - 0.25, xmax=i + 0.25,
                           colors="red", linestyles="--", linewidth=1.2)
                plt.text(i + 0.3, med_val, f"{med_val:.4f}",
                         va="center", ha="left", color="red", fontsize=8)

        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"{sym}_stability_boxplot.png"))
        plt.close()

        # === Trend line per parameter ===
        plt.figure(figsize=(8, 5))
        for param in params_to_plot:
            plt.plot(df_stats["lookback"], df_stats[param], marker="o", label=param)
            # median line
            med_val = median_stats[param]
            plt.hlines(y=med_val, xmin=min(df_stats["lookback"]), xmax=max(df_stats["lookback"]),
                       colors="red", linestyles="--", alpha=0.5)

        plt.title(f"{sym} Parameter Trend across lookbacks")
        plt.xlabel("Lookback days")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"{sym}_trend.png"))
        plt.close()

    # update YAML config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        for sym, med in results_by_sym.items():
            if sym in cfg:
                cfg[sym]["atr_floor"] = round_val(med["atr_p10"], 5)
                cfg[sym]["rsi_flat"] = [
                    round_val(med["rsi_flat_low"], 2),
                    round_val(med["rsi_flat_high"], 2),
                ]
                cfg[sym]["bb_width_thr"] = round_val(med["bb_width_thr"], 5)
                cfg[sym]["ema_squeeze_k"] = round_val(med["ema_squeeze_k"], 5)

                print(
                    f"[AUTO-TUNE] {sym} → "
                    f"atr_floor={cfg[sym]['atr_floor']}, "
                    f"rsi_flat={cfg[sym]['rsi_flat']}, "
                    f"bb_width_thr={cfg[sym]['bb_width_thr']}, "
                    f"ema_squeeze_k={cfg[sym]['ema_squeeze_k']}"
                )

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, allow_unicode=True, sort_keys=False)
        print(f"[INFO] config.symbols.yaml updated ✅ (auto-tune mode)")

    except Exception as e:
        print(f"[ERROR] Failed to update config: {e}")



# ========== MAIN ==========
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan indicator distributions.")
    parser.add_argument("--days", type=int, default=180, help="Lookback days (default=180)")
    parser.add_argument("--no-update", action="store_true", help="Skip config update")
    parser.add_argument("--plot", action="store_true", help="Generate hist/box plots")
    parser.add_argument(
        "--compare",
        nargs="+",
        type=int,
        help="Compare mode: provide multiple lookback periods, e.g. --compare 90 180 365",
    )
    parser.add_argument(
        "--autotune",
        nargs="+",
        type=int,
        help="Auto-tune mode: provide multiple lookback periods, e.g. --autotune 90 180 365",
    )
    args = parser.parse_args()

    if not mt5.initialize():
        print("MT5 initialize() failed")
        quit()

    if args.compare:
        compare_mode(SYMBOLS, args.compare)
        exit(0)

    if args.autotune:
        auto_tune(SYMBOLS, args.autotune)
        exit(0)

    # default mode
    results, raw_data = [], []
    for sym, tf in SYMBOLS.items():
        stats, data = scan_symbol(sym, tf, days=args.days)
        if stats:
            results.append(stats)
            raw_data.append((sym, data))

    df_export = pd.DataFrame(
        [
            {
                "symbol": r["symbol"],
                "atr_p10": round_val(r["atr_p10"], 5),
                "rsi_flat_low": round_val(r["rsi_flat_low"], 2),
                "rsi_flat_high": round_val(r["rsi_flat_high"], 2),
                "bb_width_thr": round_val(r["bb_width_thr"], 5),
                "ema_squeeze_k": round_val(r["ema_squeeze_k"], 5),
            }
            for r in results
        ]
    )

    print("\n=== Suggested Parameters (p10 as floor/threshold) ===")
    print(df_export)

    export_file = f"indicator_floor_stats_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    df_export.to_csv(export_file, index=False)
    print(f"\n[INFO] Exported → {export_file}")

    if not args.no_update:
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)

            for r in results:
                sym = r["symbol"]
                if sym in cfg:
                    cfg[sym]["atr_floor"] = round_val(r["atr_p10"], 5)
                    cfg[sym]["rsi_flat"] = [
                        round_val(r["rsi_flat_low"], 2),
                        round_val(r["rsi_flat_high"], 2),
                    ]
                    cfg[sym]["bb_width_thr"] = round_val(r["bb_width_thr"], 5)
                    cfg[sym]["ema_squeeze_k"] = round_val(r["ema_squeeze_k"], 5)

                    print(
                        f"[UPDATE] {sym}: atr_floor={cfg[sym]['atr_floor']}, "
                        f"rsi_flat={cfg[sym]['rsi_flat']}, "
                        f"bb_width_thr={cfg[sym]['bb_width_thr']}, "
                        f"ema_squeeze_k={cfg[sym]['ema_squeeze_k']}"
                    )

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, allow_unicode=True, sort_keys=False)
            print(f"[INFO] config.symbols.yaml updated ✅")

        except Exception as e:
            print(f"[ERROR] Failed to update config: {e}")
