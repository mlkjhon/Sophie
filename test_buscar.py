import sys
sys.stdout.reconfigure(encoding='utf-8')
from ddgs import DDGS
import json

def _ddgs(query, n=5):
    try:
        return DDGS().text(query, max_results=n) or []
    except Exception:
        return []

def _buscar_track(termo):
    termo_quoted = f'"{termo}"'
    rs = _ddgs(f"site:open.spotify.com/track {termo_quoted}", 5)
    
    if not rs:
        rs_aberto = _ddgs(f"{termo_quoted} spotify", 8)
        rs = [r for r in rs_aberto if "open.spotify.com/track" in r.get('href', '')]
    
    if not rs:
        rs = _ddgs(f"site:open.spotify.com/track {termo}", 5)

    if not rs:
        print("FALHOU: rs vazio")
        return False

    melhor = None
    termo_lower = termo.lower()
    for r in rs:
        titulo = r.get('title', '').lower()
        href = r.get('href', '')
        if "/track/" in href and titulo.startswith(termo_lower):
            melhor = r
            break
            
    if not melhor:
        for r in rs:
            titulo = r.get('title', '').lower()
            href = r.get('href', '')
            if "/track/" in href and termo.split()[0].lower() in titulo:
                melhor = r
                break
                
    if not melhor:
        for r in rs:
            if "/track/" in r.get('href', ''):
                melhor = r
                break
                
    if not melhor:
        print("FALHOU: nenhum melhor")
        return False

    url = melhor['href']
    nome = melhor.get('title', termo).split("-")[0].strip()
    print(f"SUCESSO: {nome} -> {url}")
    return True

_buscar_track("dark red")
