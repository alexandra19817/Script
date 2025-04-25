import streamlit as st
import requests

st.title("📊 Yahoo Finance 127: Test")

ticker = st.text_input("Ticker eingeben (z. B. TSLA)", "TSLA").upper()

API_KEY = st.secrets.get("RAPIDAPI", {}).get("key", "")

if not API_KEY:
    st.error("❌ API-Key fehlt.")
elif st.button("Abrufen"):
    url = f"https://yahoo-finance127.p.rapidapi.com/finance-analytics/{ticker}"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "yahoo-finance127.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    st.write(f"📡 Status Code: {response.status_code}")

    if response.status_code == 200:
        st.success("✅ Daten erfolgreich abgerufen!")
        st.json(response.json())
    else:
        st.warning(f"⚠️ Fehler beim Abrufen: {response.status_code}")
        st.text(response.text)
