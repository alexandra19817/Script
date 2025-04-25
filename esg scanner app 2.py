import streamlit as st
import requests
import pandas as pd

st.set_page_config("🌱📈 ESG & Wachstums-Scanner", layout="centered")
st.title("🌱📈 ESG & Wachstums-Scanner")

st.subheader("🗂️ Übersicht deiner Aktienanalyse:")

# Tickerliste
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

# API-Zugriff
API_KEY = st.secrets["RAPIDAPI"]["key"]
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "yahoo-finance127.p.rapidapi.com"
}

data_list = []

# Loop durch alle Ticker
for symbol in tickers:
    st.write(f"🔍 Abrufe Daten für: `{symbol}` ...")

    url = f"https://yahoo-finance127.p.rapidapi.com/esg-scores/{symbol}"
    response = requests.get(url, headers=HEADERS)

    st.write(f"📡 Status Code für {symbol}: {response.status_code}")

    if response.status_code == 200:
        try:
            result = response.json()
            esg = result.get("totalEsg", {}).get("raw")
            env = result.get("environmentScore", {}).get("raw")
            soc = result.get("socialScore", {}).get("raw")
            gov = result.get("governanceScore", {}).get("raw")

            data_list.append({
                "Ticker": symbol,
                "🌿 ESG Score": esg,
                "🌍 Environment": env,
                "👥 Social": soc,
                "🏛️ Governance": gov
            })
        except Exception as e:
            st.error(f"❌ Fehler beim Verarbeiten der Antwort für {symbol}: {e}")
    else:
        st.warning(f"⚠️ Fehler beim Abrufen von {symbol} (Status: {response.status_code})")

# DataFrame erstellen und anzeigen
if data_list:
    df = pd.DataFrame(data_list)

    # Beispielbewertung basierend auf ESG
    def bewertung(row):
        if row["🌿 ESG Score"] and row["🌿 ESG Score"] > 80:
            return "✅ Top ESG"
        elif row["🌿 ESG Score"] and row["🌿 ESG Score"] > 60:
            return "🟡 Ok"
        else:
            return "❌ Niedrig"

    df["📌 Bewertung"] = df.apply(bewertung, axis=1)

    st.dataframe(df)

    # Downloadbutton
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("💾 Ergebnisse als CSV speichern", csv, "esg_ergebnisse.csv", "text/csv")
else:
    st.warning("⚠️ Keine Daten geladen. Überprüfe API-Schlüssel und Ticker.")
