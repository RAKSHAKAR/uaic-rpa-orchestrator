import json

words_to_add = [
    "addgroup",
    "addopts",
    "adduser",
    "errorlevel",
    "filterwarnings",
    "libc",
    "minversion",
    "nextjs",
    "setuptools",
    "testpaths",
]

ignore_paths = [
    "node_modules",
    "node_modules/**",
    "**/node_modules/**",
    ".next",
    ".next/**",
    "**/.next/**",
    ".venv",
    ".venv/**",
    "**/.venv/**",
    "backend/.venv/**",
    "frontend/node_modules/**",
    "frontend/.next/**",
    "*.lock",
    "*.min.js",
    "dist",
    "dist/**",
    "build",
    "build/**",
    "anticaptcha-plugin_v0.83",
    "anticaptcha-plugin_v0.83/**",
    "BotCreation_1_0_0_7",
    "BotCreation_1_0_0_7/**",
    "v4_subflows",
    "v4_subflows/**",
    "backend/test_two_step_profile/**",
    "backend/scratch/**",
    "backend/logs/**",
    "logs/**",
    "backend/data/**",
    "data/**",
    "exports/**",
    "backend/exports/**",
    "backend/screenshots/**",
    "screenshots/**",
    "backend/uploads/**",
    "uploads/**",
    "docs/recordings/**",
    "docs/frames/**",
    "docs/images/**",
    "**/*.tsbuildinfo",
    "**/*.log",
    "**/*.db*",
    "**/*.wal",
]

# 1. Update cspell.json
with open("cspell.json", "r", encoding="utf-8") as f:
    cspell_data = json.load(f)

current_words = set(cspell_data.get("words", []))
current_words.update(words_to_add)
sorted_words = sorted(list(current_words), key=lambda s: s.lower())

cspell_data["words"] = sorted_words
cspell_data["ignorePaths"] = sorted(list(set(ignore_paths)))

with open("cspell.json", "w", encoding="utf-8") as f:
    json.dump(cspell_data, f, indent=2)
    f.write("\n")

print(f"Updated cspell.json: {len(sorted_words)} words, {len(cspell_data['ignorePaths'])} ignorePaths")

# 2. Update .vscode/settings.json
with open(".vscode/settings.json", "r", encoding="utf-8") as f:
    settings_data = json.load(f)

settings_data["cSpell.words"] = sorted_words
settings_data["cSpell.ignorePaths"] = sorted(list(set(ignore_paths)))

if "files.exclude" in settings_data:
    settings_data["files.exclude"]["**/*.tsbuildinfo"] = True
if "search.exclude" in settings_data:
    settings_data["search.exclude"]["**/*.tsbuildinfo"] = True

with open(".vscode/settings.json", "w", encoding="utf-8") as f:
    json.dump(settings_data, f, indent=4)
    f.write("\n")

print(f"Updated .vscode/settings.json: {len(sorted_words)} words, {len(settings_data['cSpell.ignorePaths'])} cSpell.ignorePaths")

