import streamlit as st
import requests

st.title("📊 Yahoo Finance 127 Test")

ticker = st.text_input("Ticker eingeben (z. B. TSLA)")

if ticker:
    url = f"https://yahoo-finance127.p.rapidapi.com/esg-scores/{ticker.lower()}"

    headers = {
        "X-RapidAPI-Key": st.secrets["RAPIDAPI"]["key"],  # oder direkt eingeben zum Testen
        "X-RapidAPI-Host": "yahoo-finance127.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    st.write(f"📡 Status Code: {response.status_code}")

    if response.status_code == 200:
        st.success("✅ Daten erfolgreich abgerufen!")
        st.json(response.json())
    else:
        st.error(f"❌ Fehler bei der Datenabfrage (Status {response.status_code})")
        st.code(response.text)
