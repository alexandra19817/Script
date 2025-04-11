import yfinance as yf
import pandas as pd
import streamlit as st
import io
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Aktien Screening", layout="wide")
st.title("\U0001F4C8 Automatisches Aktien-Screening Tool")

# Nutzerdefinierte Tickerauswahl
def user_ticker_input():
    default_tickers = "Rollins:ROL, Advantest:ATEYY, Flex:FLEX, Deutsche Wohnen:DWNI.DE, Daimler Truck:DTG.F, Evotec SE:EVT.DE, HelloFresh:HFG.DE"
    user_input = st.text_input("\U0001F3AF Unternehmen und Ticker eingeben (Format: Name:TICKER, ...)", value=default_tickers)
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

            roe = info.get("returnOnEquity", 0)
            roa = info.get("returnOnAssets", 0)
            debt = info.get("totalDebt")
            assets = info.get("totalAssets")
            verschuldung = round((debt / assets) * 100, 2) if debt and assets else None
            revenue = info.get("totalRevenue")
            div_yield = info.get("dividendYield", 0)
            beta = info.get("beta")
            price = info.get("currentPrice")
            target = info.get("targetMeanPrice")

            score = 0
            if perf_1y and perf_1y > 10: score += 1
            if perf_6m and perf_6m > 5: score += 1
            if pe and fair_pe and pe < fair_pe: score += 1
            if roa > 0.1: score += 1
            if div_yield > 0.02: score += 1
            stars = "⭐" * score if score > 0 else "-"

            upside = round(((target - price) / price) * 100, 2) if price and target else None

            # Erweiterte Empfehlungslogik
            if all([upside is not None, roa is not None, verschuldung is not None, beta is not None]):
                if upside > 25 and roa >= 12 and verschuldung < 100 and beta < 1.2:
                    recommendation = "Kaufen ✅"
                elif upside > 10 and roa >= 6:
                    recommendation = "Beobachten \U0001F440"
                elif upside < 0 or verschuldung > 200 or roa < 3:
                    recommendation = "Nicht kaufen ❌"
                else:
                    recommendation = "Unklar \U0001F937"
            else:
                recommendation = "Unklar \U0001F937"

            # CAGR-Berechnung (letzte 5 Jahre)
            hist_5y = stock.history(period="5y")
            cagr = None
            if not hist_5y.empty:
                start_price = hist_5y["Close"].iloc[0]
                end_price = hist_5y["Close"].iloc[-1]
                years = 5
                cagr = ((end_price / start_price) ** (1 / years) - 1) * 100

            row = {
                "Unternehmen": name,
                "Ticker": ticker,
                "Marktkapitalisierung": info.get("marketCap"),
                "Umsatz (in Mrd. €)": round(revenue / 1e9, 2) if revenue else None,
                "KGV (P/E)": pe,
                "Faires KGV": fair_pe,
                "KUV (P/S)": info.get("priceToSalesTrailing12Months"),
                "KBV (P/B)": info.get("priceToBook"),
                "Dividendenrendite": round(div_yield * 100, 2) if div_yield else None,
                "ROE (%)": round(roe * 100, 2) if roe else None,
                "ROA (%)": round(roa * 100, 2) if roa else None,
                "Verschuldungsgrad (%)": verschuldung,
                "Beta": beta,
                "Aktueller Kurs": price,
                "Kursziel": target,
                "Performance 6M (%)": round(perf_6m, 2) if perf_6m else None,
                "Performance 1Y (%)": round(perf_1y, 2) if perf_1y else None,
                "CAGR 5Y (%)": round(cagr, 2) if cagr else None,
                "Bewertung (1-5 Sterne)": stars,
                "Upside (%)": upside,
                "Empfehlung": recommendation
            }

            rows.append(row)
        except Exception as e:
            st.warning(f"Fehler beim Abrufen von {name} ({ticker}): {e}")

    df = pd.DataFrame(rows)
    return df.sort_values(by="Bewertung (1-5 Sterne)", ascending=False, key=lambda x: x.str.len() if x.dtype == "object" else x)

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

# Chartanzeige – Vergleich mehrerer Unternehmen
def show_charts(tickers):
    st.subheader("\U0001F4CA Kursverlauf vergleichen")
    selected = st.multiselect("Unternehmen auswählen", list(tickers.keys()), default=list(tickers.keys())[:2])

    if selected:
        fig = go.Figure()
        for name in selected:
            ticker = tickers[name]
            data = yf.Ticker(ticker).history(period="1y")
            if not data.empty:
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=name))
        fig.update_layout(title="Kursverlauf Vergleich (12 Monate)", xaxis_title="Datum", yaxis_title="Kurs", legend_title="Unternehmen")
        st.plotly_chart(fig, use_container_width=True)

show_charts(TICKER_LIST)

# Export
st.subheader("\U0001F4E5 Export")
file_buffer = io.BytesIO()
df.to_excel(file_buffer, index=False, engine='openpyxl')
file_buffer.seek(0)

st.download_button(
    label="\U0001F4CA Excel herunterladen",
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
    - **Umsatz**: Gesamtumsatz des Unternehmens in den letzten 12 Monaten (in Milliarden Euro).
    - **Upside**: Potenzieller Kursgewinn zum Kursziel laut Analysten.
    - **Beta**: Volatilität im Vergleich zum Markt (1 = gleich wie Markt).
    - **Bewertung (1-5 Sterne)**: Schnellbewertung nach quantitativen Kriterien (Wachstum, Rendite, Bewertung).
    - **Empfehlung**: Automatisch abgeleitet aus mehreren Kennzahlen (z. B. Rendite, Verschuldung, Bewertung).
    - **CAGR 5Y**: Durchschnittliche jährliche Wachstumsrate der letzten 5 Jahre (zusammengesetzt).
    """)

st.caption(f"\U0001F50D Datenquelle: Yahoo Finance | Stand: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
