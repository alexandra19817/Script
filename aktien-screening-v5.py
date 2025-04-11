import yfinance as yf
import pandas as pd
import streamlit as st
import io
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Aktien Screening", layout="wide")
st.title("📈 Automatisches Aktien-Screening Tool")

# Nutzerdefinierte Tickerauswahl
def user_ticker_input():
    default_tickers = "Rollins:ROL, Advantest:ATEYY, Flex:FLEX, Deutsche Wohnen:DWNI.DE, Daimler Truck:DTG.F, Evotec SE:EVT.DE, HelloFresh:HFG.DE"
    user_input = st.text_input("🎯 Unternehmen und Ticker eingeben (Format: Name:TICKER, ...)", value=default_tickers)
    ticker_dict = {}
    try:
        entries = [x.strip() for x in user_input.split(",") if ":" in x]
        for entry in entries:
            name, ticker = entry.split(":")
            ticker_dict[name.strip()] = ticker.strip()
    except:
        st.error("Bitte Eingabe im Format 'Name:TICKER' machen.")
    return ticker_dict

TICKER_LIST = user_ticker_input()

# Tabelle vorbereiten
def get_stock_data(tickers):
    rows = []
    for name, ticker in tickers.items():
        stock = yf.Ticker(ticker)
        info = stock.info

        try:
            hist_6m = stock.history(period="6mo")
            hist_1y = stock.history(period="1y")
            perf_6m = ((hist_6m["Close"].iloc[-1] - hist_6m["Close"].iloc[0]) / hist_6m["Close"].iloc[0]) * 100 if not hist_6m.empty else None
            perf_1y = ((hist_1y["Close"].iloc[-1] - hist_1y["Close"].iloc[0]) / hist_1y["Close"].iloc[0]) * 100 if not hist_1y.empty else None

            pe = info.get("trailingPE")
            growth_est = info.get("earningsQuarterlyGrowth") or 0.1
            fair_pe = round(15 + growth_est * 100, 2) if growth_est else None

            # Bewertungsskala
            score = 0
            if perf_1y and perf_1y > 10: score += 1
            if perf_6m and perf_6m > 5: score += 1
            if pe and fair_pe and pe < fair_pe: score += 1
            if info.get("returnOnAssets", 0) > 0.1: score += 1
            if info.get("dividendYield", 0) > 0.02: score += 1
            stars = "⭐" * score if score > 0 else "-"

            row = {
                "Unternehmen": name,
                "Ticker": ticker,
                "Marktkapitalisierung": info.get("marketCap"),
                "KGV (P/E)": pe,
                "Faires KGV": fair_pe,
                "KUV (P/S)": info.get("priceToSalesTrailing12Months"),
                "KBV (P/B)": info.get("priceToBook"),
                "Dividendenrendite": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
                "ROE (%)": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
                "ROA (%)": round(info.get("returnOnAssets", 0) * 100, 2) if info.get("returnOnAssets") else None,
                "Verschuldungsgrad (%)": round((info.get("totalDebt") / info.get("totalAssets")) * 100, 2) if info.get("totalDebt") and info.get("totalAssets") else None,
                "Beta": info.get("beta"),
                "Aktueller Kurs": info.get("currentPrice"),
                "Kursziel": info.get("targetMeanPrice"),
                "Performance 6M (%)": round(perf_6m, 2) if perf_6m else None,
                "Performance 1Y (%)": round(perf_1y, 2) if perf_1y else None,
                "Bewertung (1-5 Sterne)": stars
            }
            if row["Aktueller Kurs"] and row["Kursziel"]:
                row["Upside (%)"] = round(((row["Kursziel"] - row["Aktueller Kurs"]) / row["Aktueller Kurs"]) * 100, 2)
            else:
                row["Upside (%)"] = None

            if row["Upside (%)"] is not None and row["ROA (%)"] is not None and row["Verschuldungsgrad (%)"] is not None:
                if row["Upside (%)"] > 20 and row["ROA (%)"] >= 10 and row["Verschuldungsgrad (%)"] < 150:
                    row["Empfehlung"] = "Kaufen ✅"
                elif row["Upside (%)"] > 5 and row["ROA (%)"] >= 5:
                    row["Empfehlung"] = "Beobachten 👀"
                else:
                    row["Empfehlung"] = "Nicht kaufen ❌"
            else:
                row["Empfehlung"] = "Unklar 🤷"

            rows.append(row)
        except Exception as e:
            st.warning(f"Fehler beim Abrufen von {name} ({ticker}): {e}")

    return pd.DataFrame(rows)

