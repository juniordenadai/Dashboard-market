
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import math

st.set_page_config(layout="wide", page_title="Dashboard de Mercado em Tempo Real")
st.title("📈 Dashboard de Mercado em Tempo Real")

@st.cache_data(ttl=300)
def get_data(ticker, period='5d', interval='1h'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Erro ao buscar dados para {ticker}: {str(e)}")
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
                fig = px.line(data, x="Datetime", y="Close", title=f"{label} - Últimos dias")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            col.metric(label=label, value="Erro", delta="")
    else:
        col.metric(label=label, value="Sem dados", delta="")

# Tickers por categoria
indices_europeus = {
    "DAX (Alemanha)": "^GDAXI",
    "IBEX 35 (Espanha)": "^IBEX",
    "CAC 40 (França)": "^FCHI",
    "FTSE MIB (Itália)": "FTSEMIB.MI",
    "FTSE 100 (Reino Unido)": "^FTSE",
    "MOEX (Rússia)": "IMOEX.ME",
    "OMXS30 (Suécia)": "^OMXS30",
    "SMI (Suíça)": "^SSMI",
    "Euro Stoxx 50": "^STOXX50E"
}

indices_asiaticos = {
    "Nikkei 225 (Japão)": "^N225",
    "Hang Seng (Hong Kong)": "^HSI",
    "Shanghai Composite (China)": "000001.SS",
    "KOSPI (Coreia do Sul)": "^KS11",
    "Sensex (Índia)": "^BSESN"
}

commodities = {
    "Ouro": "GC=F",
    "Prata": "SI=F",
    "Cobre": "HG=F",
    "Minério de Ferro (via ETF)": "SDS",  # Substituto temporário
    "Petróleo Brent": "BZ=F",
    "Petróleo WTI": "CL=F"
}

criptos = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "XRP": "XRP-USD"
}

tabs = st.tabs(["Índices Europeus", "Índices Asiáticos", "Commodities", "Criptomoedas"])

# Aba Europa
with tabs[0]:
    st.header("🌍 Índices Europeus")
    cols = st.columns(len(indices_europeus))
    for i, (nome, ticker) in enumerate(indices_europeus.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], nome, data)

# Aba Ásia
with tabs[1]:
    st.header("🌏 Índices Asiáticos")
    cols = st.columns(len(indices_asiaticos))
    for i, (nome, ticker) in enumerate(indices_asiaticos.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], nome, data)

# Aba Commodities
with tabs[2]:
    st.header("⛏️ Commodities")
    cols = st.columns(len(commodities))
    for i, (nome, ticker) in enumerate(commodities.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], nome, data)

# Aba Criptomoedas
with tabs[3]:
    st.header("₿ Criptomoedas")
    cols = st.columns(len(criptos))
    for i, (nome, ticker) in enumerate(criptos.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], nome, data)

st.caption("Atualizado a cada 5 minutos | Dados via Yahoo Finance e APIs públicas")
