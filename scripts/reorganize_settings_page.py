import os
import shutil

file_path = os.path.join("frontend", "src", "app", "settings", "page.tsx")
backup_path = file_path + ".bak"
shutil.copyfile(file_path, backup_path)
print(f"Backed up {file_path} to {backup_path}")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update tabs array
old_tabs = """  const tabs = [
    { id: "guidewire", label: "APIs", icon: Zap },
    { id: "portals", label: "County Court Portals", icon: Globe },
    { id: "automation", label: "Browser & CAPTCHA", icon: ShieldCheck },
    { id: "proxy", label: "Proxy Settings", icon: Network },
    { id: "extension", label: "AntiCaptcha Extension", icon: Plug },
    { id: "email", label: "Email & Notifications", icon: Mail },
    { id: "storage", label: "Storage & Error Screenshots", icon: HardDrive },
    { id: "matcher", label: "RapidFuzz & Filters", icon: Sparkles },
    { id: "queue", label: "Task Queue & Alerts", icon: Layers },
  ];"""

new_tabs = """  const tabs = [
    { id: "guidewire", label: "APIs & Matching Engine", icon: Zap },
    { id: "portals", label: "County Court Portals", icon: Globe },
    { id: "automation", label: "Browser Automation & Fleet", icon: ShieldCheck },
    { id: "extension", label: "CAPTCHA Solver & Extension", icon: Plug },
    { id: "proxy", label: "Proxy Network", icon: Network },
    { id: "email", label: "Email & Notifications", icon: Mail },
    { id: "storage", label: "Storage & Retention", icon: HardDrive },
    { id: "queue", label: "Task Queue & Telemetry", icon: Layers },
  ];"""

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)
    print("[OK] Updated tabs navigation array")
else:
    print("[FAIL] Warning: Could not find exact old_tabs")

# 2. Extract RapidFuzz Engine Card from activeTab === "matcher"
# Let's find the card content from line 6003 to 6168
matcher_start_tag = '{activeTab === "matcher" && ('
matcher_end_tag = '{activeTab === "queue" && ('

idx_m_start = content.find(matcher_start_tag)
idx_q_start = content.find(matcher_end_tag)

if idx_m_start != -1 and idx_q_start != -1:
    matcher_block = content[idx_m_start:idx_q_start]
    # Inside matcher_block, get the card div
    card_start_str = '<div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">'
    card_start_idx = matcher_block.find(card_start_str)
    card_end_idx = matcher_block.rfind('</div>') + len('</div>')
    
    rapidfuzz_card = matcher_block[card_start_idx:card_end_idx]
    print(f"[OK] Extracted RapidFuzz card ({len(rapidfuzz_card)} chars)")
    
    # Remove activeTab === "matcher" block
    content = content[:idx_m_start] + content[idx_q_start:]
    print("[OK] Removed redundant activeTab === 'matcher' tab block")
    
    # Insert RapidFuzz card into activeTab === "guidewire", directly before the Fuzzy Match API Tester
    fuzzy_tester_comment = '{/* Fuzzy Match API Tester */}'
    if fuzzy_tester_comment in content:
        replacement = rapidfuzz_card + "\n\n            " + fuzzy_tester_comment
        content = content.replace(fuzzy_tester_comment, replacement, 1)
        print("[OK] Inserted RapidFuzz Engine card directly above Fuzzy Match API Tester in 'guidewire' tab")
    else:
        print("[FAIL] Warning: Could not find fuzzy_tester_comment")
else:
    print(f"[FAIL] Warning: Could not find matcher block (start: {idx_m_start}, q: {idx_q_start})")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved intermediate updates to page.tsx")
