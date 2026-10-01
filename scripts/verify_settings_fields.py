fields = [
    "anticaptcha_api_key",
    "anticaptcha_enabled",
    "anticaptcha_auto_submit",
    "anticaptcha_play_sounds",
    "anticaptcha_solve_recaptcha2",
    "anticaptcha_solve_invisible",
    "anticaptcha_solve_recaptcha3",
    "anticaptcha_recaptcha3_score",
    "anticaptcha_solve_hcaptcha",
    "anticaptcha_solve_turnstile",
    "anticaptcha_solve_funcaptcha",
    "anticaptcha_solve_geetest",
    "extension_setup_verified",
    "extension_setup_timestamp",
    "chrome_binary_path",
    "chrome_extension_dir",
    "browser_engine",
    "headless",
    "slow_mo",
    "timeout",
    "typing_speed_mode",
    "typing_delay_ms",
    "action_pacing_ms",
    "stealth_clicks",
    "max_concurrent_claims"
]

with open('frontend/src/app/settings/page.tsx', 'r', encoding='utf-8') as f:
    page_content = f.read()

print("Verifying Automation & AntiCaptcha fields in settings/page.tsx:")
all_found = True
for fld in fields:
    present = fld in page_content
    print(f" - {fld}: {'FOUND' if present else 'MISSING'}")
    if not present:
        all_found = False

print(f"\nAll fields present: {all_found}")
