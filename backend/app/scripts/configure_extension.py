import os

path = r"D:\UAIG\Bot Automation Project\anticaptcha-plugin_v0.83 1\js\config_ac_api_key.js"
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = content.replace("var antiCapthaPredefinedApiKey = '';", "var antiCapthaPredefinedApiKey = '28b486b8f31f74c6bf4453735815aa53';")
    content = content.replace("auto_submit_form: false,", "auto_submit_form: true,")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Configured antiCaptchaPredefinedApiKey and auto_submit_form in AntiCaptcha plugin.")
else:
    print("ERROR: Extension path not found.")
