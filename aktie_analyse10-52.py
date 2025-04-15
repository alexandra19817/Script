import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import io

st.set_page_config(page_title="📊 Aktienanalyse & Portfolio-Tool", layout="wide")
st.title("📈 Aktienanalyse & Portfolio-Tool")

# 📥 Datei-Upload
uploaded_file = st.file_uploader("Lade deine Excel-Datei hoch (mit den Sheets: Portfolio & Watchlist)", type=["xlsx"])

# Analysefunktion
def analyze_stock(row):
    ticker = row["Ticker"]
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=row["Kaufdatum"])

        if data.empty:
            raise ValueError("Keine Kursdaten verfügbar.")

        current_price = data["Close"].iloc[-1]
        kaufpreis = row["Kaufpreis"]
        anzahl = row["Anzahl"]

        perf_abs = (current_price - kaufpreis) * anzahl
        perf_pct = ((current_price - kaufpreis) / kaufpreis) * 100

        info = stock.info
        dividend = info.get("dividendRate", 0)

        if perf_pct > 25:
            recommendation = "Teilweise verkaufen"
        elif perf_pct < -20:
            recommendation = "Beobachten / Nachkaufen"
        else:
            recommendation = "Halten"

        return pd.Series({
            "Aktueller Kurs": round(current_price, 2),
            "Dividende p.a. (€)": round(dividend, 2) if dividend else 0,
            "Gewinn/Verlust (€)": round(perf_abs, 2),
            "Performance (%)": round(perf_pct, 2),
            "Empfehlung": recommendation
        })

    except Exception as e:
        return pd.Series({
            "Aktueller Kurs": None,
            "Dividende p.a. (€)": None,
            "Gewinn/Verlust (€)": None,
            "Performance (%)": None,
            "Empfehlung": f"Fehler: {str(e)}"
        })

if uploaded_file:
    # 📂 Excel einlesen
    xls = pd.ExcelFile(uploaded_file)
    df_portfolio = pd.read_excel(xls, sheet_name="Portfolio")
    df_watchlist = pd.read_excel(xls, sheet_name="Watchlist")

    st.subheader("📁 Dein Portfolio")
    st.dataframe(df_portfolio, use_container_width=True)

    st.subheader("👁️ Deine Watchlist")
    st.dataframe(df_watchlist, use_container_width=True)

    # 📈 Analyse ausführen
    st.subheader("🧮 Portfolio-Analyse mit Kurs, Dividende & Empfehlungen")
    st.subheader("🔍 Test: Einzelne Analyse")
# Probiere es nur mit der ersten Zeile
first_row = df_portfolio.iloc[0]
result = analyze_stock(first_row)
st.write("Analyse-Ergebnis für die erste Aktie:")
st.write(result)df_analysis = df_portfolio.copy()
    df_analysis = pd.concat([df_portfolio, df_portfolio.apply(analyze_stock, axis=1)], axis=1)
    st.dataframe(df_analysis, use_container_width=True)

    # 📊 Kursverlauf + Kaufpreis visualisieren
    st.subheader("📊 Kursverlauf mit Kaufpreis")
    for index, row in df_portfolio.iterrows():
        ticker = row["Ticker"]
        kaufpreis = row["Kaufpreis"]
        data = yf.Ticker(ticker).history(period="5y")

        if not data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Kurs"))
            fig.add_hline(y=kaufpreis, line_dash="dot", line_color="red", name="Kaufpreis")
            fig.update_layout(
                title=f"{ticker} Kursverlauf mit Kaufpreis",
                xaxis_title="Datum",
                yaxis_title="Kurs (€)"
            )
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{index}")
        else:
            st.warning(f"Keine Kursdaten für {ticker} verfügbar.")

    # 📈 Langfristprognose (CAGR)
    st.subheader("📈 Langfristige Performance (CAGR)")
    cagr_results = []
    for _, row in df_portfolio.iterrows():
        ticker = row["Ticker"]
        data = yf.Ticker(ticker).history(period="10y")
        if len(data) > 1:
            start_price = data["Close"].iloc[0]
            end_price = data["Close"].iloc[-1]
            years = (data.index[-1] - data.index[0]).days / 365
            cagr = ((end_price / start_price) ** (1 / years)) - 1
            cagr_results.append({"Ticker": ticker, "CAGR (%)": round(cagr * 100, 2)})

    if cagr_results:
        st.dataframe(pd.DataFrame(cagr_results), use_container_width=True)

    # 💾 Export-Option
    st.subheader("💾 Ergebnisse als Excel speichern")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_portfolio.to_excel(writer, index=False, sheet_name="Portfolio")
        df_watchlist.to_excel(writer, index=False, sheet_name="Watchlist")
        df_analysis.to_excel(writer, index=False, sheet_name="Analyse")
    excel_buffer.seek(0)

    st.download_button("⬇️ Download aktualisierte Excel-Datei", data=excel_buffer,
                       file_name="portfolio_auswertung.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("⬆️ Bitte lade deine Excel-Datei hoch (mit den Sheets: Portfolio & Watchlist)")
