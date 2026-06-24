import requests
import re
import urllib.parse
query = urllib.parse.quote("raça negra")
res = requests.get(f"https://open.spotify.com/search/{query}/tracks", headers={"User-Agent": "Mozilla/5.0"})
matches = re.findall(r'spotify%3Atrack%3A([a-zA-Z0-9]+)', res.text)
matches2 = re.findall(r'spotify:track:([a-zA-Z0-9]+)', res.text)
print("Matches 1:", matches[:5])
print("Matches 2:", matches2[:5])
