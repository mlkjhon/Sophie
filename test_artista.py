import sys
sys.stdout.reconfigure(encoding='utf-8')
from ddgs import DDGS
import json

def _ddgs(query, n=5):
    try:
        return DDGS().text(query, max_results=n) or []
    except Exception:
        return []

termo_spotify = "anavitória"
res_artista = _ddgs(f"site:open.spotify.com/artist {termo_spotify}", 2)
print("RES_ARTISTA:", json.dumps(res_artista, indent=2, ensure_ascii=False))
eh_artista = False
for res in res_artista:
    if "/artist/" in res.get('href', ''):
        titulo_pg = res.get('title', '').lower()
        nome_pg = titulo_pg.split("|")[0].split("-")[0].strip()
        print("TITULO PG:", titulo_pg)
        print("NOME PG:", nome_pg)
        palavras = [p for p in termo_spotify.lower().split() if len(p) > 2]
        print("PALAVRAS:", palavras)
        if palavras and all(p in nome_pg for p in palavras):
            eh_artista = True
            break
print("EH_ARTISTA:", eh_artista)
