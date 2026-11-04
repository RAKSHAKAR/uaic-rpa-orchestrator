import asyncio
import os
import re
from playwright.async_api import async_playwright

def md_to_html(md_text):
    # Split by mermaid blocks
    parts = re.split(r'(```mermaid[\s\S]*?```)', md_text)
    html_parts = []
    for part in parts:
        if part.startswith('```mermaid'):
            code = part[len('```mermaid'):-len('```')].strip()
            # Escape HTML
            escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_parts.append(f'<pre class="mermaid" style="all: unset;">{escaped}</pre>')
        else:
            # Simple line/paragraph rendering
            # We can use simple paragraph / header wraps
            lines = part.split('\n')
            for line in lines:
                if line.startswith('# '):
                    html_parts.append(f'<h1>{line[2:]}</h1>')
                elif line.startswith('## '):
                    html_parts.append(f'<h2>{line[3:]}</h2>')
                elif line.startswith('### '):
                    html_parts.append(f'<h3>{line[4:]}</h3>')
                elif line.startswith('---'):
                    html_parts.append('<hr>')
                elif line.strip():
                    html_parts.append(f'<p>{line}</p>')
                    
    bundle_path = r'C:/Users/priyer/.vscode/extensions/bierner.markdown-mermaid-1.32.1/dist-preview/index.bundle.js'
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    background-color: #121314;
    color: #cccccc;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe WPC', 'Segoe UI', system-ui, 'Ubuntu', 'Droid Sans', sans-serif;
    font-size: 14px;
    padding: 20px;
    line-height: 1.6;
}}
h2 {{ border-bottom: 1px solid #333; padding-bottom: 4px; }}
hr {{ border: 0; border-top: 1px solid #333; margin: 20px 0; }}
</style>
<script id="markdown-mermaid" type="application/json" data-config='{{"darkModeTheme":"dark","lightModeTheme":"default","clickDrag":"alt","showControls":"always","resizable":true}}'></script>
</head>
<body class="vscode-dark">
{''.join(html_parts)}
<script src="file:///{bundle_path}"></script>
</body>
</html>"""

async def run():
    with open('UAIC_FINAL_100_RECORD_CROSS_STATE_ACCEPTANCE_REPORT.md', 'r', encoding='utf-8') as f:
        md = f.read()
    html = md_to_html(md)
    with open('scripts/full_report_test.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1024, 'height': 800})
        
        abs_path = os.path.abspath('scripts/full_report_test.html').replace('\\', '/')
        await page.goto(f'file:///{abs_path}')
        await page.wait_for_timeout(3000)
        
        # Scroll to section 9
        h2 = await page.query_selector('h2:has-text("9. Eight-Bot Architecture")')
        if h2:
            await h2.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)
            await page.screenshot(path='scripts/full_report_section_9.png')
            print('Screenshot taken of section 9 in full report!')
        else:
            print('Section 9 header not found!')
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
