import streamlit as st
import requests

st.title("🔍 ESG Test (Stock Pulse API)")

ticker = st.text_input("Ticker eingeben (z. B. AAPL)", "AAPL").upper()

# API-Key sicher laden
API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")

if not API_KEY:
    st.error("❌ API-Key fehlt. Bitte überprüfe die Secrets-Einstellungen.")
else:
    if st.button("Abrufen"):
        url = f"https://stock-pulse.p.rapidapi.com/esg-scores/{ticker}"
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
        }

        try:
            response = requests.get(url, headers=headers)
            st.write(f"📡 Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                st.success("✅ Daten erfolgreich geladen!")
                st.json(data)
            else:
                st.warning(f"⚠️ Fehler beim Abrufen: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"❌ Fehler: {str(e)}")
