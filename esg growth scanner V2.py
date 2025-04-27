import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config("📈 Nasdaq 100 ESG-Scanner", layout="wide")
st.title("📈 Nasdaq 100 ESG-Scanner mit Bewertung & Charts")

# Tickerliste Nasdaq 100 Auswahl
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "INTC", "CSCO", "PEP",
    "ADBE", "NFLX", "COST", "AVGO", "TXN", "AMD", "QCOM", "AMAT", "BKNG", "INTU",
    "ISRG", "SBUX", "ADI", "VRTX", "GILD", "REGN", "PYPL", "LRCX", "MU", "MRNA",
    "FISV", "KDP", "MAR", "IDXX", "CTAS", "ADP", "ASML", "PDD", "JD", "ZM", "DOCU",
    "TEAM", "CRWD", "SNOW", "PLTR", "OKTA", "ZS", "DDOG", "ROKU", "EXC", "BKR", "CEG"
]

# Bewertungslogik
def smart_rating(kurs, kgv, fair_kgv, esg_score, wachstum):
    if esg_score > 70 and wachstum > 10:
        if kgv and kgv < fair_kgv * 0.9:
            return "✅ Kaufen"
        elif kgv and kgv < fair_kgv * 1.1:
            return "🟡 Beobachten"
    return "❌ Zu teuer"

results = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        kurs = info.get("currentPrice")
        kgv = info.get("trailingPE")
        eps = info.get("trailingEps")
        wachstum = info.get("earningsQuarterlyGrowth", 0) * 100
        branche = info.get("sector", "Unbekannt")
        mk_cap = info.get("marketCap", 0)
        esg = info.get("esgPopulated", False)
        esg_score = info.get("esgScores", {}).get("totalEsg", 50) if esg else 50
        fair_kgv = 20

        bewertung = smart_rating(kurs or 0, kgv or 0, fair_kgv, esg_score, wachstum)

        results.append({
            "Ticker": ticker,
            "Kurs ($)": kurs,
            "KGV": kgv,
            "EPS ($)": eps,
            "Fair-KGV": fair_kgv,
            "Branche": branche,
            "Wachstum (%)": round(wachstum, 2),
            "ESG-Score": esg_score,
            "Marktkapitalisierung ($)": mk_cap,
            "📌 Bewertung": bewertung
        })

    except Exception as e:
        st.warning(f"⚠️ Fehler bei {ticker}: {e}")

# Ergebnisse zusammenbauen
df = pd.DataFrame(results)

if not df.empty:
    # KPI Cards oben
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Kaufkandidaten", df[df["📌 Bewertung"] == "✅ Kaufen"].shape[0])
    with col2:
        st.metric("Ø ESG Score", round(df["ESG-Score"].mean(), 2))
    with col3:
        st.metric("🏆 Top ESG Aktie", df.loc[df["ESG-Score"].idxmax()]['Ticker'])

    # Tabelle anzeigen
    st.subheader("🗂️ Details aller analysierten Unternehmen")
    st.dataframe(df.set_index("Ticker"))

    # ESG Score Histogramm
    st.subheader("📈 ESG Score Verteilung")
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df["ESG-Score"], nbinsx=20))
    fig.update_layout(bargap=0.2)
    st.plotly_chart(fig, use_container_width=True)

    # CSV Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV-Datei herunterladen", csv, "nasdaq100_esg_scan.csv", "text/csv")
else:
    st.info("Keine Daten verfügbar.")
