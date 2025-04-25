import streamlit as st
import pandas as pd
import requests

# Titel der App
st.title("🌱📈 ESG & Wachstums-Scanner")

# Beispielhafte Tickerliste (Top 10, erweiterbar auf 50-100)
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

# API-Header (deinen API-Key hier einfügen oder via st.secrets laden)
headers = {
    "X-RapidAPI-Key": st.secrets.get("RAPIDAPI", {}).get("key", ""),
    "X-RapidAPI-Host": "yahoo-finance127.p.rapidapi.com"
}

# Hilfsfunktion zum Datenabruf und Berechnung
def get_stock_data(ticker):
    url = f"https://yahoo-finance127.p.rapidapi.com/stock/v2/get-summary?symbol={ticker}&region=US"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()
    fin_data = data.get("financialData", {})
    summary_data = data.get("price", {})

    return {
        "Ticker": ticker,
        "Aktienkurs ($)": summary_data.get("regularMarketPrice", {}).get("raw"),
        "Marktkapitalisierung ($)": summary_data.get("marketCap", {}).get("raw"),
        "Branche": summary_data.get("sector", "N/A"),
        "KGV": fin_data.get("trailingPE", {}).get("raw"),
        "EPS": fin_data.get("earningsPerShare", {}).get("raw"),
        "Umsatz (Mrd $)": (fin_data.get("totalRevenue", {}).get("raw", 0)) / 1e9,
        "Gewinnmarge (%)": (fin_data.get("profitMargins", {}).get("raw", 0)) * 100,
        "Schuldenquote (%)": fin_data.get("debtToEquity", {}).get("raw"),
        "Dividendenrendite (%)": (fin_data.get("dividendYield", {}).get("raw", 0)) * 100,
        "Performance YTD (%)": fin_data.get("52WeekChange", {}).get("raw", 0) * 100,
    }

# Daten sammeln
results = []
for ticker in ticker_list:
    stock_info = get_stock_data(ticker)
    if stock_info:
        results.append(stock_info)

# DataFrame erstellen
df = pd.DataFrame(results)

# Automatische Bewertung basierend auf Regeln
def bewertung(row):
    try:
        if pd.notnull(row["KGV"]) and pd.notnull(row["Gewinnmarge (%)"]) and pd.notnull(row["Schuldenquote (%)"]):
            if row["KGV"] < 20 and row["Gewinnmarge (%)"] > 10 and row["Schuldenquote (%)"] < 50:
                return "✅ Kaufen"
            elif 20 <= row["KGV"] <= 30:
                return "⚠️ Beobachten"
            else:
                return "❌ Riskant"
        else:
            return "❓ Keine ausreichenden Daten"
    except:
        return "❓ Fehler bei Bewertung"

df["📌 Bewertung"] = df.apply(bewertung, axis=1)

# Farbliche Darstellung
def highlight_rows(row):
    color = "white"
    if row["📌 Bewertung"] == "✅ Kaufen":
        color = "#d4edda"  # Grün
    elif row["📌 Bewertung"] == "⚠️ Beobachten":
        color = "#fff3cd"  # Gelb
    elif row["📌 Bewertung"] == "❌ Riskant":
        color = "#f8d7da"  # Rot
    return [f"background-color: {color}" for _ in row]

# Ausgabe
st.subheader("📋 Übersicht deiner Aktienanalyse:")
st.dataframe(df.style.apply(highlight_rows, axis=1), use_container_width=True)

# Download-Option
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Ergebnisse als CSV speichern",
    data=csv,
    file_name='esg_growth_scanner.csv',
    mime='text/csv'
)
