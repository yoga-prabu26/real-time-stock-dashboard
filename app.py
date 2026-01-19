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

# ---------------- THEME VARIABLES ----------------
if theme == "Dark Mode 🌙":
    bg = "#0f172a"
    card = "#020617"
    text = "#ffffff"
    subtext = "#cbd5f5"
    accent = "#38bdf8"
    plot_theme = "plotly_dark"
else:
    bg = "#f8fafc"
    card = "#ffffff"
    text = "#020617"
    subtext = "#475569"
    accent = "#2563eb"
    plot_theme = "plotly"

# ---------------- CSS ----------------
st.markdown(f"""
<style>
.main {{ background-color: {bg}; }}
.metric-card {{
    background: linear-gradient(145deg, {card}, #020617);
    padding: 22px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}}
.metric-icon {{ font-size: 28px; }}
.metric-value {{ font-size: 30px; font-weight: 700; color: {text}; }}
.metric-label {{
    font-size: 13px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {subtext};
}}
.footer {{
    text-align: center;
    color: {subtext};
    margin-top: 30px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    f"<h1 style='text-align:center;color:{accent};'>📊 Real-Time Stock Market Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown(
    f"<p style='text-align:center;color:{subtext};'>Sector-wise Analysis • Search • Alerts</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# ---------------- SECTORS ----------------
sectors = {
    "IT Sector": {
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "Wipro": "WIPRO.NS",
        "HCL Tech": "HCLTECH.NS"
    },
    "Banking Sector": {
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "SBI": "SBIN.NS"
    },
    "US Tech": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN"
    }
}

# ---------------- SELECTION ----------------
selected_sector = st.sidebar.selectbox("Select Sector", list(sectors.keys()))
search_query = st.sidebar.text_input("🔍 Search Company")

company_list = list(sectors[selected_sector].keys())
if search_query:
    company_list = [c for c in company_list if search_query.lower() in c.lower()]

selected_companies = st.sidebar.multiselect(
    "Select Companies",
    company_list,
    default=company_list[:1]
)

# ---------------- DATE RANGE ----------------
st.sidebar.markdown("### 📅 Date Range")
end_date = date.today()
start_date = end_date - timedelta(days=7)

start_date = st.sidebar.date_input("Start Date", start_date)
end_date = st.sidebar.date_input("End Date", end_date)

if not selected_companies:
    st.warning("Please select at least one company")
    st.stop()

# ---------------- FETCH DATA ----------------
all_data = []

for company in selected_companies:
    ticker = sectors[selected_sector][company]
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date + timedelta(days=1),
        progress=False
    )

    if data.empty:
        continue

    data = data[["Open", "High", "Low", "Close", "Volume"]]
    data["Company"] = company
    data["Time"] = data.index
    all_data.append(data)

if not all_data:
    st.error("No data available for selected options.")
    st.stop()

df = pd.concat(all_data)

# ---------------- MARKET STATUS ----------------
india = pytz.timezone("Asia/Kolkata")
now = datetime.now(india).time()

if time(9, 15) <= now <= time(15, 30):
    st.success("🟢 Market is OPEN")
else:
    st.warning("🔴 Market is CLOSED")

# ---------------- METRICS ----------------
base = df[df["Company"] == selected_companies[0]].copy()

base["Close"] = pd.to_numeric(base["Close"], errors="coerce")
base["High"] = pd.to_numeric(base["High"], errors="coerce")
base["Low"] = pd.to_numeric(base["Low"], errors="coerce")
base["Volume"] = pd.to_numeric(base["Volume"], errors="coerce")

current = base["Close"].dropna().iloc[-1]
previous = base["Close"].dropna().iloc[-2] if len(base["Close"].dropna()) > 1 else current

change = ((current - previous) / previous) * 100 if previous else 0
high = base["High"].max()
low = base["Low"].min()
vol = int(base["Volume"].dropna().iloc[-1])

color = "#16a34a" if change >= 0 else "#dc2626"

c1, c2, c3, c4, c5 = st.columns(5)

c1.markdown(f"<div class='metric-card'><div class='metric-icon'>💰</div><div class='metric-value'>₹ {current:.2f}</div><div class='metric-label'>Price</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><div class='metric-icon'>📊</div><div class='metric-value' style='color:{color};'>{change:.2f}%</div><div class='metric-label'>Change</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><div class='metric-icon'>⬆️</div><div class='metric-value'>₹ {high:.2f}</div><div class='metric-label'>High</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'><div class='metric-icon'>⬇️</div><div class='metric-value'>₹ {low:.2f}</div><div class='metric-label'>Low</div></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='metric-card'><div class='metric-icon'>📦</div><div class='metric-value'>{vol:,}</div><div class='metric-label'>Volume</div></div>", unsafe_allow_html=True)

# ---------------- PRICE ALERT ----------------
st.subheader("🔔 Price Alert")

alert_price = st.number_input(
    f"Set alert price for {selected_companies[0]}",
    min_value=0.0,
    step=1.0
)

if alert_price > 0:
    if current >= alert_price:
        st.success(f"🚨 ALERT: {selected_companies[0]} crossed ₹{alert_price}")
    else:
        st.info(f"ℹ️ Current price ₹{current:.2f} has not crossed ₹{alert_price}")

# ---------------- CSV DOWNLOAD ----------------
st.subheader("⬇️ Download Stock Data")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download as CSV",
    data=csv,
    file_name="stock_data.csv",
    mime="text/csv"
)

# ---------------- CHART ----------------
st.subheader("📈 Stock Price Comparison")

fig = px.line(df, x="Time", y="Close", color="Company", template=plot_theme)
st.plotly_chart(fig, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown(
    "<div class='footer'>Educational Project | Data from public APIs<br>"
    "🔗 GitHub: https://github.com/yoga-prabu26/real-time-stock-dashboard</div>",
    unsafe_allow_html=True
)
