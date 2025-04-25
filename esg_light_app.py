import streamlit as st
import pandas as pd
import requests

# --- Einstellungen ---
st.set_page_config("📊 ESG-Light Aktienbewertung", layout="wide")
st.title("📊 ESG-Light Aktienbewertung")
st.markdown("Analysiere Aktien basierend auf einem eigenen ESG-Light-Score.")

# --- Eingabe ---
ticker_input = st.text_input("🔎 Ticker eingeben (z.B. AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA, NVDA")
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

# --- API-Key ---
API_KEY = st.secrets["RAPIDAPI"]["475144edcemshb099c7a946dfa28p145a29jsn18d5b7af5186"]  # Sichere API-Key-Verwaltung
HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}

# --- Analysefunktion ---
def analyse_aktie(ticker):
    url = f"https://stock-pulse.p.rapidapi.com/stock?symbol={ticker}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return {"Ticker": ticker, "Fehler": f"❌ {r.status_code}"}

    data = r.json()
    price = data.get("price")
    pe = data.get("pe")
    dividend = data.get("dividendYield")
    beta = data.get("beta")
    sector = data.get("sector")

    score = 0
    if pe and pe < 20: score += 25
    elif pe and pe < 40: score += 15

    if dividend and dividend > 0.02: score += 25
    elif dividend and dividend > 0.01: score += 10

    if beta and beta < 1: score += 20
    elif beta and beta < 1.3: score += 10

    if sector:
        if sector.lower() in ["utilities", "renewable energy"]: score += 25
        elif sector.lower() in ["oil & gas", "coal"]: score -= 10

    score = min(score, 100)

    if score >= 85: rating = "🟢 A"
    elif score >= 70: rating = "🟡 B"
    elif score >= 50: rating = "🔵 C"
    else: rating = "🔴 D"

    return {
        "Ticker": ticker,
        "Preis ($)": price,
        "KGV": pe,
        "Dividende (%)": round(dividend * 100, 2) if dividend else None,
        "Beta": beta,
        "Sektor": sector,
        "Score": score,
        "Bewertung": rating
    }

# --- Analyse starten ---
if st.button("🚀 Analyse starten") and tickers:
    results = []
    for ticker in tickers:
        with st.spinner(f"{ticker} wird analysiert..."):
            results.append(analyse_aktie(ticker))

    df = pd.DataFrame(results)

    if "Fehler" in df.columns:
        st.warning("Einige Ticker konnten nicht geladen werden.")
        st.dataframe(df)
    else:
        st.success("✅ Analyse abgeschlossen.")

        # Farben für Score visualisieren
        def color_rating(val):
            if isinstance(val, str):
                if "A" in val: return "background-color: lightgreen"
                if "B" in val: return "background-color: khaki"
                if "C" in val: return "background-color: lightblue"
                if "D" in val: return "background-color: lightcoral"
            return ""

        st.dataframe(df.style.applymap(color_rating, subset=["Bewertung"]))

        # 📥 Export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ CSV herunterladen", csv, "esg_bewertung.csv", "text/csv")

# Hinweis unten
st.caption("Made with ❤️ by Alexa")
