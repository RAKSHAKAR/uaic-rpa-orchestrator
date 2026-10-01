import urllib.request
import re

req = urllib.request.Request(
    'https://www.browardclerk.org/Web2',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print('Status:', resp.status)
        for m in re.finditer(r'<a\s+([^>]*?)>(.*?)</a>', html, re.IGNORECASE | re.DOTALL):
            attrs, txt = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()
            href_m = re.search(r'href=[\'"]([^\'"]+)[\'"]', attrs, re.IGNORECASE)
            id_m = re.search(r'id=[\'"]([^\'"]+)[\'"]', attrs, re.IGNORECASE)
            href = href_m.group(1) if href_m else ''
            el_id = id_m.group(1) if id_m else ''
            if any(k in txt.lower() or k in href.lower() for k in ['case', 'search', 'premium', 'glossary']):
                print(f"ID: {el_id:15} | HREF: {href:50} | TEXT: {txt}")
except Exception as e:
    print('Error:', e)
