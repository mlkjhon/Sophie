import sys
sys.stdout.reconfigure(encoding='utf-8')
from ddgs import DDGS
import json
print(json.dumps(DDGS().text('site:open.spotify.com/track "dark red"', max_results=5), indent=2, ensure_ascii=False))
