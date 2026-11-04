import json

new_words = [
    "ehthumbs",
    "emptively",
    "htmlcov",
    "libpq",
    "monkeypatch",
    "nopw",
    "pyvenv",
    "setattr",
    "tempmediaStorage",
    "topbar",
    "Vercel",
    "vercel",
]

# 1. Update cspell.json
with open("cspell.json", "r", encoding="utf-8") as f:
    cspell_data = json.load(f)

cspell_words = set(cspell_data.get("words", []))
cspell_words.update(new_words)
cspell_data["words"] = sorted(list(cspell_words), key=lambda x: (x.lower(), x))

with open("cspell.json", "w", encoding="utf-8") as f:
    json.dump(cspell_data, f, indent=4)
    f.write("\n")

print(f"Updated cspell.json: {len(cspell_data['words'])} words")

# 2. Update .vscode/settings.json
with open(".vscode/settings.json", "r", encoding="utf-8") as f:
    vscode_data = json.load(f)

vscode_words = set(vscode_data.get("cSpell.words", []))
vscode_words.update(new_words)
vscode_data["cSpell.words"] = sorted(list(vscode_words), key=lambda x: (x.lower(), x))

with open(".vscode/settings.json", "w", encoding="utf-8") as f:
    json.dump(vscode_data, f, indent=4)
    f.write("\n")

print(f"Updated .vscode/settings.json: {len(vscode_data['cSpell.words'])} words")
