import streamlit as st
import requests

st.title("Finanzkennzahlen-Abfrage")

# Ticker-Eingabe
ticker = st.text_input("Bitte Ticker-Symbol eingeben (z.B. TSLA):")

if ticker:
    # API-Anfrage vorbereiten
    base_url = "https://yahoo-finance127.p.rapidapi.com/stock/v2/get-summary"
    params = {"symbol": ticker, "region": "US"}
    headers = {
        "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",  # <--- RapidAPI API-Key hier einsetzen
        "x-rapidapi-host": "yahoo-finance127.p.rapidapi.com"
    }

    # Anfrage senden
    response = requests.get(base_url, params=params, headers=headers)
    st.write("Status Code:", response.status_code)
    if response.status_code == 200:
        st.success("Abfrage erfolgreich! ✅")
        data = response.json()

        # Daten aus JSON extrahieren
        result = data.get("quoteSummary", {}).get("result", [])
        if result:
            fd = result[0].get("financialData", {})
            current_price = fd.get("currentPrice", {}).get("raw")
            target_price = fd.get("targetMeanPrice", {}).get("raw")
            rec_key   = fd.get("recommendationKey")  # Analystenempfehlung (Text)
            rec_mean  = fd.get("recommendationMean", {}).get("raw")
            analysts  = fd.get("numberOfAnalystOpinions", {}).get("raw")
            revenue   = fd.get("totalRevenue", {}).get("raw")
            ebitda    = fd.get("ebitda", {}).get("raw")
            profit_margin = fd.get("profitMargins", {}).get("raw")
            debt      = fd.get("totalDebt", {}).get("raw")
            free_cf   = fd.get("freeCashflow", {}).get("raw")
            currency  = fd.get("financialCurrency", "")  # z.B. "USD"

            # Ausgabe in Kategorien
            # Bewertung
            st.subheader("Bewertung")
            st.write(f"**Aktueller Preis:** {current_price} {currency}")
            st.write(f"**Kursziel (Ø):** {target_price} {currency}")
            if rec_key:
                rec_text = rec_key.capitalize()
                st.write(f"**Analystenmeinung:** {rec_text} (Durchschnitt {rec_mean:.1f} von 5)")
                st.write(f"**Analystenanzahl:** {analysts}")
            else:
                st.write("**Analystenmeinung:** N/A")

            # Umsätze und Rentabilität
            st.subheader("Umsätze und Rentabilität")
            st.write(f"**Gesamtumsatz:** {revenue} {currency}")
            st.write(f"**EBITDA:** {ebitda} {currency}")
            if profit_margin is not None:
                st.write(f"**Gewinnmarge:** {profit_margin * 100:.1f} %")

            # Schulden und Cashflow
            st.subheader("Schulden und Cashflow")
            st.write(f"**Gesamtschulden:** {debt} {currency}")
            st.write(f"**Freier Cashflow:** {free_cf} {currency}")
        else:
            st.error("Keine Daten im Ergebnis gefunden.")
    else:
        st.error(f"Fehler bei der Datenabfrage (Status {response.status_code})")
