import subprocess

out = subprocess.check_output(['git', 'show', 'HEAD:frontend/src/app/settings/page.tsx'], text=True, encoding='utf-8')
target = '{activeTab === "extension"'
start = out.find(target)
next_tab = out.find('{activeTab ===', start + len(target))
print('Found at:', start, 'Next at:', next_tab)
with open('scripts/old_extension_tab.txt', 'w', encoding='utf-8') as f:
    f.write(out[start:next_tab])
print('Saved', next_tab - start, 'bytes to scripts/old_extension_tab.txt')
