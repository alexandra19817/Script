import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import io
import datetime
import re

st.set_page_config(page_title="📊 Aktienanalyse & Portfolio-Tool", layout="wide")
st.title("📈 Aktienanalyse & Portfolio-Tool")

# 📥 Datei-Upload
uploaded_file = st.file_uploader("Lade deine Excel-Datei hoch (mit den Sheets: Portfolio & Watchlist)", type=["xlsx"])

# Hilfsfunktion: Kaufpreis bereinigen
def clean_kaufpreis(value):
    try:
        if pd.isnull(value):
            return None
        value_str = str(value).strip()
        if value_str == "" or value_str.lower() in ["nan", "none", "-", "—"]:
            return None
        clean = re.sub(r"[^\d,.-]", "", value_str).replace(",", ".")
        return float(clean)
    except Exception:
        return None

# Analysefunktion
def analyze_stock(row):
    ticker = row["Ticker"]
    try:
        kaufdatum = row["Kaufdatum"]
        if pd.isnull(kaufdatum) or kaufdatum > datetime.datetime.today():
            raise ValueError("Kaufdatum liegt in der Zukunft oder fehlt.")

        stock = yf.Ticker(ticker)
        data = stock.history(start=kaufdatum)

        if data is None or data.empty:
            raise ValueError("Keine Kursdaten verfügbar.")

        current_price = float(data["Close"].iloc[-1])
        kaufpreis = clean_kaufpreis(row["Kaufpreis"])
        if kaufpreis is None:
            raise ValueError(f"Ungültiger Kaufpreis: {row['Kaufpreis']}")

        anzahl = float(row["Anzahl"])
        perf_abs = (current_price - kaufpreis) * anzahl
        perf_pct = ((current_price - kaufpreis) / kaufpreis) * 100

        info = stock.info
        dividend = info.get("dividendRate", 0.0)

        # Empfehlung
        if perf_pct > 50:
            recommendation = "Klar verkaufen"
        elif perf_pct > 25:
            recommendation = "Teilweise verkaufen"
        elif perf_pct >= 0:
            recommendation = "Halten"
        elif perf_pct > -10:
            recommendation = "Beobachten"
        elif perf_pct > -20:
            recommendation = "Beobachten / evtl. Nachkaufen"
        elif perf_pct > -30:
            recommendation = "Beobachten / Risiko prüfen"
        else:
            recommendation = "Verlust begrenzen?"

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


# Verarbeitung nach Upload
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    df_portfolio = pd.read_excel(xls, sheet_name="Portfolio")
    df_watchlist = pd.read_excel(xls, sheet_name="Watchlist")

    # Analyse
    df_analysewerte = df_portfolio.apply(analyze_stock, axis=1)
    df_analysis = df_portfolio.join(df_analysewerte, rsuffix="_analyse")

    # Relevante Ansicht
    relevante_spalten = [
        "Ticker", "Name", "Anzahl", "Kaufpreis", "Aktueller Kurs",
        "Gewinn/Verlust (€)", "Performance (%)", "Dividende p.a. (€)", "Empfehlung"
    ]

    # 📁 Anzeige des analysierten Portfolios
    st.subheader("📁 Dein Portfolio (inkl. Analyse)")
    st.dataframe(df_analysis[relevante_spalten], use_container_width=True)

    # 👁️ Watchlist
    st.subheader("👁️ Deine Watchlist")
    st.dataframe(df_watchlist, use_container_width=True)

    # 📋 Sortierte Analyseansicht
    st.subheader("📋 Auswertung deines Portfolios (sortiert nach Performance)")

    # 📋 Sortierte Analyseansicht
st.subheader("📋 Auswertung deines Portfolios (sortiert nach Performance)")

# 🛡️ Sicherheitscheck
perf_col_name = "Performance (%)"
if "df_analysis" not in locals() or perf_col_name not in df_analysis.columns:
    st.error(f"❌ Analyse fehlgeschlagen – '{perf_col_name}' fehlt. Aktuelle Spalten:")
    st.write(df_analysis.columns.tolist() if "df_analysis" in locals() else "DataFrame 'df_analysis' nicht vorhanden.")
    st.stop()

# ✅ Sortierte Version für Analyse
df_analysis_view = df_analysis[relevante_spalten].sort_values(by=perf_col_name, ascending=False, na_position="last")

# 🔍 Suchfeld
search_query = st.text_input("🔎 Aktie suchen (Ticker oder Name)", "")

# 🔄 Gefilterte Ansicht
filtered_df = df_analysis_view[
    df_analysis_view["Ticker"].str.contains(search_query, case=False, na=False) |
    df_analysis_view["Name"].astype(str).str.contains(search_query, case=False, na=False)
]

st.dataframe(filtered_df, use_container_width=True)

# 📊 Balkendiagramm Performance
if not filtered_df.empty:
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Bar(
        x=filtered_df["Ticker"],
        y=filtered_df["Performance (%)"],
        text=filtered_df["Performance (%)"],
        textposition="auto"
    ))
    fig_perf.update_layout(
        title="📊 Performance pro Aktie",
        xaxis_title="Ticker",
        yaxis_title="Performance (%)"
    )
    st.plotly_chart(fig_perf, use_container_width=True, key=f"performance_chart_{search_query}")

# 💡 Hinweise bei extremen Fällen
extreme_winners = filtered_df[filtered_df["Performance (%)"] > 100]
extreme_losers = filtered_df[filtered_df["Performance (%)"] < -50]

if not extreme_winners.empty:
    st.success("🚀 Diese Aktien haben über **+100 % Performance** erreicht!")
    st.dataframe(extreme_winners[["Ticker", "Name", "Performance (%)", "Empfehlung"]])

if not extreme_losers.empty:
    st.error("⚠️ Diese Aktien haben über **–50 % Verlust** – prüfe ob Handlungsbedarf besteht.")
    st.dataframe(extreme_losers[["Ticker", "Name", "Performance (%)", "Empfehlung"]])
    # 📊 Kursverläufe
    st.subheader("📊 Kursverlauf mit Kaufpreis")
    for index, row in df_portfolio.iterrows():
        ticker = row["Ticker"]
        kaufpreis = clean_kaufpreis(row["Kaufpreis"])
        data = yf.Ticker(ticker).history(period="5y")

        if not data.empty and kaufpreis is not None:
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
            st.warning(f"⚠️ Keine Kursdaten für {ticker} verfügbar oder Kaufpreis fehlt.")

    # 📈 CAGR-Berechnung
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

    # 💾 Excel-Export
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
