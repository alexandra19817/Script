import streamlit as st
import pandas as pd
import requests

# --- Einstellungen ---
st.set_page_config(page_title="📊 ESG-Light Aktienbewertung", layout="wide")
st.title("📈 ESG-Light Aktienbewertung")
st.markdown("Analysiere Aktien basierend auf einem eigenen ESG-Light-Score.")

# --- Eingabe ---
ticker_input = st.text_input("🔍 Ticker eingeben (z.B. AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

# --- API-Key holen ---
API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")

if not API_KEY:
    st.error("❌ API-Key fehlt. Bitte stelle sicher, dass dein Key korrekt in den Secrets hinterlegt ist.")
    st.stop()

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}

# --- Daten holen ---
def fetch_data(ticker):
    url = f"https://stock-pulse.p.rapidapi.com/stock-fundamentals?ticker={ticker}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        return data if isinstance(data, dict) else None
    except Exception as e:
        return {"error": str(e)}

# --- Ergebnis-Ansicht ---
results = []

for ticker in tickers:
    data = fetch_data(ticker)
    if not data or "companyName" not in data:
        st.warning(f"❌ Keine Daten für {ticker} gefunden.")
        continue

    # Beispiel-Score: ESG-Score Light (nur Platzhalter)
    esg_light_score = round((data.get("esgScore", 50) + data.get("peRatio", 15)) / 2, 2)

    results.append({
        "Ticker": ticker,
        "Name": data.get("companyName", "—"),
        "Kurs": data.get("price", "—"),
        "KGV": data.get("peRatio", "—"),
        "ESG Light": esg_light_score,
        "Dividende": data.get("dividendYield", "—"),
        "Marktkapitalisierung": data.get("marketCap", "—")
    })

# --- Anzeige ---
if results:
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
else:
    st.error("❌ Keine gültigen Ergebnisse erhalten.")
