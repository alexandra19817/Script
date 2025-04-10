import yfinance as yf
import pandas as pd
import streamlit as st
import io
import datetime

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
            row = {
                "Unternehmen": name,
                "Ticker": ticker,
                "Marktkapitalisierung": info.get("marketCap"),
                "KGV (P/E)": info.get("trailingPE"),
                "KUV (P/S)": info.get("priceToSalesTrailing12Months"),
                "KBV (P/B)": info.get("priceToBook"),
                "Dividendenrendite": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
                "ROE (%)": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
                "ROA (%)": round(info.get("returnOnAssets", 0) * 100, 2) if info.get("returnOnAssets") else None,
                "Beta": info.get("beta"),
                "Aktueller Kurs": info.get("currentPrice"),
                "Kursziel": info.get("targetMeanPrice"),
            }
            # Upside berechnen
            if row["Aktueller Kurs"] and row["Kursziel"]:
                row["Upside (%)"] = round(((row["Kursziel"] - row["Aktueller Kurs"]) / row["Aktueller Kurs"]) * 100, 2)
            else:
                row["Upside (%)"] = None

            rows.append(row)
        except Exception as e:
            st.warning(f"Fehler beim Abrufen von {name} ({ticker}): {e}")

    return pd.DataFrame(rows)

# Daten abrufen und anzeigen
df = get_stock_data(TICKER_LIST)

# Formatierungen
def colorize(val, column):
    if pd.isna(val):
        return ""
    if column == "ROA (%)" and val >= 10:
        return "background-color: #C6EFCE"  # grün
    elif column == "ROA (%)" and val < 5:
        return "background-color: #FFC7CE"  # rot
    elif column == "ROE (%)" and val >= 15:
        return "background-color: #C6EFCE"
    elif column == "ROE (%)" and val < 10:
        return "background-color: #FFC7CE"
    elif column == "Upside (%)" and val > 20:
        return "background-color: #C6EFCE"
    return ""

def highlight(df):
    return df.style.apply(lambda row: [colorize(val, col) for col, val in row.items()], axis=1)

st.dataframe(highlight(df), use_container_width=True)

# Export-Funktion
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

st.caption(f"🔍 Datenquelle: Yahoo Finance | Stand: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
