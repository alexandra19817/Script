import requests

headers = {
    "X-RapidAPI-Key": "475144edcemshb099c7a946dfa28p145a29jsn18d5b7af5186Y",
    "X-RapidAPI-Host": "stock-pulse.p.rapidapi.com"
}

url = "https://stock-pulse.p.rapidapi.com/search"
params = {"query": "AAPL"}

response = requests.get(url, headers=headers, params=params)
print(response.status_code)
print(response.json())
