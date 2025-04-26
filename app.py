import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import math

st.set_page_config(layout="wide", page_title="Real-Time Market Dashboard", initial_sidebar_state="expanded")

st.title("Real-Time Market Dashboard")

@st.cache_data(ttl=300)
def get_data(ticker, period='5d', interval=None):
    try:
        if ticker.startswith("^") or ticker.endswith(".SS") or ticker.endswith(".ME") or ticker in us_futures.values():
            interval = interval or "1d"
        else:
            interval = interval or "1h"
        data = yf.download(ticker, period=period, interval=interval)
        data.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in data.columns]
        data.reset_index(inplace=True)
        return data
    except Exception:
        return pd.DataFrame()

def safe_metric_display(col, label, ticker, data):
    if data.empty or len(data) < 2:
        col.metric(label=label, value="No data", delta="")
        return

    possible_close_cols = [f"Close {ticker}", "Close"]
    close_col = next((c for c in possible_close_cols if c in data.columns), None)

    if close_col:
        try:
            current = data[close_col].iloc[-1]
            previous = data[close_col].iloc[-2]
            change = ((current - previous) / previous) * 100 if previous != 0 else 0
            col.metric(label=label, value=f"{current:,.2f}", delta=f"{change:.2f}%")
        except Exception:
            col.metric(label=label, value="Error", delta="")
    else:
        col.metric(label=label, value="No data", delta="")

# Tickers by category
market_indices = {
    "DAX (Germany)": "^GDAXI",
    "IBEX 35 (Spain)": "^IBEX",
    "CAC 40 (France)": "^FCHI",
    "FTSE MIB (Italy)": "FTSEMIB.MI",
    "FTSE 100 (United Kingdom)": "^FTSE",
    "MOEX (Russia)": "IMOEX.ME",
    "OMXS30 (Sweden)": "^OMXS30",
    "SMI (Switzerland)": "^SSMI",
    "Euro Stoxx 50": "^STOXX50E",
    "Nikkei 225 (Japan)": "^N225",
    "Hang Seng (Hong Kong)": "^HSI",
    "Shanghai Composite (China)": "000001.SS",
    "KOSPI (South Korea)": "^KS11",
    "Sensex (India)": "^BSESN",
    "S&P 500 Futures": "^GSPC",
    "Nasdaq Futures": "^IXIC",
    "Dow Jones Futures": "^DJI",
    "Russell 2000 Futures": "^RUT"
}

commodities = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Iron Ore (SGX)": "TIO1!",
    "Brent Crude Oil": "BZ=F",
    "WTI Crude Oil": "CL=F"
}

cryptos = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "XRP": "XRP-USD"
}

tabs = st.tabs(["Traditional Markets", "Commodities", "Cryptocurrencies", "Crypto Market Profile"])

# Traditional Markets Tab
with tabs[0]:
    st.header("Traditional Market Indices")
    rows = list(market_indices.items())
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(rows):
                name, ticker = rows[i + j]
                data = get_data(ticker)
                safe_metric_display(cols[j], name, ticker, data)

# Commodities Tab
with tabs[1]:
    st.header("Commodities")
    rows = list(commodities.items())
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(rows):
                name, ticker = rows[i + j]
                data = get_data(ticker)
                safe_metric_display(cols[j], name, ticker, data)

# Cryptos Tab
with tabs[2]:
    st.header("Cryptocurrencies")
    rows = list(cryptos.items())
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(rows):
                name, ticker = rows[i + j]
                data = get_data(ticker)
                safe_metric_display(cols[j], name, ticker, data)

# Crypto Market Profile Tab
with tabs[3]:
    st.header("Crypto Market Profile")
    col1, col2 = st.columns(2)

    with col1:
        selected_crypto = st.selectbox("Select Cryptocurrency:", list(cryptos.keys()))
    with col2:
        selected_period = st.selectbox("Select Period:", ["7d", "30d", "90d", "180d"])

    ticker = cryptos[selected_crypto]
    period_mapping = {"7d": "7d", "30d": "30d", "90d": "90d", "180d": "180d"}

    crypto_data = get_data(ticker, period=period_mapping[selected_period], interval='1h')

    possible_close_cols = [f"Close {ticker}", "Close"]
    close_col = next((c for c in possible_close_cols if c in crypto_data.columns), None)

    if close_col:
        st.subheader(f"{selected_crypto} Price Chart")
        fig_price = px.line(crypto_data, x="Datetime", y=close_col, title=f"{selected_crypto} Price - Last {selected_period}", template="plotly_dark")
        st.plotly_chart(fig_price, use_container_width=True)

        st.subheader(f"{selected_crypto} Volume Profile")
        possible_volume_cols = [f"Volume {ticker}", "Volume"]
        volume_col = next((c for c in possible_volume_cols if c in crypto_data.columns), None)

        if volume_col:
            hist_data = pd.cut(crypto_data[close_col], bins=50)
            volume_profile = crypto_data.groupby(hist_data)[volume_col].sum().reset_index()
            volume_profile['price_bin'] = volume_profile[hist_data.name].apply(lambda x: x.mid)
            fig_volume = px.bar(volume_profile, x=volume_col, y="price_bin", orientation='h', title=f"{selected_crypto} Volume by Price", template="plotly_dark")
            fig_volume.update_layout(yaxis_title="Price Range")
            st.plotly_chart(fig_volume, use_container_width=True)
    else:
        st.error("No data available for this selection.")

st.caption("Updated every 5 minutes | Data via Yahoo Finance and public APIs")
