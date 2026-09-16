import os
import re

file_path = os.path.join("frontend", "src", "app", "settings", "page.tsx")

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
    lines = content.splitlines()

print(f"Total lines: {len(lines)}")

# Find tab definitions in 'const tabs = ['
tabs_match = re.search(r"const tabs\s*=\s*\[(.*?)\];", content, re.DOTALL)
if tabs_match:
    print("\n--- Defined Tabs in Navigation ---")
    print(tabs_match.group(1).strip())

# Scan for h2/h3/h4 with multi-line support
pattern = re.compile(r'\{activeTab === "([^"]+)"')
for i, line in enumerate(lines):
    m = pattern.search(line)
    if m:
        tab_id = m.group(1)
        print(f"\n=======================================================")
        print(f"[Line {i+1}] TAB ID: '{tab_id}'")
        print(f"=======================================================")
        # Look ahead until the next activeTab
        end_idx = len(lines)
        for k in range(i+1, len(lines)):
            if pattern.search(lines[k]):
                end_idx = k
                break
        
        tab_chunk = "\n".join(lines[i:end_idx])
        # Find all h2, h3, h4
        headers = re.findall(r'<h[234][^>]*>(.*?)</h[234]>', tab_chunk, re.DOTALL)
        for h in headers:
            clean_h = re.sub(r'<[^>]+>', '', h).strip()
            clean_h = re.sub(r'\s+', ' ', clean_h)
            if clean_h and not clean_h.startswith('{'):
                print(f"   • {clean_h}")
        # Also look for any button labels or section banners
        cards = re.findall(r'(\/\* =+ \*\/|\/\* [^*]+ \*\/)', tab_chunk)
        for c in cards[:10]:
            if any(term in c for term in ['CARD', 'SECTION', 'PANEL', 'MODAL', 'TAB']):
                print(f"     [Comment] {c.strip()}")

