import requests

API_KEY = "AIzaSyCb9e6CeitMGLCooN0TC08E3_rceF2efpQ"

url = "https://br-icloud.com.br"

endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"

payload = {
  "client": {
    "clientId": "your-app",
    "clientVersion": "1.0"
  },
  "threatInfo": {
    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
    "platformTypes": ["ANY_PLATFORM"],
    "threatEntryTypes": ["URL"],
    "threatEntries": [{"url": url}]
  }
}

res = requests.post(endpoint, json=payload)
data = res.json()

print(data)  # DEBUG

if "error" in data:
    print("❌ API Error:", data["error"])
elif "matches" in data:
    print("⚠️ Dangerous URL")
else:
    print("✅ Safe URL")