import yfinance as yf
import pandas as pd
import streamlit as st
import io
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Aktien Screening", layout="wide")
st.title("\U0001F4C8 Automatisches Aktien-Screening Tool")

# Sprachumschaltung
lang = st.radio("Sprache / Language", ["Deutsch", "English"], horizontal=True)

# Nutzerdefinierte Tickerauswahl
default_tickers = "EVT.DE, AAPL, MSFT"
ticker_label = "Ticker eingeben (z. B. AAPL, EVT.DE):" if lang == "Deutsch" else "Enter tickers (e.g., AAPL, EVT.DE):"
user_input = st.text_input(ticker_label, value=default_tickers)
tickers = [x.strip() for x in user_input.split(",") if x.strip()]

# Zeitraum-Auswahl
period_map = {"12 Monate": "1y", "5 Jahre": "5y", "10 Jahre": "10y"}
period_label = "Zeitraum auswählen:" if lang == "Deutsch" else "Select time period:"
selected_period_key = st.selectbox(period_label, list(period_map.keys()))
selected_period = period_map[selected_period_key]

# Funktion zur Datenabfrage
def get_stock_data(tickers):
    rows = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            hist = stock.history(period="1y")
            perf_1y = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100 if not hist.empty else None

            pe = info.get("trailingPE")
            growth_est = info.get("earningsQuarterlyGrowth") or 0.1
            fair_pe = round(15 + growth_est * 100, 2) if growth_est else None

            roe = info.get("returnOnEquity", 0)
            roa = info.get("returnOnAssets", 0)
            debt = info.get("totalDebt")
            assets = info.get("totalAssets")
            verschuldung = round((debt / assets) * 100, 2) if debt and assets else None
            revenue = info.get("totalRevenue")
            div_yield = info.get("dividendYield", 0)
            beta = info.get("beta")
            price = info.get("currentPrice")
            target = info.get("targetMeanPrice")
            name = info.get("shortName") or ticker

            # Bewertungsempfehlung
            if all([roa, verschuldung, beta]):
                if roa >= 12 and verschuldung < 100 and beta < 1.2:
                    recommendation = "Kaufen ✅" if lang == "Deutsch" else "Buy ✅"
                elif roa >= 6:
                    recommendation = "Beobachten 👀" if lang == "Deutsch" else "Watch 👀"
                elif verschuldung > 200 or roa < 3:
                    recommendation = "Nicht kaufen ❌" if lang == "Deutsch" else "Do not buy ❌"
                else:
                    recommendation = "Unklar 🤷‍♂️" if lang == "Deutsch" else "Unclear 🤷‍♂️"
            else:
                recommendation = "Unklar 🤷‍♂️" if lang == "Deutsch" else "Unclear 🤷‍♂️"

            row = {
                "Unternehmen" if lang == "Deutsch" else "Company": name,
                "Ticker": ticker,
                "Umsatz (Mrd. €)" if lang == "Deutsch" else "Revenue (€bn)": round(revenue / 1e9, 2) if revenue else None,
                "KGV (P/E)": pe,
                "Faires KGV" if lang == "Deutsch" else "Fair P/E": fair_pe,
                "ROE (%)": round(roe * 100, 2) if roe else None,
                "ROA (%)": round(roa * 100, 2) if roa else None,
                "Verschuldungsgrad (%)" if lang == "Deutsch" else "Debt Ratio (%)": verschuldung,
                "Dividendenrendite (%)" if lang == "Deutsch" else "Dividend Yield (%)": round(div_yield * 100, 2) if div_yield else None,
                "Beta": beta,
                "Kurs" if lang == "Deutsch" else "Price": price,
                "Kursziel" if lang == "Deutsch" else "Target Price": target,
                "Performance 1J (%)": round(perf_1y, 2) if perf_1y else None,
                "Empfehlung" if lang == "Deutsch" else "Recommendation": recommendation
            }

            rows.append(row)
        except Exception as e:
            st.warning(f"Fehler bei {ticker}: {e}")

    return pd.DataFrame(rows)

# Tabelle generieren
df = get_stock_data(tickers)
st.dataframe(df, use_container_width=True)

# Kursverlauf-Grafik
st.subheader("📊 Kursverlauf" if lang == "Deutsch" else "📊 Price Chart")
selected_compare = st.multiselect(
    "Unternehmen für Vergleich auswählen:" if lang == "Deutsch" else "Select companies to compare:",
    df["Ticker"].tolist(),
    default=df["Ticker"].tolist()[:2]
)

if selected_compare:
    fig = go.Figure()
    for ticker in selected_compare:
        hist = yf.Ticker(ticker).history(period=selected_period)
        if not hist.empty:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name=ticker))
    fig.update_layout(title="Kursverlauf", xaxis_title="Datum", yaxis_title="Kurs (€)")
    st.plotly_chart(fig, use_container_width=True)

# Langfristige CAGR-Simulation
st.subheader("📈 Langfristige CAGR-Simulation (10 Jahre)" if lang == "Deutsch" else "📈 Long-Term CAGR Simulation")
cagr_fig = go.Figure()
for ticker in selected_compare:
    data = yf.Ticker(ticker).history(period="10y")
    if len(data) > 1:
        start = data["Close"].iloc[0]
        end = data["Close"].iloc[-1]
        years = (data.index[-1] - data.index[0]).days / 365
        cagr = ((end / start) ** (1 / years)) - 1
        cagr_fig.add_trace(go.Bar(name=ticker, x=[ticker], y=[round(cagr * 100, 2)]))
cagr_fig.update_layout(title="10-Jahres-Wachstum (%)", yaxis_title="CAGR % p.a.")
st.plotly_chart(cagr_fig, use_container_width=True)

# Export als Excel
excel_buffer = io.BytesIO()
df.to_excel(excel_buffer, index=False, engine="openpyxl")
excel_buffer.seek(0)
st.download_button(
    label="📥 Excel herunterladen" if lang == "Deutsch" else "📥 Download Excel",
    data=excel_buffer,
    file_name="aktien_screening_export.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Quelle
st.caption(f"📊 Datenquelle: Yahoo Finance | Stand: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
