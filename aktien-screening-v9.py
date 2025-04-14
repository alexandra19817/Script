import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="📈 Portfolio Analyzer+", layout="wide")
st.title("📊 Persönliches Portfolio Analyse Tool mit Erweiterungen")

# Sprachwahl
lang = st.radio("Sprache / Language", ["Deutsch", "English"], horizontal=True)

# Datei-Upload
uploaded_file = st.file_uploader("📤 Portfolio-Datei im Excel-Format hochladen (.xlsx):", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Ticker"] = df["Ticker"].str.upper()

    st.info("🔄 Kursdaten und Fundamentaldaten werden geladen...", icon="⏳")
    live_data = {}
    for ticker in df["Ticker"]:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="10y")

            current_price = info.get("currentPrice", None)
            dividend_yield = info.get("dividendYield", 0.0)
            short_name = info.get("shortName", ticker)

            if hist.empty or not current_price:
                continue

            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            years = (hist.index[-1] - hist.index[0]).days / 365
            cagr = ((end_price / start_price) ** (1 / years)) - 1

            live_data[ticker] = {
                "price": current_price,
                "div_yield": dividend_yield,
                "name": short_name,
                "history": hist,
                "cagr": round(cagr * 100, 2)
            }
        except:
            live_data[ticker] = {}

    df["Name"] = df["Ticker"].map(lambda x: live_data.get(x, {}).get("name", x))
    df["Aktueller Kurs (€)"] = df["Ticker"].map(lambda x: live_data.get(x, {}).get("price"))
    df["Dividendenrendite (%)"] = df["Ticker"].map(lambda x: round(live_data.get(x, {}).get("div_yield", 0) * 100, 2))
    df["CAGR (10J) %"] = df["Ticker"].map(lambda x: live_data.get(x, {}).get("cagr"))

    df["Investiert (€)"] = df["Anzahl"] * df["Kaufpreis (€)"]
    df["Wert aktuell (€)"] = df["Anzahl"] * df["Aktueller Kurs (€)"]
    df["Gewinn/Verlust (€)"] = df["Wert aktuell (€)"] - df["Investiert (€)"]
    df["Gewinn/Verlust (%)"] = round((df["Gewinn/Verlust (€)"] / df["Investiert (€)"]) * 100, 2)

    # Empfehlung auf Basis von Performance und Ziel
    def recommendation(row):
        if row["Ziel"] == "Langfristig":
            if row["Gewinn/Verlust (%)"] < -20:
                return "Nachkaufen"
            elif row["Gewinn/Verlust (%)"] > 50:
                return "Halten"
            else:
                return "Halten"
        else:
            if row["Gewinn/Verlust (%)"] > 20:
                return "Verkaufen"
            elif row["Gewinn/Verlust (%)"] < -10:
                return "Vermeiden"
            else:
                return "Beobachten"
    df["Empfehlung"] = df.apply(recommendation, axis=1)

    # Ausgabe der Tabelle
    st.subheader("📋 Portfolio Übersicht mit Empfehlungen")
    st.dataframe(df, use_container_width=True)

    # Gewinn/Verlust Diagramm
    st.subheader("📈 Gewinn / Verlust je Position")
    fig = px.bar(df, x="Ticker", y="Gewinn/Verlust (€)", color="Empfehlung", hover_data=["Name", "Ziel", "Kommentar"])
    st.plotly_chart(fig, use_container_width=True)

    # Dividendenübersicht
    st.subheader("💰 Dividendenanalyse")
    df["Erwartete Dividende (€)"] = df["Wert aktuell (€)"] * (df["Dividendenrendite (%)"] / 100)
    st.dataframe(df[["Ticker", "Wert aktuell (€)", "Dividendenrendite (%)", "Erwartete Dividende (€)"]], use_container_width=True)

    # Langfrist-Prognose
    st.subheader("📈 Langfristige Wachstumsprojektion (CAGR Simulation)")
    years_projection = st.slider("Zeitraum für Prognose (Jahre)", min_value=1, max_value=20, value=10)
    projection_fig = go.Figure()
    for _, row in df.iterrows():
        if pd.notna(row["CAGR (10J) %"]) and pd.notna(row["Wert aktuell (€)"]):
            future_value = row["Wert aktuell (€)"] * ((1 + (row["CAGR (10J) %"] / 100)) ** years_projection)
            projection_fig.add_trace(go.Bar(name=row["Ticker"], x=[row["Ticker"]], y=[future_value]))
    projection_fig.update_layout(title=f"📈 Prognose Portfolio-Wert in {years_projection} Jahren", yaxis_title="€")
    st.plotly_chart(projection_fig, use_container_width=True)

    # Historischer Chartvergleich
    st.subheader("📉 Kursentwicklung seit Kauf")
    selected_ticker = st.selectbox("Wähle einen Ticker", df["Ticker"].unique())
    if selected_ticker in live_data and "history" in live_data[selected_ticker]:
        hist = live_data[selected_ticker]["history"]
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name=selected_ticker))
        fig_hist.update_layout(title=f"Kursverlauf: {selected_ticker}", xaxis_title="Datum", yaxis_title="Kurs")
        st.plotly_chart(fig_hist, use_container_width=True)

    # Export mit Empfehlungen
    st.subheader("⬇️ Analyse speichern")
    export_file = df.copy()
    export_buffer = pd.ExcelWriter("Portfolio_Analyse_Ergebnis.xlsx", engine="openpyxl")
    export_file.to_excel(export_buffer, index=False)
    export_buffer.close()
    with open("Portfolio_Analyse_Ergebnis.xlsx", "rb") as f:
        st.download_button("📥 Analyse als Excel herunterladen", f, file_name="Portfolio_Analyse_Ergebnis.xlsx")

else:
    st.info("⬆️ Bitte lade deine Portfolio-Datei hoch, um loszulegen.")
