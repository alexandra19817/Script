import streamlit as st
import pandas as pd
import requests

# --- UI Setup ---
st.set_page_config(page_title="📊 ESG-Light Aktienbewertung", layout="wide")
st.title("📋 ESG-Light Aktienbewertung")
st.markdown("Analysiere Aktien basierend auf einem eigenen ESG-Light-Score.")

# --- Eingabe ---
ticker_input = st.text_input("🔍 Ticker eingeben (z.B. AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

# --- API Setup ---
API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}
BASE_URL = "https://stock-pulse.p.rapidapi.com/esg-scores"

# --- Daten abrufen ---
results = []

if not API_KEY:
    st.error("❌ API-Key fehlt. Bitte stelle sicher, dass dein Key korrekt in den Secrets hinterlegt ist.")
else:
    for ticker in tickers:
        with st.spinner(f"Lade ESG-Daten für {ticker}..."):
            try:
                response = requests.get(BASE_URL, headers=HEADERS, params={"ticker": ticker})
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        info = data[0]
                        results.append({
                            "Ticker": ticker,
                            "ESG-Score": info.get("esgScore"),
                            "Environment": info.get("environmentScore"),
                            "Social": info.get("socialScore"),
                            "Governance": info.get("governanceScore")
                        })
                    else:
                        st.warning(f"⚠️ Keine ESG-Daten für {ticker} gefunden.")
                else:
                    st.warning(f"⚠️ Fehler beim Abrufen von {ticker} (Status: {response.status_code})")
            except Exception as e:
                st.error(f"❌ Fehler für {ticker}: {str(e)}")

    # --- Ergebnisse anzeigen ---
    if results:
        df = pd.DataFrame(results)
        st.success("✅ Erfolgreich geladen")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("❌ Keine gültigen Ergebnisse erhalten.")
