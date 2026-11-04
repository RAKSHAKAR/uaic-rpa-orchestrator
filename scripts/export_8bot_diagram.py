import os
from playwright.sync_api import sync_playwright

mermaid_code = """flowchart TD
    Init["BrowserManager.launch_session()"] --> Launch["Launch Single Chrome Instance with AntiCaptcha"]
    Launch --> Context["Create Persistent BrowserContext"]

    Context --> FL_Batch["Florida Portals Batch"]
    Context --> TX_Batch["Texas Portals Batch"]

    subgraph FL["Florida Portals (Concurrent Sessions)"]
        Tab1["Tab 1: Florida Portal (Broward County)"]
        Tab2["Tab 2: Florida Portal (Hillsborough County)"]
        Tab3["Tab 3: Florida Portal (Miami-Dade County)"]
        
        Tab1 --> S1["Search & Extract Cases (Broward)"]
        Tab2 --> S2["Search & Extract Cases (Hillsborough)"]
        Tab3 --> S3["Search & Extract Cases (Miami-Dade)"]
        
        S1 --> C1["Close Tab 1 (Context Remains Open)"]
        S2 --> C2["Close Tab 2 (Context Remains Open)"]
        S3 --> C3["Close Tab 3 (Context Remains Open)"]
    end

    subgraph TX["Texas Portals (Concurrent Sessions)"]
        Tab4["Tab 4: Texas Portal (Dallas County)"]
        Tab5["Tab 5: Texas Portal (Travis County)"]
        Tab6["Tab 6: Texas Portal (Harris JP)"]
        Tab7["Tab 7: Texas Portal (Harris County Clerk)"]
        Tab8["Tab 8: Texas Portal (Harris District Clerk)"]
        
        Tab4 --> S4["Search & Extract Cases (Dallas)"]
        Tab5 --> S5["Search & Extract Cases (Travis)"]
        Tab6 --> S6["Search & Extract Cases (Harris JP)"]
        Tab7 --> S7["Search & Extract Cases (Harris Clerk)"]
        Tab8 --> S8["Search & Extract Cases (Harris District)"]
        
        S4 --> C4["Close Tab 4 (Context Remains Open)"]
        S5 --> C5["Close Tab 5 (Context Remains Open)"]
        S6 --> C6["Close Tab 6 (Context Remains Open)"]
        S7 --> C7["Close Tab 7 (Context Remains Open)"]
        S8 --> C8["Close Tab 8 (Context Remains Open)"]
    end

    FL_Batch --> Tab1 & Tab2 & Tab3
    TX_Batch --> Tab4 & Tab5 & Tab6 & Tab7 & Tab8

    C1 & C2 & C3 & C4 & C5 & C6 & C7 & C8 --> Teardown["Clean Session Shutdown"]
"""

# Also test a pure flat version with all 8 bots clearly arranged
mermaid_code_flat = """flowchart TD
    Init["BrowserManager.launch_session()"] --> Launch["Launch Single Chrome Instance with AntiCaptcha"]
    Launch --> Context["Create Persistent BrowserContext"]

    Context --> Tab1["Tab 1: Florida Portal (Broward)"]
    Context --> Tab2["Tab 2: Florida Portal (Hillsborough)"]
    Context --> Tab3["Tab 3: Florida Portal (Miami-Dade)"]
    Context --> Tab4["Tab 4: Texas Portal (Dallas)"]
    Context --> Tab5["Tab 5: Texas Portal (Travis)"]
    Context --> Tab6["Tab 6: Texas Portal (Harris JP)"]
    Context --> Tab7["Tab 7: Texas Portal (Harris County Clerk)"]
    Context --> Tab8["Tab 8: Texas Portal (Harris District Clerk)"]

    Tab1 --> Scrape1["Search & Extract Cases"]
    Tab2 --> Scrape2["Search & Extract Cases"]
    Tab3 --> Scrape3["Search & Extract Cases"]
    Tab4 --> Scrape4["Search & Extract Cases"]
    Tab5 --> Scrape5["Search & Extract Cases"]
    Tab6 --> Scrape6["Search & Extract Cases"]
    Tab7 --> Scrape7["Search & Extract Cases"]
    Tab8 --> Scrape8["Search & Extract Cases"]

    Scrape1 --> Close1["Close Tab 1 (Context Remains Open)"]
    Scrape2 --> Close2["Close Tab 2 (Context Remains Open)"]
    Scrape3 --> Close3["Close Tab 3 (Context Remains Open)"]
    Scrape4 --> Close4["Close Tab 4 (Context Remains Open)"]
    Scrape5 --> Close5["Close Tab 5 (Context Remains Open)"]
    Scrape6 --> Close6["Close Tab 6 (Context Remains Open)"]
    Scrape7 --> Close7["Close Tab 7 (Context Remains Open)"]
    Scrape8 --> Close8["Close Tab 8 (Context Remains Open)"]

    Close1 & Close2 & Close3 & Close4 & Close5 & Close6 & Close7 & Close8 --> Teardown["Clean Session Shutdown"]
"""

html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#1e293b',
                primaryTextColor: '#f8fafc',
                primaryBorderColor: '#38bdf8',
                lineColor: '#38bdf8',
                secondaryColor: '#0f172a',
                tertiaryColor: '#1e293b'
            }}
        }});
    </script>
    <style>
        body {{
            background: #0b1120;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            max-width: 1400px;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align: center; color: #38bdf8; margin-top: 0; font-size: 20px;">Multi-Tab Single-Session Orchestration Architecture (All 8 Bots)</h2>
        <div class="mermaid" id="diagram">
{mermaid_code}
        </div>
    </div>
</body>
</html>"""

out_html = r"d:\scratch\Bot_UAIC\scripts\render_8bot_diagram.html"
with open(out_html, "w", encoding="utf-8") as f:
    f.write(html)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1600, "height": 1400}, device_scale_factor=2)
    page.goto(f"file:///{out_html.replace(os.sep, '/')}")
    page.wait_for_timeout(3000)
    
    container = page.query_selector(".container")
    if container:
        png_path = r"d:\scratch\Bot_UAIC\docs\images\multi_tab_8bot_architecture.png"
        container.screenshot(path=png_path)
        print(f"Saved PNG to {png_path}")
        
    svg_el = page.query_selector("#diagram svg")
    if svg_el:
        svg_content = svg_el.evaluate("el => el.outerHTML")
        svg_path = r"d:\scratch\Bot_UAIC\docs\images\multi_tab_8bot_architecture.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Saved SVG to {svg_path}")
        
    browser.close()

