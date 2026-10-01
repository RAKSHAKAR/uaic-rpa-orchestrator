with open('scripts/old_extension_tab.txt', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in old extension tab: {len(lines)}")
for i, line in enumerate(lines):
    s = line.strip()
    if s.startswith('<h') or s.startswith('<button') or 'Step' in s or 'step' in s or 'Pin' in s or 'Toggle' in s or 'toggle' in s or 'Balance' in s or 'Health' in s or 'Browser' in s or 'Test' in s or 'Launch' in s:
        print(f"{i:4d}: {s[:120]}")
