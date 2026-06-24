import sys
sys.stdout.reconfigure(encoding='utf-8')
from ddgs import DDGS
import json

def _ddgs(query, n=5):
    try:
        return DDGS().text(query, max_results=n) or []
    except Exception:
        return []

def _remover_acentos(texto):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

termo_spotify = "anavitoria"
res_artista = _ddgs(f"{termo_spotify} spotify artist", 4)
print("RES_ARTISTA:", json.dumps(res_artista, indent=2, ensure_ascii=False))

eh_artista = False
termo_norm = _remover_acentos(termo_spotify.lower())

for res in res_artista:
    if "/artist/" in res.get('href', ''):
        titulo_pg = _remover_acentos(res.get('title', '').lower())
        nome_pg = titulo_pg.split("|")[0].split("-")[0].strip()
        print("TITULO PG:", titulo_pg)
        print("NOME PG:", nome_pg)
        palavras = [p for p in termo_norm.split() if len(p) > 2]
        print("PALAVRAS:", palavras)
        if palavras and all(p in nome_pg for p in palavras):
            eh_artista = True
            break
print("EH_ARTISTA:", eh_artista)
