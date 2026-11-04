"""
Synchronize cspell.json and .vscode/settings.json custom dictionary words.
Maintains case-insensitive alphabetical sorting, exact parity, and 4-space indentation.
"""
import json
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
cspell_path = root_dir / "cspell.json"
settings_path = root_dir / ".vscode" / "settings.json"

with open(cspell_path, "r", encoding="utf-8") as f:
    cspell_data = json.load(f)

with open(settings_path, "r", encoding="utf-8") as f:
    settings_data = json.load(f)

cspell_words = set(cspell_data.get("words", []))
settings_words = set(settings_data.get("cSpell.words", []))

# Union of both sets
all_words = sorted(list(cspell_words | settings_words), key=lambda x: (x.lower(), x))

cspell_data["words"] = all_words
settings_data["cSpell.words"] = all_words

with open(cspell_path, "w", encoding="utf-8") as f:
    json.dump(cspell_data, f, indent=4)
    f.write("\n")

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings_data, f, indent=4)
    f.write("\n")

print(f"Synchronized cspell.json and .vscode/settings.json: {len(all_words)} words.")
