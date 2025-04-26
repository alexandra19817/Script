import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# Streamlit Seitenlayout
st.set_page_config("📈 ESG-Scanner mit Bewertung", layout="wide")
st.title("📈 ESG-Scanner mit Bewertung & Charts")

# Beispielhafte Tickerliste (kann später dynamisch geladen werden)
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

# Bewertung berechnen basierend auf ESG, Wachstum und KGV
def smart_rating(kurs, kgv, fair_kgv, esg_score, wachstum):
    if esg_score > 70 and wachstum > 10:
        if kgv < fair_kgv * 0.9:
            return "✅ Kaufen"
        elif kgv < fair_kgv * 1.1:
            return "🟡 Beobachten"
    return "❌ Zu teuer"

# Ergebnisse speichern
results = []

for ticker in tickers:
    st.subheader(f"📊 {ticker}")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        kurs = info.get("currentPrice")
        kgv = info.get("trailingPE")
        eps = info.get("trailingEps")
        wachstum = info.get("earningsQuarterlyGrowth", 0) * 100  # In Prozent
        branche = info.get("sector", "Unbekannt")
        mk_cap = info.get("marketCap", 0)
        esg = info.get("esgPopulated", False)
        esg_score = info.get("esgScores", {}).get("totalEsg", 50) if esg else 50
        fair_kgv = 20  # Einfacher Fair-KGV Wert als Richtlinie

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

        # 📈 Mini-Chart Kursverlauf (6 Monate)
        data = stock.history(period="6mo")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Kursverlauf"))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"⚠️ Fehler beim Abrufen von {ticker}: {e}")

# Ergebnisse zusammenfassen
df = pd.DataFrame(results)

if not df.empty:
    st.subheader("🗂️ Zusammenfassung aller analysierten Aktien")
    st.dataframe(df.set_index("Ticker"))

    # 📤 CSV Export Option
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Ergebnisse als CSV herunterladen",
        data=csv,
        file_name="aktienanalyse.csv",
        mime="text/csv"
    )
else:
    st.info("ℹ️ Noch keine Daten verfügbar.")
