import yfinance as yf
import plotly.graph_objects as go

import streamlit as st
import pandas as pd

df_portfolio = pd.DataFrame([
    {"Ticker": "AAPL", "Kaufpreis": 120},
    {"Ticker": "MSFT", "Kaufpreis": 230}
])

st.subheader("📊 Kursverlauf & Kaufpreis")

for _, row in df_portfolio.iterrows():
    ticker = row["Ticker"]
    data = yf.Ticker(ticker).history(period="5y")

    if not data.empty:
        kaufpreis = row["Kaufpreis"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Kurs"))
        fig.add_hline(y=kaufpreis, line_dash="dot", line_color="red", name="Kaufpreis")
        fig.update_layout(
            title=f"{ticker} Kursverlauf mit Kaufpreis",
            xaxis_title="Datum",
            yaxis_title="Kurs (€)"
        )
        st.plotly_chart(fig, use_container_width=True)
