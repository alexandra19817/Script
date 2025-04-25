import streamlit as st
import requests

st.title("🔍 Stock Pulse API Test: Search")

ticker = st.text_input("Ticker eingeben (z. B. AAPL)", "AAPL").upper()

API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")

if not API_KEY:
    st.error("❌ API-Key fehlt.")
elif st.button("Suchen"):
    url = f"https://stock-pulse.p.rapidapi.com/search/{ticker}"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
    }

    try:
        r = requests.get(url, headers=headers)
        st.write(f"📡 Status Code: {r.status_code}")

        if r.status_code == 200:
            st.success("✅ Daten erhalten!")
            st.json(r.json())
        else:
            st.warning(f"⚠️ Fehler beim Abrufen: {r.status_code}")
            st.text(r.text)

    except Exception as e:
        st.error(f"❌ Fehler: {str(e)}")
