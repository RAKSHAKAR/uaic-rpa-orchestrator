with open("frontend/src/app/settings/page.tsx", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "activeTab" in line or "queue" in line.lower() and "tab" in line.lower():
            if any(term in line for term in ["queue", "setActiveTab", "activeTab ==="]):
                print(f"{idx}: {line.strip()[:100]}")
