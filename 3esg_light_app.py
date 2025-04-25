import streamlit as st
import pandas as pd
import requests

# --- Einstellungen ---
st.set_page_config(page_title="📊 ESG-Light Aktienbewertung", layout="wide")
st.title("📈 ESG-Light Aktienbewertung")
st.markdown("Analysiere Aktien basierend auf einem eigenen ESG-Light-Score.")

# --- Eingabe ---
ticker_input = st.text_input("🔎 Ticker eingeben (z.B. AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

# --- API-Key aus Streamlit Secrets ---
API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")
if not API_KEY:
    st.error("❌ API-Key fehlt. Bitte stelle sicher, dass dein Key korrekt in den Secrets hinterlegt ist.")
    st.stop()

# --- API-Aufruf-Konfiguration ---
BASE_URL = "https://stock-pulse.p.rapidapi.com/stock-fundamentals"
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}

# --- Daten sammeln ---
results = []
for ticker in tickers:
    response = requests.get(BASE_URL, headers=HEADERS, params={"ticker": ticker})
    if response.status_code == 200:
        data = response.json()
        # Beispielhafte Berechnung für ESG-Light Bewertung
        fundamentals = data.get("data", {})
        score = 0
        if fundamentals:
            market_cap = fundamentals.get("marketCap", 0)
            dividend_yield = fundamentals.get("dividendYield", 0)
            pe_ratio = fundamentals.get("peRatio", 0)

            if dividend_yield and dividend_yield > 1:
                score += 1
            if pe_ratio and pe_ratio < 30:
                score += 1
            if market_cap and market_cap > 10_000_000_000:
                score += 1

            results.append({
                "Ticker": ticker,
                "Dividendenrendite": f"{dividend_yield:.2f}%" if dividend_yield else "-",
                "KGV (P/E)": pe_ratio,
                "Marktkapitalisierung": f"{market_cap/1e9:.2f} Mrd $",
                "ESG-Light Score": f"{score}/3"
            })
        else:
            st.warning(f"⚠️ Keine ESG-Daten für {ticker} gefunden.")
    else:
        st.warning(f"⚠️ Fehler beim Abrufen von {ticker} (Status: {response.status_code})")

# --- Ausgabe ---
if results:
    df = pd.DataFrame(results)
    st.success("✅ Analyse abgeschlossen.")
    st.dataframe(df, use_container_width=True)
else:
    st.error("❌ Keine gültigen Ergebnisse erhalten.")
