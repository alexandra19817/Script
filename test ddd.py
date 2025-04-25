import streamlit as st
import pandas as pd
import requests

# --- Einstellungen ---
st.set_page_config("📋 ESG-Light Aktienbewertung", layout="wide")
st.title("📋 ESG-Light Aktienbewertung")
st.markdown("Analysiere Aktien basierend auf einem eigenen ESG-Light-Score.")

# --- Eingabe ---
ticker_input = st.text_input("🔍 Ticker eingeben (z.B. AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

# --- API-Zugang ---
API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}

# --- Funktion zum Abrufen von Daten über den /search Endpoint ---
def get_stock_data(ticker):
    url = f"https://stock-pulse.p.rapidapi.com/search/{ticker}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"⚠️ Fehler beim Abrufen von {ticker} (Status: {response.status_code})")
            return None
    except Exception as e:
        st.error(f"Fehler bei Anfrage für {ticker}: {e}")
        return None

# --- Hauptanzeige ---
if not API_KEY:
    st.error("❌ API-Key fehlt. Bitte stelle sicher, dass dein Key korrekt in den Secrets hinterlegt ist.")
else:
    all_results = []
    for ticker in tickers:
        data = get_stock_data(ticker)
        if data and "quotes" in data:
            for item in data["quotes"]:
                all_results.append({
                    "Ticker": item.get("symbol"),
                    "Name": item.get("shortname"),
                    "Börse": item.get("exchange"),
                    "Typ": item.get("quoteType"),
                    "Industrie": item.get("industry")
                })

    if all_results:
        df = pd.DataFrame(all_results)
        st.dataframe(df)
    else:
        st.error("❌ Keine gültigen Ergebnisse erhalten.")