df = get_stock_data(TICKER_LIST)

# Farbformatierung
def colorize(val, column):
    if pd.isna(val):
        return ""
    if column == "ROA (%)" and val >= 10:
        return "background-color: #C6EFCE"
    elif column == "ROA (%)" and val < 5:
        return "background-color: #FFC7CE"
    elif column == "ROE (%)" and val >= 15:
        return "background-color: #C6EFCE"
    elif column == "ROE (%)" and val < 10:
        return "background-color: #FFC7CE"
    elif column == "Verschuldungsgrad (%)" and val >= 200:
        return "background-color: #FFC7CE"
    elif column == "Upside (%)" and val > 20:
        return "background-color: #C6EFCE"
    elif column == "KGV (P/E)" and df["Faires KGV"].notna().all():
        if val < df.loc[df["KGV (P/E)"] == val, "Faires KGV"].values[0]:
            return "background-color: #C6EFCE"
        else:
            return "background-color: #FFC7CE"
    return ""

def highlight(df):
    return df.style.apply(lambda row: [colorize(val, col) for col, val in row.items()], axis=1)

st.dataframe(highlight(df), use_container_width=True)

# Chartanzeige
def show_charts(tickers):
    st.subheader("📊 Kursverlauf")
    selected = st.selectbox("Wähle ein Unternehmen für den Kursverlauf", list(tickers.keys()))
    if selected:
        ticker = tickers[selected]
        data = yf.Ticker(ticker).history(period="1y")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=selected))
        fig.update_layout(title=f"Kursverlauf von {selected} (12 Monate)", xaxis_title="Datum", yaxis_title="Kurs")
        st.plotly_chart(fig, use_container_width=True)

show_charts(TICKER_LIST)

# Export
st.subheader("📥 Export")
file_buffer = io.BytesIO()
df.to_excel(file_buffer, index=False, engine='openpyxl')
file_buffer.seek(0)

st.download_button(
    label="📊 Excel herunterladen",
    data=file_buffer,
    file_name="Aktien_Screening_Ergebnisse.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Kommentarfeld
with st.expander("ℹ️ Erklärungen zu den Kennzahlen"):
    st.markdown("""
    - **KGV (P/E)**: Kurs-Gewinn-Verhältnis. Je niedriger, desto günstiger (unter Annahme stabiler Gewinne).
    - **Faires KGV**: Geschätztes angemessenes KGV basierend auf Gewinnwachstum oder Benchmark.
    - **KUV (P/S)**: Kurs-Umsatz-Verhältnis.
    - **KBV (P/B)**: Kurs-Buchwert-Verhältnis.
    - **Dividendenrendite**: Ausgeschüttete Dividende im Verhältnis zum Kurs.
    - **ROE**: Return on Equity – Eigenkapitalrendite.
    - **ROA**: Return on Assets – Gesamtkapitalrendite.
    - **Verschuldungsgrad**: Schulden im Verhältnis zu Gesamtvermögen.
    - **Upside**: Potenzieller Kursgewinn zum Kursziel laut Analysten.
    - **Bewertung (1-5 Sterne)**: Schnellbewertung nach quantitativen Kriterien (Wachstum, Rendite, Bewertung).
    """)

st.caption(f"🔍 Datenquelle: Yahoo Finance | Stand: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
