import os
import json
import time
import zmq
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from fpdf import FPDF
from datetime import datetime

API_URL = os.getenv("API_URL", "http://localhost:9000")
ZMQ_SUB_URL = os.getenv("ZMQ_SUB_URL", "tcp://localhost:5557")
ZMQ_TOPIC = os.getenv("ZMQ_TOPIC", "signals")

st.set_page_config(page_title="TwinTradeAi Dashboard", layout="wide")

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# === ZMQ Subscriber ===
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect(ZMQ_SUB_URL)
sub.setsockopt_string(zmq.SUBSCRIBE, ZMQ_TOPIC)

def fetch_risk_status():
    """ดึง risk status จาก API (risk_guard_status.json)"""
    try:
        r = requests.get(f"{API_URL}/risk_status", timeout=5)
        if r.status_code == 200:
            return r.json().get("data", {})
        return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# === Chart Builder ===
def make_chart(df: pd.DataFrame, symbol: str):
    fig = go.Figure()

    # Price + Bollinger Bands
    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["entry"],
        high=df["tp3"],
        low=df["sl"],
        close=df["entry"],
        name="Price"
    ))
    if "bb_up" in df and "bb_lo" in df:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["bb_up"], line=dict(color="blue"), name="BB Upper"))
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["bb_lo"], line=dict(color="blue"), name="BB Lower"))

    # RSI
    if "rsi" in df:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["rsi"], line=dict(color="purple"), name="RSI", yaxis="y2"))

    # ATR
    if "atr" in df:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["atr"], line=dict(color="orange"), name="ATR", yaxis="y3"))

    # MACD
    if "macd" in df and "macd_signal" in df:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["macd"], line=dict(color="green"), name="MACD", yaxis="y4"))
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["macd_signal"], line=dict(color="red"), name="MACD Sig", yaxis="y4"))

    fig.update_layout(
        title=f"{symbol} Indicators",
        height=500,
        yaxis=dict(title="Price"),
        yaxis2=dict(title="RSI", overlaying="y", side="right", position=0.95),
        yaxis3=dict(title="ATR", overlaying="y", side="right", position=1.05),
        yaxis4=dict(title="MACD", overlaying="y", side="right", position=1.15),
        showlegend=True
    )
    return fig

def save_report(signals_df, pnl_fig, indicator_figs):
    """บันทึก PDF Report รวม PnL + Indicators"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    pdf_path = os.path.join(REPORT_DIR, f"report_{today}.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"TwinTradeAi Report - {today}", ln=True, align="C")

    # --- Table Summary ---
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, "Signals Snapshot", ln=True)

    if not signals_df.empty:
        table_path = os.path.join(REPORT_DIR, f"signals_{today}.csv")
        signals_df.to_csv(table_path, index=False)

        for i, row in signals_df.iterrows():
            line = f"{row['symbol']} | {row['final_decision']} | entry={row['entry']} sl={row['sl']} tp1={row['tp1']}"
            pdf.cell(200, 8, line, ln=True)

    # --- Save PnL Chart ---
    pnl_img = os.path.join(REPORT_DIR, f"pnl_{today}.png")
    pio.write_image(pnl_fig, pnl_img, format="png", width=900, height=400, engine="kaleido")
    pdf.add_page()
    pdf.cell(200, 10, "PnL Overview", ln=True, align="C")
    pdf.image(pnl_img, x=10, y=30, w=190)

    # --- Save Indicators Charts ---
    for sym, fig in indicator_figs.items():
        img_path = os.path.join(REPORT_DIR, f"{sym}_{today}.png")
        pio.write_image(fig, img_path, format="png", width=900, height=500, engine="kaleido")
        pdf.add_page()
        pdf.cell(200, 10, f"Indicators - {sym}", ln=True, align="C")
        pdf.image(img_path, x=10, y=30, w=190)

    pdf.output(pdf_path)
    return pdf_path

# === UI Layout ===
st.title("📊 TwinTradeAi Dashboard")

col1, col2 = st.columns([2, 1])
signals_box = col1.empty()
risk_box = col2.empty()

st.markdown("---")
st.subheader("📈 PnL Overview")
pnl_chart_box = st.empty()

# ✅ ปุ่ม Save Report
if st.button("💾 Save Daily PDF Report"):
    signals_df = st.session_state.get("signals_data", pd.DataFrame())
    pnl_fig = st.session_state.get("fig_pnl", None)

    if not signals_df.empty and pnl_fig is not None:
        # เตรียม indicator charts
        indicator_figs = {}
        for sym in signals_df["symbol"].unique():
            hist_df = signals_df[signals_df["symbol"] == sym].tail(100)
            if not hist_df.empty:
                fig = make_chart(hist_df, sym)
                indicator_figs[sym] = fig

        pdf_path = save_report(signals_df, pnl_fig, indicator_figs)
        st.success(f"✅ PDF Report saved: {pdf_path}")

        if send_email_report(pdf_path):
            st.info(f"📧 Report sent to {EMAIL_RECEIVER}")
        else:
            st.warning("⚠️ Report saved but email not sent (check config)")
    else:
        st.warning("⚠️ ยังไม่มี signals หรือ PnL chart ให้บันทึก")
