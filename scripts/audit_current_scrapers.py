import os
import re

scrapers = {
    'Broward': 'backend/app/automation/florida/broward.py',
    'Hillsborough': 'backend/app/automation/florida/hillsborough.py',
    'Miami': 'backend/app/automation/florida/miami.py',
    'Harris County Clerk': 'backend/app/automation/texas/harris_cclerk.py',
    'Dallas': 'backend/app/automation/texas/dallas.py',
    'Harris JP': 'backend/app/automation/texas/harris_jp.py',
    'Harris District': 'backend/app/automation/texas/harris_district.py',
    'Travis': 'backend/app/automation/texas/travis.py',
}

for name, path in scrapers.items():
    print("=" * 80)
    print(f"PYTHON SCRAPER: {name} ({path})")
    print("=" * 80)
    if not os.path.exists(path):
        print("  FILE NOT FOUND!")
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # URL
    urls = re.findall(r'PORTAL_[A-Z_]+_URL\s*=\s*["\']([^"\']+)["\']', content)
    if not urls:
        urls = re.findall(r'base_url\s*:\s*str\s*=\s*["\']([^"\']+)["\']', content)
    print(f"  Configured URL: {urls}")

    # Key methods
    methods = re.findall(r'def ([a-zA-Z_0-9]+)\(self[^)]*\):', content)
    print(f"  Methods: {methods}")

    # CSS selectors / IDs queried
    selectors = set(re.findall(r'page\.(?:locator|query_selector|wait_for_selector|fill|click)\(["\']([^"\']+)["\']', content))
    print(f"  Selectors used ({len(selectors)}):")
    for s in sorted(selectors)[:15]:
        print(f"    {s}")
    if len(selectors) > 15:
        print(f"    ... and {len(selectors)-15} more")

    # Output schema keys in parse_results or scrape
    dict_keys = set(re.findall(r'["\'](CaseNumber|CaseStyle|FilingDate|CaseStatus|CaseType)["\']', content))
    print(f"  Extracted fields: {dict_keys}")
