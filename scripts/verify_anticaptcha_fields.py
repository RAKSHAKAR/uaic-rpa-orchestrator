import re

with open('frontend/src/types/index.ts', 'r', encoding='utf-8') as f:
    types_content = f.read()

# Extract AntiCaptchaSettings interface
match = re.search(r'export interface AntiCaptchaSettings \{([^}]+)\}', types_content)
if match:
    fields = [line.strip().split('?:')[0].split(':')[0].strip() for line in match.group(1).split(';') if line.strip()]
    print("AntiCaptchaSettings fields in index.ts:")
    for fld in fields:
        print(f" - {fld}")

with open('frontend/src/app/settings/page.tsx', 'r', encoding='utf-8') as f:
    page_content = f.read()

print("\nChecking presence of each AntiCaptcha field in settings/page.tsx:")
for fld in fields:
    present = f"anticaptcha.{fld}" in page_content or f"settings.anticaptcha?.{fld}" in page_content or f"settings.anticaptcha.{fld}" in page_content or f"anticaptcha_{fld}" in page_content
    print(f" - {fld}: {'FOUND' if present else 'MISSING'}")
