"""Bounded, one-shot acquisition of public fonts and licensed illustrative photos."""
from pathlib import Path
from urllib.request import Request, urlopen
import re, json, hashlib

root = Path(__file__).resolve().parents[1] / 'assets'
root.mkdir(exist_ok=True)
ua = 'Mozilla/5.0'
font_url = 'https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,700;6..96,800&family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&family=Manrope:wght@400;500;600;700;800&family=Barlow+Condensed:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap'
css = urlopen(Request(font_url, headers={'User-Agent': ua}), timeout=30).read().decode()
origins=[]
for i, url in enumerate(dict.fromkeys(re.findall(r'url\((https://[^)]+)\)', css))):
    ext = url.split('?')[0].rsplit('.',1)[-1]
    name = f'font-{i}.{ext}'
    payload=urlopen(url, timeout=30).read()
    (root / name).write_bytes(payload)
    css=css.replace(url,name)
    origins.append({'file':name,'url':url,'sha256':hashlib.sha256(payload).hexdigest()})
(root / 'fonts.css').write_text(css)
photos = [
 ('bratislava-dusk.jpg','https://images.unsplash.com/photo-1622010583916-28832e5efa13?auto=format&fit=crop&w=1600&q=85','Pavol Svantner','https://unsplash.com/photos/jYIH4_w6Ct0'),
 ('bratislava-river.jpg','https://images.unsplash.com/photo-1716731312696-788b9c3b37ac?auto=format&fit=crop&w=1600&q=85','Michal Vrba','https://unsplash.com/photos/zM9iO5wFnp0'),
]
for name,url,author,page in photos:
    payload=urlopen(url,timeout=30).read()
    (root/name).write_bytes(payload)
    origins.append({'file':name,'url':url,'page':page,'author':author,'license':'Unsplash License','role':'illustration, not evidence of a reported event','sha256':hashlib.sha256(payload).hexdigest()})
(root/'origins.json').write_text(json.dumps({'collected_at':'2026-09-09','font_source':font_url,'assets':origins},ensure_ascii=False,indent=2))
print(f'Saved {len(origins)} assets; fonts are self-hosted; no runtime external requests.')
