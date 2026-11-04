import os
import glob
import re
from playwright.sync_api import sync_playwright

md_files = glob.glob(r"d:\scratch\Bot_UAIC\docs\**\*.md", recursive=True)

blocks = []
for fpath in md_files:
    with open(fpath, "r", encoding="utf-8") as f:
        text = f.read()
    found = re.findall(r"```mermaid\s*\n(.*?)\n```", text, re.DOTALL)
    for idx, b in enumerate(found):
        blocks.append({
            "file": os.path.relpath(fpath, r"d:\scratch\Bot_UAIC"),
            "index": idx + 1,
            "code": b.strip()
        })

print(f"Total mermaid diagrams found across docs: {len(blocks)}")

# Build HTML with each diagram in its own container
divs = ""
for i, item in enumerate(blocks):
    divs += f"""
    <div style="margin: 20px 0; padding: 15px; border: 1px solid #334155; border-radius: 8px;">
        <h3>{item['file']} (Diagram #{item['index']})</h3>
        <div class="mermaid" id="diagram-{i}">
{item['code']}
        </div>
    </div>
    """

html = f"""<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            securityLevel: 'loose'
        }});
    </script>
</head>
<body style="background: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 20px;">
    <h1>All Mermaid Diagrams Diagnostic Suite</h1>
    {divs}
</body>
</html>"""

test_html_path = r"d:\scratch\Bot_UAIC\scripts\all_mermaids_test.html"
with open(test_html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generated. Now validating in Playwright headless Chrome...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    
    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    page.goto(f"file:///{test_html_path.replace(os.sep, '/')}")
    page.wait_for_timeout(4000)

    # Check each container
    for i, item in enumerate(blocks):
        container = page.query_selector(f"#diagram-{i}")
        svg = container.query_selector("svg") if container else None
        if svg:
            bbox = svg.bounding_box()
            print(f"  [PASS] {item['file']} (#{item['index']}): SVG rendered {bbox['width']:.0f}x{bbox['height']:.0f}px")
        else:
            err_text = container.inner_text() if container else "Not found"
            print(f"  [FAIL] {item['file']} (#{item['index']}): NO SVG! Error: {err_text[:150]}")

    if page_errors:
        print("\nPage errors encountered:")
        for e in page_errors:
            print("  ", e)

    browser.close()

