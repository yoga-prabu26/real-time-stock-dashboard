import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, time, date, timedelta
import pytz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Real-Time Stock Market Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Settings")
theme = st.sidebar.radio("Theme", ["Dark Mode 🌙", "Light Mode ☀️"])
refresh = st.sidebar.selectbox("Auto Refresh", ["Manual", "30 sec", "60 sec"])

if refresh != "Manual":
    st.autorefresh(interval=int(refresh.split()[0]) * 1000, key="refresh")

plot_theme = "plotly_dark" if "Dark" in theme else "plotly"

# ---------------- HEADER ----------------
st.title("📊 Real-Time Stock Market Dashboard")
st.caption("Sector-wise Analysis • Search • Alerts")

# ---------------- SECTORS (MORE COMPANIES) ----------------
sectors = {
    "IT Sector (India)": {
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "Wipro": "WIPRO.NS",
        "HCL Tech": "HCLTECH.NS",
        "LTIMindtree": "LTIM.NS",
        "Tech Mahindra": "TECHM.NS"
    },
    "Banking Sector (India)": {
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "SBI": "SBIN.NS",
        "Axis Bank": "AXISBANK.NS",
        "Kotak Bank": "KOTAKBANK.NS"
    },
    "US Tech": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN",
        "Google": "GOOGL",
        "Tesla": "TSLA",
        "Meta": "META"
    }
}

# ---------------- USER INPUT ----------------
selected_sector = st.sidebar.selectbox("Select Sector", list(sectors.keys()))
companies = sectors[selected_sector]

selected_company = st.sidebar.selectbox(
    "Select Company", list(companies.keys())
)

end_date = date.today()
start_date = end_date - timedelta(days=7)

# ---------------- FETCH DATA (SAFE WAY) ----------------
ticker = companies[selected_company]

data = yf.download(
    ticker,
    start=start_date,
    end=end_date + timedelta(days=1),
    progress=False
)

if data.empty:
    st.error("No data available for this stock.")
    st.stop()

# 🔒 FLATTEN COLUMNS (IMPORTANT)
data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
data = data.reset_index()

# ---------------- MARKET STATUS ----------------
india = pytz.timezone("Asia/Kolkata")
now = datetime.now(india).time()

if time(9, 15) <= now <= time(15, 30):
    st.success("🟢 Market is OPEN")
else:
    st.warning("🔴 Market is CLOSED")

# ---------------- METRICS (100% SAFE) ----------------
close_prices = data["Close"].values
high_prices = data["High"].values
low_prices = data["Low"].values
volumes = data["Volume"].values

current = float(close_prices[-1])
previous = float(close_prices[-2]) if len(close_prices) > 1 else current
change = ((current - previous) / previous) * 100 if previous != 0 else 0

high = float(high_prices.max())
low = float(low_prices.min())
vol = int(volumes[-1])

color = "green" if change >= 0 else "red"

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("💰 Price", f"{current:.2f}")
c2.metric("📊 Change %", f"{change:.2f}%")
c3.metric("⬆️ High", f"{high:.2f}")
c4.metric("⬇️ Low", f"{low:.2f}")
c5.metric("📦 Volume", f"{vol:,}")

# ---------------- PRICE ALERT ----------------
st.subheader("🔔 Price Alert")
alert = st.number_input("Alert when price crosses:", min_value=0.0)

if alert > 0:
    if current >= alert:
        st.success(f"🚨 ALERT: {selected_company} crossed {alert}")
    else:
        st.info("Alert not triggered yet")

# ---------------- CHART ----------------
st.subheader("📈 Stock Price Trend")

fig = px.line(
    data,
    x="Date",
    y="Close",
    title=f"{selected_company} Price Movement",
    template=plot_theme
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.subheader("⬇️ Download Data")
st.download_button(
    "Download CSV",
    data.to_csv(index=False),
    "stock_data.csv",
    "text/csv"
)

# ---------------- FOOTER ----------------
st.caption(
    "Educational Project | Data from Yahoo Finance | "
    "GitHub: https://github.com/yoga-prabu26/real-time-stock-dashboard"
)
