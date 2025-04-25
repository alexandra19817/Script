import requests

headers = {
    "X-RapidAPI-Key": "DEIN_API_KEY",
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}

url = "https://stock-pulse.p.rapidapi.com/search"
params = {"query": "AAPL"}

response = requests.get(url, headers=headers, params=params)
print(response.status_code)
print(response.json())
