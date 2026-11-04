import re

path = r"d:\scratch\Bot_UAIC\docs\Implementation Reports\BROWSER_AUTOMATION_VERIFICATION_REPORT.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

replacement = """```mermaid
flowchart TD
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

    Tab1 --> Scrape1["Search and Extract Cases"]
    Tab2 --> Scrape2["Search and Extract Cases"]
    Tab3 --> Scrape3["Search and Extract Cases"]
    Tab4 --> Scrape4["Search and Extract Cases"]
    Tab5 --> Scrape5["Search and Extract Cases"]
    Tab6 --> Scrape6["Search and Extract Cases"]
    Tab7 --> Scrape7["Search and Extract Cases"]
    Tab8 --> Scrape8["Search and Extract Cases"]

    Scrape1 --> Close1["Close Tab 1 (Context Remains Open)"]
    Scrape2 --> Close2["Close Tab 2 (Context Remains Open)"]
    Scrape3 --> Close3["Close Tab 3 (Context Remains Open)"]
    Scrape4 --> Close4["Close Tab 4 (Context Remains Open)"]
    Scrape5 --> Close5["Close Tab 5 (Context Remains Open)"]
    Scrape6 --> Close6["Close Tab 6 (Context Remains Open)"]
    Scrape7 --> Close7["Close Tab 7 (Context Remains Open)"]
    Scrape8 --> Close8["Close Tab 8 (Context Remains Open)"]

    Close1 --> Teardown["Clean Session Shutdown"]
    Close2 --> Teardown
    Close3 --> Teardown
    Close4 --> Teardown
    Close5 --> Teardown
    Close6 --> Teardown
    Close7 --> Teardown
    Close8 --> Teardown
```"""

pattern = r"```mermaid\s*flowchart TD.*?Teardown\n```"
new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
if new_text == text:
    # Try finding between ```mermaid and ```
    start = text.find("```mermaid\nflowchart TD")
    end = text.find("```\n\n### Benefits", start)
    if start != -1 and end != -1:
        new_text = text[:start] + replacement + text[end+3:]

with open(path, "w", encoding="utf-8") as f:
    f.write(new_text)

print("Updated BROWSER_AUTOMATION_VERIFICATION_REPORT.md successfully")

