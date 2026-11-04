with open('backend/app/services/settings_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Make sure human_interaction_mode="unattended" is present in get_default_settings()
if 'human_interaction_mode="unattended"' not in text:
    text = text.replace(
        'stealth_clicks=True,',
        'stealth_clicks=True,\n            human_interaction_mode="unattended",\n            enable_screen_recording=False,'
    )
    with open('backend/app/services/settings_service.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("settings_service.py updated with human_interaction_mode='unattended'")

# Update test_imp_2026_1031_003.py
with open('backend/tests/test_imp_2026_1031_003.py', 'r', encoding='utf-8') as f:
    test_text = f.read()

test_text = test_text.replace(
    'assert result["valid_count"] == 1\n    record = result["records"][0]',
    'assert result["valid_rows"] == 1\n    record = result["records_to_insert"][0]'
)

with open('backend/tests/test_imp_2026_1031_003.py', 'w', encoding='utf-8') as f:
    test_text = test_text.replace(
        'assert result["valid_count"] == 1\n    record = result["records"][0]',
        'assert result["valid_rows"] == 1\n    record = result["records_to_insert"][0]'
    )
    f.write(test_text)
print("test_imp_2026_1031_003.py updated")

