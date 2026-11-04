with open('backend/app/automation/browser_manager.py', encoding='utf-8') as f:
    content = f.read()

target = '''KNOWN_ANTICAPTCHA_IDS: list[str] = [
    "okbjeoddobbhhjdekgnjfloflgbpojjk",  # Unpacked Anti-Captcha extension ID in Bot_UAIC workspace'''

replacement = '''KNOWN_ANTICAPTCHA_IDS: list[str] = [
    "nggficlddfbeclbjkefphnblclmmadko",  # Cryptographic PEM public key ID for anticaptcha-plugin_v0.83
    "okbjeoddobbhhjdekgnjfloflgbpojjk",  # Unpacked Anti-Captcha extension ID in Bot_UAIC workspace'''

if target in content:
    content = content.replace(target, replacement, 1)

pref_target = 'pref_file.write_text(json.dumps(prefs, indent=2), encoding="utf-8")'
pref_replacement = '''pref_file.write_text(json.dumps(prefs, indent=2), encoding="utf-8")

            # Also ensure profile Local State has developer_mode enabled
            try:
                local_state_file = pref_file.parent.parent / "Local State"
                if local_state_file.parent.exists():
                    ls_data: dict[str, Any] = {}
                    if local_state_file.is_file():
                        try:
                            ls_data = json.loads(local_state_file.read_text(encoding="utf-8"))
                        except Exception:
                            ls_data = {}
                    ls_ext = ls_data.setdefault("extensions", {})
                    ls_ui = ls_ext.setdefault("ui", {})
                    ls_ui["developer_mode"] = True
                    local_state_file.write_text(json.dumps(ls_data, indent=2), encoding="utf-8")
            except Exception as ls_err:
                logger.debug(f"Local State developer_mode note: {ls_err}")'''

if pref_target in content:
    content = content.replace(pref_target, pref_replacement, 1)

with open('backend/app/automation/browser_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Successfully patched browser_manager.py')
