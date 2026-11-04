with open('scripts/record_broward_genuine_attended.py', encoding='utf-8') as f:
    content = f.read()

target = '        browser_engine=auto.browser_engine,'
replacement = '        browser_engine="chrome",'

if target in content:
    content = content.replace(target, replacement, 1)

with open('scripts/record_broward_genuine_attended.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated browser_engine to chrome in record_broward_genuine_attended.py')
