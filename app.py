import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import math

st.set_page_config(layout="wide", page_title="Real-Time Market Dashboard", initial_sidebar_state="expanded")

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: #c7d5e0;
}
</style>
""", unsafe_allow_html=True)

st.title("Real-Time Market Dashboard")

@st.cache_data(ttl=300)
def get_data(ticker, period='5d', interval='1h'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()

def safe_metric_display(col, label, data):
    if not data.empty and "Close" in data.columns and len(data["Close"]) >= 2:
        try:
            current = float(data["Close"].iloc[-1])
            previous = float(data["Close"].iloc[-2])
            change = ((current - previous) / previous) * 100 if previous != 0 else 0
            if math.isnan(current) or math.isnan(change):
                col.metric(label=label, value="N/A", delta="N/A")
            else:
                col.metric(label=label, value=f"{current:,.2f}", delta=f"{change:.2f}%")

                if "Datetime" in data.columns:
                    x_axis = "Datetime"
                elif "Date" in data.columns:
                    x_axis = "Date"
                else:
                    x_axis = data.index.name if data.index.name else data.index

                fig = px.line(data, x=x_axis, y="Close", title=f"{label} - Last Days", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            col.metric(label=label, value="Error", delta="")
    else:
        col.metric(label=label, value="No data", delta="")

# Tickers by category
european_indices = {
    "DAX (Germany)": "^GDAXI",
    "IBEX 35 (Spain)": "^IBEX",
    "CAC 40 (France)": "^FCHI",
    "FTSE MIB (Italy)": "FTSEMIB.MI",
    "FTSE 100 (United Kingdom)": "^FTSE",
    "MOEX (Russia)": "IMOEX.ME",
    "OMXS30 (Sweden)": "^OMXS30",
    "SMI (Switzerland)": "^SSMI",
    "Euro Stoxx 50": "^STOXX50E"
}

asian_indices = {
    "Nikkei 225 (Japan)": "^N225",
    "Hang Seng (Hong Kong)": "^HSI",
    "Shanghai Composite (China)": "000001.SS",
    "KOSPI (South Korea)": "^KS11",
    "Sensex (India)": "^BSESN"
}

commodities = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Iron Ore (SGX)": "TIO1!",  # Correction applied here
    "Brent Crude Oil": "BZ=F",
    "WTI Crude Oil": "CL=F"
}

cryptos = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "XRP": "XRP-USD"
}

us_futures = {
    "S&P 500 Futures": "^GSPC",
    "Nasdaq Futures": "^IXIC",
    "Dow Jones Futures": "^DJI",
    "Russell 2000 Futures": "^RUT"
}

tabs = st.tabs(["European Indices", "Asian Indices", "Commodities", "Cryptocurrencies", "US Futures", "Crypto Market Profile"])

# Europe Tab
with tabs[0]:
    st.header("\ud83c\udf0d European Indices")
    cols = st.columns(len(european_indices))
    for i, (name, ticker) in enumerate(european_indices.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], name, data)

# Asia Tab
with tabs[1]:
    st.header("\ud83c\udf0f Asian Indices")
    cols = st.columns(len(asian_indices))
    for i, (name, ticker) in enumerate(asian_indices.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], name, data)

# Commodities Tab
with tabs[2]:
    st.header("\u26cf\ufe0f Commodities")
    cols = st.columns(len(commodities))
    for i, (name, ticker) in enumerate(commodities.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], name, data)

# Cryptos Tab
with tabs[3]:
    st.header("\u20bf Cryptocurrencies")
    cols = st.columns(len(cryptos))
    for i, (name, ticker) in enumerate(cryptos.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], name, data)

# US Futures Tab
with tabs[4]:
    st.header("\ud83c\uddfa\ud83c\uddf8 US Futures")
    cols = st.columns(len(us_futures))
    for i, (name, ticker) in enumerate(us_futures.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], name, data)

# Crypto Market Profile Tab
with tabs[5]:
    st.header("\ud83d\udcca Crypto Market Profile")

    selected_crypto = st.selectbox("Select Cryptocurrency:", list(cryptos.keys()))
    selected_period = st.selectbox("Select Period:", ["7d", "30d", "90d", "180d"])

    ticker = cryptos[selected_crypto]
    period_mapping = {"7d": "7d", "30d": "30d", "90d": "90d", "180d": "180d"}

    crypto_data = get_data(ticker, period=period_mapping[selected_period], interval='1h')

    if not crypto_data.empty:
        st.subheader(f"{selected_crypto} Price Chart")
        fig_price = px.line(crypto_data, x=crypto_data.columns[0], y="Close", title=f"{selected_crypto} Price - Last {selected_period}", template="plotly_dark")
        st.plotly_chart(fig_price, use_container_width=True)

        st.subheader(f"{selected_crypto} Volume Profile")
        hist_data = pd.cut(crypto_data['Close'], bins=50)
        volume_profile = crypto_data.groupby(hist_data)['Volume'].sum()
        volume_profile = volume_profile.reset_index()
        fig_volume = px.bar(volume_profile, x="Volume", y="Close", orientation='h', title=f"{selected_crypto} Volume by Price", template="plotly_dark")
        st.plotly_chart(fig_volume, use_container_width=True)
    else:
        st.error("No data available for this selection.")

st.caption("Updated every 5 minutes | Data via Yahoo Finance and public APIs")
