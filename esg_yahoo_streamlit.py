import streamlit as st
import pandas as pd
import requests

# ---------------------------
# CONFIG
# ---------------------------
API_KEY = "475144edcemshb099c7a946dfa28p145a29jsn18d5b7af5186"  # <- hier den echten Key eintragen
API_HOST = "yfinanceapi.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

# ---------------------------
# Funktionen
# ---------------------------
def get_stock_data(ticker):
    url = f"https://yfinanceapi.p.rapidapi.com/quote/{ticker}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def analyze_stock(ticker):
    data = get_stock_data(ticker)
    if not data:
        return None

    # ESG-Light Score Berechnung
    price = data.get("price")
    pe = data.get("pe") or 0
    beta = data.get("beta") or 0
    dividend = data.get("dividendYield") or 0

    score = 0
    if pe < 20: score += 25
    elif pe < 40: score += 15

    if dividend > 0.02: score += 25
    elif dividend > 0.01: score += 10

    if beta < 1: score += 25
    elif beta < 1.3: score += 10

    score = min(score, 100)
    if score >= 85:
        rating, recommendation = "A", "Kaufen"
    elif score >= 70:
        rating, recommendation = "B", "Beobachten"
    elif score >= 50:
        rating, recommendation = "C", "Halten"
    else:
        rating, recommendation = "D", "Prüfen"

    return {
        "Ticker": ticker,
        "Kurs ($)": price,
        "KGV": pe,
        "DivRendite": round(dividend * 100, 2),
        "Beta": beta,
        "Score": score,
        "Rating": rating,
        "Empfehlung": recommendation
    }

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config("📊 Marktanalyse mit ESG-Light")
st.title("📈 ESG-Light Aktienbewertung")

st.markdown("Analysiere beliebige Aktien mit vereinfachtem Bewertungsmodell.")

user_input = st.text_input("🔎 Ticker eingeben (z.B. AAPL, MSFT, TSLA):", "AAPL")

if st.button("Analyse starten"):
    tickers = [ticker.strip().upper() for ticker in user_input.split(",") if ticker.strip()]
    results = []
    for t in tickers:
        with st.spinner(f"Analysiere {t}..."):
            result = analyze_stock(t)
            if result:
                results.append(result)
            else:
                st.warning(f"❌ Keine Daten für {t} gefunden.")

    if results:
        df = pd.DataFrame(results)
        st.success("✅ Analyse abgeschlossen")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Keine gültigen Ergebnisse erhalten.")
