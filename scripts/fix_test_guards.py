with open('backend/app/api/v1/endpoints/settings.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_ver_code = 'detected_ver = ChromeSession.get_browser_version(browser_engine, chrome_exe)'
new_ver_code = '''detected_ver = None
        try:
            raw_ver = ChromeSession.get_browser_version(browser_engine, chrome_exe)
            if isinstance(raw_ver, str):
                detected_ver = raw_ver
        except Exception:
            pass'''
if old_ver_code in text:
    text = text.replace(old_ver_code, new_ver_code)
    with open('backend/app/api/v1/endpoints/settings.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('settings.py patched')

with open('backend/app/services/settings_service.py', 'r', encoding='utf-8') as f:
    st_text = f.read()

st_text = st_text.replace(
    'browser_engine="chrome",\n            use_chrome_browser=True,',
    'browser_engine="chromium",\n            use_chrome_browser=False,'
)
with open('backend/app/services/settings_service.py', 'w', encoding='utf-8') as f:
    f.write(st_text)
print('settings_service.py patched')

