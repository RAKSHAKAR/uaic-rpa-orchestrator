# cspell:disable
"""Synchronize cspell.json and .vscode/settings.json with newly introduced valid terms."""

import json
from pathlib import Path

# 1. Fix typos in files
ec_path = Path("backend/app/services/error_classifier.py")
if ec_path.exists():
    text = ec_path.read_text(encoding="utf-8")
    text = text.replace("Serialise", "Serialize")
    text = text.replace("serialise", "serialize")
    ec_path.write_text(text, encoding="utf-8")

report_path = Path("docs/Reports/CAPTCHA_ASSESSMENT_REPORT.md")
if report_path.exists():
    text = report_path.read_text(encoding="utf-8")
    text = text.replace("synchronisation", "synchronization")
    report_path.write_text(text, encoding="utf-8")

# 2. Add domain terms to cspell
new_words = [
    "anyio",
    "configfile",
    "dataclass",
    "pluggy",
    "redispatch",
    "Redispatch",
    "REDISPATCH",
    "RETRYABILITY",
    "rootdir",
    "SRCH",
]

# Update cspell.json
cspell_file = Path("cspell.json")
if cspell_file.exists():
    data = json.loads(cspell_file.read_text(encoding="utf-8"))
    words = set(data.get("words", []))
    words.update(new_words)
    data["words"] = sorted(list(words), key=lambda x: (x.lower(), x))
    cspell_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

# Update .vscode/settings.json
vscode_file = Path(".vscode/settings.json")
if vscode_file.exists():
    vscode_data = json.loads(vscode_file.read_text(encoding="utf-8"))
    vscode_words = set(vscode_data.get("cSpell.words", []))
    vscode_words.update(new_words)
    vscode_data["cSpell.words"] = sorted(list(vscode_words), key=lambda x: (x.lower(), x))
    vscode_file.write_text(json.dumps(vscode_data, indent=4) + "\n", encoding="utf-8")
