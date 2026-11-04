with open('scripts/record_broward_genuine_attended.py', encoding='utf-8') as f:
    content = f.read()

target1 = '        logger.info("Opening extensions verification page for authentic Developer Mode & Extension setup...")'
replacement1 = '''        active_ext_id = (ext_status.get("extension_id") if isinstance(ext_status, dict) else None) or getattr(session, "extension_id", None) or "nggficlddfbeclbjkefphnblclmmadko"
        logger.info(f"Opening extensions verification page for authentic Developer Mode & Extension setup (Active ID: {active_ext_id})...")'''

if target1 in content:
    content = content.replace(target1, replacement1, 1)

target2 = "idVal.textContent = 'fignfifoniblkonapihmkfakmlgkbkcf';"
replacement2 = "idVal.textContent = f'{active_ext_id}';"

# In raw multi-line string in python where f""" is used:
# Let's check how idVal.textContent is written
old_card_id = "idVal.textContent = 'fignfifoniblkonapihmkfakmlgkbkcf';"
new_card_id = "idVal.textContent = '{active_ext_id}';"
if old_card_id in content:
    content = content.replace(old_card_id, new_card_id, 1)

target3 = '"implementation_id": "IMP-2026-1030-003",'
replacement3 = '"implementation_id": "IMP-2026-1030-004",'
if target3 in content:
    content = content.replace(target3, replacement3, 1)

target4 = '"extension_id": "fignfifoniblkonapihmkfakmlgkbkcf",'
replacement4 = '"extension_id": active_ext_id,'
if target4 in content:
    content = content.replace(target4, replacement4, 1)

with open('scripts/record_broward_genuine_attended.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated scripts/record_broward_genuine_attended.py')
