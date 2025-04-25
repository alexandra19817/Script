import streamlit as st
import pandas as pd
import requests

# --- Einstellungen ---
st.set_page_config("📈 ESG-Light Aktienbewertung", layout="wide")
st.title("📈 ESG-Light Aktienbewertung")
st.markdown("Analysiere Aktien basierend auf einem eigenen ESG-Light-Score.")

# --- Eingabe ---
ticker_input = st.text_input("🔎 Ticker eingeben (z.B. AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

# --- API-Zugangsdaten ---
API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}

API_URL = "https://stock-pulse.p.rapidapi.com/esg-scores"

if not API_KEY:
    st.error("❌ API-Key fehlt. Bitte stelle sicher, dass dein Key korrekt in den Secrets hinterlegt ist.")
    st.stop()

# --- Ergebnisse sammeln ---
results = []

for ticker in tickers:
    try:
        response = requests.get(API_URL, headers=HEADERS, params={"ticker": ticker})
        if response.status_code == 200:
            data = response.json()
            results.append({
                "Ticker": ticker,
                "Name": data.get("name", "-"),
                "ESG Score": data.get("totalEsg", None),
                "Environment": data.get("environmentScore", None),
                "Social": data.get("socialScore", None),
                "Governance": data.get("governanceScore", None)
            })
        else:
            st.warning(f"⚠️ Fehler beim Abrufen von {ticker} (Status: {response.status_code})")
    except Exception as e:
        st.error(f"❌ Fehler bei {ticker}: {e}")

# --- Anzeige ---
if results:
    df = pd.DataFrame(results)
    st.success("✅ Analyse abgeschlossen")
    st.dataframe(df, use_container_width=True)
else:
    st.error("❌ Keine gültigen Ergebnisse erhalten.")
