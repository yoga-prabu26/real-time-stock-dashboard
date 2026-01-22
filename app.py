import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, time
import pytz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Real-Time Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Settings")
theme = st.sidebar.radio("Theme", ["Dark Mode 🌙", "Light Mode ☀️"])

# ---------------- THEME VARIABLES ----------------
if theme.startswith("Dark"):
    plot_theme = "plotly_dark"
    bg_card = "#020617"
    text_main = "#ffffff"
    text_sub = "#94a3b8"
    title_color = "#38bdf8"
    shadow = "rgba(0,0,0,0.4)"
else:
    plot_theme = "plotly"
    bg_card = "#f8fafc"
    text_main = "#020617"
    text_sub = "#475569"
    title_color = "#0f172a"
    shadow = "rgba(0,0,0,0.1)"

# ---------------- STYLES ----------------
st.markdown(
    f"""
    <style>
    .title {{
        font-size:24px;
        font-weight:700;
        color:{title_color};
    }}
    .subtitle {{
        color:{text_sub};
        margin-bottom:12px;
    }}
    .card {{
        background:{bg_card};
        padding:18px;
        border-radius:14px;
        text-align:center;
        box-shadow:0 6px 16px {shadow};
    }}
    .label {{
        font-size:12px;
        color:{text_sub};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE ----------------
st.markdown("<div class='title'>📊 Real-Time Stock Market Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sector-wise Analysis • Controlled Fetch • Alerts</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- SECTORS ----------------
sectors = {
    "Indian Banking": {
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "SBI": "SBIN.NS"
    },
    "Indian IT": {
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "Wipro": "WIPRO.NS"
    },
    "US Tech": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN",
        "Nvidia": "NVDA"
    }
}

sector = st.sidebar.selectbox("Select Sector", list(sectors.keys()))
company = st.sidebar.selectbox("Select Company", list(sectors[sector].keys()))
ticker = sectors[sector][company]

# ---------------- FETCH BUTTON (IMPORTANT) ----------------
fetch = st.sidebar.button("📥 Fetch Stock Data")

# ---------------- CACHE FUNCTION ----------------
@st.cache_data(ttl=600)
def fetch_data(symbol):
    df = yf.download(
        symbol,
        period="1mo",
        interval="1d",
        auto_adjust=True,
        progress=False
    )
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.reset_index()

# ---------------- FETCH LOGIC ----------------
if not fetch:
    st.info("👈 Select a stock and click **Fetch Stock Data**")
    st.stop()

data = fetch_data(ticker)

if data is None:
    st.warning("⚠️ Yahoo Finance rate-limited the request. Please wait 1–2 minutes and try again.")
    st.stop()

# ---------------- MARKET STATUS ----------------
india = pytz.timezone("Asia/Kolkata")
now = datetime.now(india).time()

if time(9, 15) <= now <= time(15, 30):
    st.success("🟢 Market is OPEN")
else:
    st.warning("🔴 Market is CLOSED")

# ---------------- METRICS ----------------
close = data["Close"]
high = data["High"].max()
low = data["Low"].min()
volume = int(data["Volume"].iloc[-1])

current = float(close.iloc[-1])
previous = float(close.iloc[-2]) if len(close) > 1 else current
change = ((current - previous) / previous) * 100 if previous != 0 else 0

def card(icon, value, label, color=text_main):
    st.markdown(
        f"""
        <div class="card">
            <div style="font-size:22px">{icon}</div>
            <div style="font-size:20px;font-weight:700;color:{color}">{value}</div>
            <div class="label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

c1, c2, c3, c4, c5 = st.columns(5)
with c1: card("💰", f"{current:.2f}", "Price")
with c2: card("📊", f"{change:.2f}%", "Change",
              "#16a34a" if change >= 0 else "#dc2626")
with c3: card("⬆️", f"{high:.2f}", "High")
with c4: card("⬇️", f"{low:.2f}", "Low")
with c5: card("📦", f"{volume:,}", "Volume")

# ---------------- CHART ----------------
st.markdown("## 📈 Price Trend")
fig = px.line(data, x="Date", y="Close", template=plot_theme)
st.plotly_chart(fig, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download CSV",
    data.to_csv(index=False),
    "stock_data.csv",
    "text/csv"
)

# ---------------- FOOTER ----------------
st.markdown(
    "<hr><center style='color:gray'>Educational Project • Stable Version</center>",
    unsafe_allow_html=True
)
