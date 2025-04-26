
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

indices = {
    "S&P 500": "^GSPC",
    "DAX": "^GDAXI",
    "IBEX 35": "^IBEX",
    "Euro Stoxx 50": "^STOXX50E"
}

commodities = {
    "Ouro": "GC=F",
    "Prata": "SI=F",
    "Petróleo Brent": "BZ=F",
    "Petróleo WTI": "CL=F"
}

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

tab1, tab2 = st.tabs(["Índices Globais", "Commodities"])

with tab1:
    st.header("📊 Índices Globais")
    cols = st.columns(len(indices))
    for i, (nome, ticker) in enumerate(indices.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], nome, data)

with tab2:
    st.header("⛏️ Commodities")
    cols = st.columns(len(commodities))
    for i, (nome, ticker) in enumerate(commodities.items()):
        data = get_data(ticker)
        safe_metric_display(cols[i], nome, data)

st.caption("Atualizado a cada 5 minutos | Dados via Yahoo Finance")
