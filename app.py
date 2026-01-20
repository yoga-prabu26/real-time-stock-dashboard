import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, time, date, timedelta
import pytz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Real-Time Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# ---------------- STATE ----------------
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = True

# ---------------- SIDEBAR ----------------
if st.session_state.show_sidebar:
    st.sidebar.header("⚙️ Settings")
    theme = st.sidebar.radio("Theme", ["Dark Mode 🌙", "Light Mode ☀️"])
else:
    theme = "Dark Mode 🌙"

# ---------------- THEME VARIABLES ----------------
if theme == "Dark Mode 🌙":
    bg_color = "#020617"
    card_color = "#020617"
    text_color = "#ffffff"
    sub_text = "#94a3b8"
    accent = "#38bdf8"
    plot_theme = "plotly_dark"
else:
    bg_color = "#f8fafc"
    card_color = "#ffffff"
    text_color = "#020617"
    sub_text = "#475569"
    accent = "#2563eb"
    plot_theme = "plotly"

# ---------------- GLOBAL CSS ----------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .top-title {{
        font-size:22px;
        font-weight:700;
        color:{accent};
        margin-bottom:6px;
    }}
    .metric-card {{
        background:{card_color};
        padding:18px;
        border-radius:14px;
        text-align:center;
        box-shadow:0 8px 18px rgba(0,0,0,0.25);
    }}
    .metric-label {{
        font-size:12px;
        color:{sub_text};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HEADER ----------------
h1, h2 = st.columns([9, 1])
with h1:
    st.markdown("<div class='top-title'>📊 Real-Time Stock Market Dashboard</div>", unsafe_allow_html=True)
with h2:
    if st.button("☰"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

st.caption("Sector-wise Analysis • Search • Alerts")
st.markdown("---")

# ---------------- SECTORS ----------------
sectors = {
    "IT Sector (India)": {
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "Wipro": "WIPRO.NS",
        "HCL Tech": "HCLTECH.NS"
    },
    "Banking Sector (India)": {
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "SBI": "SBIN.NS"
    },
    "US Tech": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN",
        "Google": "GOOGL",
        "Tesla": "TSLA"
    }
}

# ---------------- INPUT ----------------
if st.session_state.show_sidebar:
    sector = st.sidebar.selectbox("Select Sector", list(sectors.keys()))
    company = st.sidebar.selectbox("Select Company", list(sectors[sector].keys()))
else:
    sector = list(sectors.keys())[0]
    company = list(sectors[sector].keys())[0]

ticker = sectors[sector][company]

# ---------------- DATE RANGE ----------------
end_date = date.today()
start_date = end_date - timedelta(days=7)

# ---------------- FETCH DATA ----------------
data = yf.download(
    ticker,
    start=start_date,
    end=end_date + timedelta(days=1),
    progress=False
)

if data.empty:
    st.error("No data available.")
    st.stop()

data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
data = data.reset_index()

# ---------------- MARKET STATUS ----------------
india = pytz.timezone("Asia/Kolkata")
now = datetime.now(india).time()

if time(9, 15) <= now <= time(15, 30):
    st.success("🟢 Market is OPEN")
else:
    st.warning("🔴 Market is CLOSED")

# ---------------- METRICS ----------------
close = data["Close"].values
highs = data["High"].values
lows = data["Low"].values
vols = data["Volume"].values

current = float(close[-1])
previous = float(close[-2]) if len(close) > 1 else current
change = ((current - previous) / previous) * 100 if previous != 0 else 0

if change > 0:
    change_color = "#16a34a"
    change_icon = "🔼"
elif change < 0:
    change_color = "#dc2626"
    change_icon = "🔽"
else:
    change_color = "#9ca3af"
    change_icon = "➡️"

high = float(highs.max())
low = float(lows.min())
vol = int(vols[-1])

c1, c2, c3, c4, c5 = st.columns(5)

def card(icon, value, label, color=text_color):
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:22px">{icon}</div>
            <div style="font-size:20px;font-weight:700;color:{color}">
                {value}
            </div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c1: card("💰", f"{current:.2f}", "Price")
with c2: card(change_icon, f"{change:.2f}%", "Change %", change_color)
with c3: card("⬆️", f"{high:.2f}", "High")
with c4: card("⬇️", f"{low:.2f}", "Low")
with c5: card("📦", f"{vol:,}", "Volume")

# ---------------- PRICE ALERT ----------------
st.markdown("## 🔔 Price Alert")
alert = st.number_input("Alert when price crosses:", min_value=0.0)

if alert > 0:
    if current >= alert:
        st.success(f"🚨 ALERT: {company} crossed {alert}")
    else:
        st.info("Alert not triggered yet")

# ---------------- CHART ----------------
st.markdown("## 📈 Stock Price Trend")
fig = px.line(
    data,
    x="Date",
    y="Close",
    title=f"{company} Stock Price",
    template=plot_theme
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.markdown("## ⬇️ Download Data")
st.download_button(
    "Download CSV",
    data.to_csv(index=False),
    "stock_data.csv",
    "text/csv"
)

# ---------------- FOOTER ----------------
st.markdown(
    "<hr style='border:0.5px solid #334155'>"
    f"<center style='color:{sub_text}'>Educational Project • "
    "GitHub: https://github.com/yoga-prabu26/real-time-stock-dashboard</center>",
    unsafe_allow_html=True
)
