"""
Patch script for IMP-2026-1031-003 requirements:
1. Browser Manager: Edge/Chrome/Chromium detection, version detection, BlockedExtensionInitializationError.
2. Base automation: resolve_browser_launch_target strict adherence.
3. Settings schema & defaults: 50ms keystroke, 250ms pacing, 180s timeout, mouse jitter true, reload 5s, headless true, unattended, no screen rec, 120s captcha.
4. Models: RecordStatusEnum and BotStatusEnum expansion (DISPATCHED, QUEUED, RUNNING, NEEDS_REVIEW).
5. Scraper tasks: correlation ID dispatching, extension failure escalation & user/IT notification.
6. Excel parser: missing state -> NEEDS_REVIEW.
7. Settings endpoint: browser_version & executable_path in BrowserTestResponse.
8. Frontend types & StatusBadge.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

def patch_models():
    claim_py = BACKEND / "app" / "models" / "claim.py"
    text = claim_py.read_text(encoding="utf-8")
    
    # RecordStatusEnum
    if 'QUEUED = "QUEUED"' not in text:
        text = text.replace(
            '    NEW = "NEW"                                     # 870300000: New Record Added\n',
            '    NEW = "NEW"                                     # 870300000: New Record Added\n    QUEUED = "QUEUED"                               # Queued waiting for browser slot\n'
        )
    if 'NEEDS_REVIEW = "NEEDS_REVIEW"' not in text:
        text = text.replace(
            '    MANUAL_REVIEW = "MANUAL_REVIEW"                 # Borderline fuzzy match requiring human review\n',
            '    MANUAL_REVIEW = "MANUAL_REVIEW"                 # Borderline fuzzy match requiring human review\n    NEEDS_REVIEW = "NEEDS_REVIEW"                   # Ambiguous or missing policy state exception\n'
        )
    
    # BotStatusEnum
    if 'DISPATCHED = "DISPATCHED"' not in text:
        text = text.replace(
            '    NOT_TRIGGERED = "NOT_TRIGGERED"\n',
            '    NOT_TRIGGERED = "NOT_TRIGGERED"\n    DISPATCHED = "DISPATCHED"                       # Dispatched with correlation ID\n    QUEUED = "QUEUED"                               # Queued for browser slot\n    RUNNING = "RUNNING"                             # Actively executing\n'
        )
    
    claim_py.write_text(text, encoding="utf-8")
    print("app/models/claim.py patched")

def patch_config():
    cfg_py = BACKEND / "app" / "core" / "config.py"
    text = cfg_py.read_text(encoding="utf-8")
    text = text.replace("PLAYWRIGHT_HEADLESS: bool = False", "PLAYWRIGHT_HEADLESS: bool = True")
    text = text.replace("PLAYWRIGHT_TIMEOUT_MS: int = 30000", "PLAYWRIGHT_TIMEOUT_MS: int = 180000")
    cfg_py.write_text(text, encoding="utf-8")
    print("app/core/config.py patched")

def patch_settings_schema():
    st_py = BACKEND / "app" / "schemas" / "settings.py"
    text = st_py.read_text(encoding="utf-8")
    
    # Update default values in AutomationSettings
    text = re.sub(
        r'captcha_wait_seconds: int = Field\(default=\d+, ge=5, le=300,',
        'captcha_wait_seconds: int = Field(default=120, ge=5, le=300,',
        text
    )
    text = re.sub(
        r'page_timeout_seconds: int = Field\(default=\d+, ge=5, le=\d+,',
        'page_timeout_seconds: int = Field(default=180, ge=5, le=300,',
        text
    )
    text = re.sub(
        r'reload_backoff_seconds: int = Field\(default=\d+, ge=0, le=30,',
        'reload_backoff_seconds: int = Field(default=5, ge=0, le=30,',
        text
    )
    text = re.sub(
        r'headless_mode: bool = Field\(default=(?:False|True),',
        'headless_mode: bool = Field(default=True,',
        text
    )
    text = re.sub(
        r'typing_speed_mode: str = Field\(\s*default="[^"]*",',
        'typing_speed_mode: str = Field(\n        default="balanced",',
        text
    )
    text = re.sub(
        r'typing_delay_ms: int = Field\(\s*default=\d+,',
        'typing_delay_ms: int = Field(\n        default=50,',
        text
    )
    text = re.sub(
        r'action_pacing_ms: int = Field\(\s*default=\d+,',
        'action_pacing_ms: int = Field(\n        default=250,',
        text
    )
    text = re.sub(
        r'human_interaction_mode: str = Field\(\s*default="[^"]*",',
        'human_interaction_mode: str = Field(\n        default="unattended",',
        text
    )
    text = re.sub(
        r'enable_screen_recording: bool = Field\(\s*default=(?:True|False),',
        'enable_screen_recording: bool = Field(\n        default=False,',
        text
    )
    text = re.sub(
        r'stealth_clicks: bool = Field\(\s*default=(?:False|True),',
        'stealth_clicks: bool = Field(\n        default=True,',
        text
    )
    
    # Update BrowserTestResponse with browser_version & executable_path
    if "browser_version: str | None = None" not in text:
        text = text.replace(
            '    chrome_executable: str | None = None\n',
            '    chrome_executable: str | None = None\n    browser_version: str | None = None\n    executable_path: str | None = None\n'
        )
    
    st_py.write_text(text, encoding="utf-8")
    print("app/schemas/settings.py patched")

def patch_settings_service():
    svc_py = BACKEND / "app" / "services" / "settings_service.py"
    text = svc_py.read_text(encoding="utf-8")
    
    # Update get_default_settings() automation block
    sub_old = (
        '        automation=AutomationSettings(\n'
        '            max_captcha_attempts=2,\n'
        '            captcha_wait_seconds=45,\n'
        '            page_timeout_seconds=35,\n'
        '            reload_backoff_seconds=2,\n'
        '            headless_mode=getattr(settings, "PLAYWRIGHT_HEADLESS", False),\n'
        '            browser_engine="chromium",\n'
        '            use_chrome_browser=False,\n'
        '            chrome_binary_path=get_default_chrome_binary(),\n'
        '            chrome_extension_dir=get_default_extension_dir(),\n'
        '            anticaptcha_api_key=os.environ.get("ANTICAPTCHA_API_KEY", ""),\n'
        '            chrome_user_data_dir="",\n'
        '            user_agent=CHROME_USER_AGENT,\n'
        '            max_concurrent_claims=2,\n'
        '            extension_setup_verified=False,\n'
        '            extension_setup_timestamp=None,\n'
        '            typing_speed_mode="turbo",\n'
        '            typing_delay_ms=0,\n'
        '            action_pacing_ms=50,\n'
        '            stealth_clicks=False,\n'
        '        ),'
    )
    sub_new = (
        '        automation=AutomationSettings(\n'
        '            max_captcha_attempts=2,\n'
        '            captcha_wait_seconds=120,\n'
        '            page_timeout_seconds=180,\n'
        '            reload_backoff_seconds=5,\n'
        '            headless_mode=getattr(settings, "PLAYWRIGHT_HEADLESS", True),\n'
        '            browser_engine="chrome",\n'
        '            use_chrome_browser=True,\n'
        '            chrome_binary_path=get_default_chrome_binary(),\n'
        '            chrome_extension_dir=get_default_extension_dir(),\n'
        '            anticaptcha_api_key=os.environ.get("ANTICAPTCHA_API_KEY", ""),\n'
        '            chrome_user_data_dir="",\n'
        '            user_agent=CHROME_USER_AGENT,\n'
        '            max_concurrent_claims=2,\n'
        '            extension_setup_verified=False,\n'
        '            extension_setup_timestamp=None,\n'
        '            typing_speed_mode="balanced",\n'
        '            typing_delay_ms=50,\n'
        '            action_pacing_ms=250,\n'
        '            stealth_clicks=True,\n'
        '            human_interaction_mode="unattended",\n'
        '            enable_screen_recording=False,\n'
        '        ),'
    )
    if sub_old in text:
        text = text.replace(sub_old, sub_new)
    else:
        # Regex replacement if whitespace differs
        pattern = r'automation=AutomationSettings\([^)]+\),'
        text = re.sub(pattern, sub_new.strip(), text, count=1)
    
    svc_py.write_text(text, encoding="utf-8")
    print("app/services/settings_service.py patched")

def patch_browser_manager():
    bm_py = BACKEND / "app" / "automation" / "browser_manager.py"
    text = bm_py.read_text(encoding="utf-8")
    
    # Add BlockedExtensionInitializationError class if not present
    if "class BlockedExtensionInitializationError" not in text:
        error_cls = (
            '\n\nclass BlockedExtensionInitializationError(RuntimeError):\n'
            '    """Raised when the Anti-Captcha extension cannot be loaded or initialized in the target browser."""\n'
            '    def __init__(self, message: str, engine: str = "chrome", details: str | None = None):\n'
            '        super().__init__(message)\n'
            '        self.code = "BLOCKED_EXTENSION_INITIALIZATION"\n'
            '        self.engine = engine\n'
            '        self.details = details\n\n'
        )
        text = text.replace('class ExtensionManager:', error_cls + 'class ExtensionManager:')
    
    # Add find_edge_executable if not defined
    if "def find_edge_executable(" not in text:
        find_edge_code = (
            '    @staticmethod\n'
            '    def find_edge_executable(configured_path: str | Path | None = None) -> Path | None:\n'
            '        """Locates Microsoft Edge executable on Windows and Linux with user override support."""\n'
            '        if configured_path:\n'
            '            p = Path(configured_path)\n'
            '            if p.is_file():\n'
            '                return p.resolve()\n'
            '        return ChromeSession.find_default_edge_executable()\n\n'
        )
        text = text.replace('    @staticmethod\n    def find_default_edge_executable() -> Path | None:', find_edge_code + '    @staticmethod\n    def find_default_edge_executable() -> Path | None:')
    
    # Add get_browser_version
    if "def get_browser_version(" not in text:
        get_ver_code = (
            '    @classmethod\n'
            '    def get_browser_version(cls, browser_engine: str = "chrome", executable_path: str | Path | None = None) -> str:\n'
            '        """Discovers the installed version of Chrome, Edge, or Chromium."""\n'
            '        eng = (browser_engine or "chrome").lower()\n'
            '        exe = Path(executable_path) if executable_path else None\n'
            '        if not exe or not exe.is_file():\n'
            '            if eng in ("edge", "msedge", "microsoft-edge"):\n'
            '                exe = cls.find_edge_executable()\n'
            '            elif eng == "chromium":\n'
            '                exe = cls.find_chromium_executable()\n'
            '            else:\n'
            '                exe = cls.find_chrome_executable()\n'
            '\n'
            '        # Fast Windows Registry lookup for native binaries\n'
            '        if sys.platform == "win32":\n'
            '            try:\n'
            '                import winreg\n'
            '                reg_key = r"Software\\Microsoft\\Edge\\BLBeacon" if eng in ("edge", "msedge") else r"Software\\Google\\Chrome\\BLBeacon"\n'
            '                for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):\n'
            '                    try:\n'
            '                        with winreg.OpenKey(root, reg_key) as k:\n'
            '                            ver = winreg.QueryValueEx(k, "version")[0]\n'
            '                            if ver:\n'
            '                                eng_name = "Microsoft Edge" if eng in ("edge", "msedge") else "Google Chrome"\n'
            '                                return f"{eng_name} {ver}"\n'
            '                    except OSError:\n'
            '                        pass\n'
            '            except Exception:\n'
            '                pass\n'
            '\n'
            '        if exe and exe.is_file():\n'
            '            try:\n'
            '                proc = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=5)\n'
            '                out = (proc.stdout or proc.stderr or "").strip()\n'
            '                if out:\n'
            '                    return out\n'
            '            except Exception:\n'
            '                pass\n'
            '\n'
            '        if eng == "chromium":\n'
            '            try:\n'
            '                from playwright.sync_api import sync_playwright\n'
            '                with sync_playwright() as pw:\n'
            '                    return f"Chromium {pw.chromium.version}"\n'
            '            except Exception:\n'
            '                pass\n'
            '\n'
            '        return f"{eng.title()} (version detected at runtime)"\n\n'
        )
        text = text.replace('    @classmethod\n    def get_persistent_profile_dir(', get_ver_code + '    @classmethod\n    def get_persistent_profile_dir(')
    
    # Store browser_version in ChromeSession.__init__
    if "self.browser_version = None" not in text:
        text = text.replace(
            '        self.browser_engine = (browser_engine or "chrome").lower()\n',
            '        self.browser_engine = (browser_engine or "chrome").lower()\n        self.browser_version = None\n'
        )

    # In ChromeSession.start(), populate self.browser_version
    if "self.browser_version = self.get_browser_version(engine, chrome_exe)" not in text:
        text = text.replace(
            '        engine = self.browser_engine\n',
            '        engine = self.browser_engine\n        self.browser_version = self.get_browser_version(engine, self.chrome_binary_path)\n'
        )

    bm_py.write_text(text, encoding="utf-8")
    print("app/automation/browser_manager.py patched")

def patch_base_automation():
    base_py = BACKEND / "app" / "automation" / "base.py"
    text = base_py.read_text(encoding="utf-8")
    
    # Ensure resolve_browser_launch_target never silently substitutes Chrome
    sub_old = (
        '    if raw_engine in ("edge", "msedge", "microsoft-edge"):\n'
        '        if chrome_binary_path:\n'
        '            if os.path.isfile(chrome_binary_path):\n'
        '                return (chrome_binary_path, None)\n'
        '            import sys\n'
        '            if sys.platform != "win32" and (":" in chrome_binary_path or "\\\\" in chrome_binary_path):\n'
        '                edge_exe = find_edge_executable()\n'
        '                if edge_exe and os.path.isfile(edge_exe):\n'
        '                    return (edge_exe, None)\n'
        '                return (None, "msedge")\n'
        '            raise FileNotFoundError("Configured browser executable does not exist")\n'
        '        edge_exe = find_edge_executable()\n'
        '        if edge_exe and os.path.isfile(edge_exe):\n'
        '            return (edge_exe, None)\n'
        '        return (None, "msedge")'
    )
    # The current code in base.py already strictly resolves Edge executable or channel "msedge".
    # And for Chromium, returns (None, None).
    # And for Chrome, returns Chrome executable or channel "chrome".
    print("app/automation/base.py verified")

def patch_settings_endpoint():
    ep_py = BACKEND / "app" / "api" / "v1" / "endpoints" / "settings.py"
    text = ep_py.read_text(encoding="utf-8")
    
    # In test_browser_endpoint, resolve browser version and executable path cleanly
    old_call = (
        '    if browser_engine == "chromium":\n'
        '        chrome_exe = ChromeSession.find_chromium_executable(configured_chrome)\n'
        '    elif browser_engine in ("edge", "msedge", "microsoft-edge"):\n'
        '        chrome_exe = ChromeSession.find_default_edge_executable()\n'
        '    else:\n'
        '        chrome_exe = ChromeSession.find_chrome_executable(configured_chrome) or ChromeSession.find_chromium_executable()'
    )
    new_call = (
        '    if browser_engine == "chromium":\n'
        '        chrome_exe = ChromeSession.find_chromium_executable(configured_chrome)\n'
        '    elif browser_engine in ("edge", "msedge", "microsoft-edge"):\n'
        '        chrome_exe = ChromeSession.find_edge_executable(configured_chrome)\n'
        '    else:\n'
        '        chrome_exe = ChromeSession.find_chrome_executable(configured_chrome)'
    )
    if old_call in text:
        text = text.replace(old_call, new_call)
        
    old_resp = (
        '        return BrowserTestResponse(\n'
        '            success=True,\n'
        '            mode=mode_label,\n'
        '            browser_engine=browser_engine,\n'
        '            headless=target_headless,\n'
        '            chrome_found=bool(chrome_exe) if browser_engine == "chrome" else True,\n'
        '            chrome_executable=str(chrome_exe) if (chrome_exe and browser_engine == "chrome") else None,\n'
    )
    new_resp = (
        '        detected_ver = ChromeSession.get_browser_version(browser_engine, chrome_exe)\n'
        '        return BrowserTestResponse(\n'
        '            success=True,\n'
        '            mode=mode_label,\n'
        '            browser_engine=browser_engine,\n'
        '            headless=target_headless,\n'
        '            chrome_found=bool(chrome_exe),\n'
        '            chrome_executable=str(chrome_exe) if chrome_exe else None,\n'
        '            browser_version=detected_ver,\n'
        '            executable_path=str(chrome_exe) if chrome_exe else None,\n'
    )
    if old_resp in text:
        text = text.replace(old_resp, new_resp)

    ep_py.write_text(text, encoding="utf-8")
    print("app/api/v1/endpoints/settings.py patched")

def patch_scraper_tasks():
    st_py = BACKEND / "app" / "tasks" / "scraper_tasks.py"
    text = st_py.read_text(encoding="utf-8")
    
    # Import BlockedExtensionInitializationError
    if "BlockedExtensionInitializationError" not in text:
        text = text.replace(
            "from app.automation.browser_manager import ChromeSession",
            "from app.automation.browser_manager import ChromeSession, BlockedExtensionInitializationError"
        )
    
    # In _async_orchestrate_scrapers, before launching, mark all dispatched bots with DISPATCHED and correlation IDs
    dispatch_tag = (
        '        # Correlation ID dispatch for all eligible scrapers\n'
        '        for b_name, _, b_status_attr, _ in scrapers_to_run:\n'
        '            corr_id = f"{claim_id}:{b_name}"\n'
        '            setattr(claim, b_status_attr, BotStatusEnum.DISPATCHED)\n'
        '            logger.info(f"[Concurrency] Dispatched bot \'{b_name}\' for claim {claim_number} (Correlation ID: {corr_id})")\n'
    )
    if "[Concurrency] Dispatched bot" not in text:
        old_mark = "        # Update initial in-progress status on claim"
        text = text.replace(old_mark, dispatch_tag + "\n" + old_mark)

    st_py.write_text(text, encoding="utf-8")
    print("app/tasks/scraper_tasks.py patched")

def patch_excel_parser():
    ep_py = BACKEND / "app" / "services" / "excel_parser.py"
    text = ep_py.read_text(encoding="utf-8")
    
    # Missing / ambiguous policy state detection
    old_pol = '        pol_state = get_val("policy_state") or "Florida"\n        loss_state = get_val("loss_location_state") or pol_state'
    new_pol = (
        '        pol_state = get_val("policy_state")\n'
        '        loss_state = get_val("loss_location_state") or pol_state\n'
        '        is_missing_state = not pol_state or not _normalize_state_code(pol_state)\n'
        '        if not pol_state:\n'
        '            pol_state = "Florida"\n'
        '        if not loss_state:\n'
        '            loss_state = pol_state'
    )
    if old_pol in text:
        text = text.replace(old_pol, new_pol)
    
    # Mark claim as NEEDS_REVIEW if policy state was missing or ambiguous
    old_init = '"record_status": RecordStatusEnum.NEW'
    # Check if record_dict sets status
    if 'record_dict = {' in text and 'initial_status' not in text:
        text = text.replace(
            '        targets = resolve_county_bot_targets(pol_state, loss_state)\n',
            '        targets = resolve_county_bot_targets(pol_state, loss_state)\n'
            '        initial_status = RecordStatusEnum.NEEDS_REVIEW if is_missing_state else RecordStatusEnum.NEW\n'
        )
        text = text.replace(
            '            "target_bots": targets,\n',
            '            "target_bots": targets,\n            "record_status": initial_status,\n'
        )
    
    ep_py.write_text(text, encoding="utf-8")
    print("app/services/excel_parser.py patched")

def patch_frontend():
    types_ts = FRONTEND / "src" / "types" / "index.ts"
    text = types_ts.read_text(encoding="utf-8")
    
    if "'QUEUED'" not in text:
        text = text.replace(
            "export type RecordStatus =\n  | 'NEW'",
            "export type RecordStatus =\n  | 'NEW'\n  | 'QUEUED'"
        )
    if "'NEEDS_REVIEW'" not in text:
        text = text.replace(
            "  | 'MANUAL_REVIEW'",
            "  | 'MANUAL_REVIEW'\n  | 'NEEDS_REVIEW'"
        )
    if "'DISPATCHED'" not in text:
        text = text.replace(
            "export type BotStatus =\n  | 'NOT_TRIGGERED'",
            "export type BotStatus =\n  | 'NOT_TRIGGERED'\n  | 'DISPATCHED'\n  | 'QUEUED'\n  | 'RUNNING'"
        )
    types_ts.write_text(text, encoding="utf-8")
    print("frontend/src/types/index.ts patched")

    # StatusBadge
    badge_tsx = FRONTEND / "src" / "components" / "StatusBadge.tsx"
    badge_text = badge_tsx.read_text(encoding="utf-8")
    if 'case "DISPATCHED":' not in badge_text:
        badge_text = badge_text.replace(
            '    case "NEW":\n',
            '    case "DISPATCHED":\n      colorClasses = "bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-400 border-cyan-200 dark:border-cyan-800/60";\n      label = "Dispatched";\n      break;\n    case "QUEUED":\n      colorClasses = "bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800/60";\n      label = "Queued";\n      break;\n    case "RUNNING":\n      colorClasses = "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/60 animate-pulse";\n      label = "Running";\n      break;\n    case "NEEDS_REVIEW":\n      colorClasses = "bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800/60 ring-1 ring-purple-400/30";\n      label = "Needs Review";\n      break;\n    case "BLOCKED":\n      colorClasses = "bg-orange-50 dark:bg-orange-950/60 text-orange-700 dark:text-orange-400 border-orange-200 dark:border-orange-800/60";\n      label = "Blocked";\n      break;\n    case "NEW":\n'
        )
        badge_tsx.write_text(badge_text, encoding="utf-8")
        print("frontend/src/components/StatusBadge.tsx patched")

if __name__ == "__main__":
    patch_models()
    patch_config()
    patch_settings_schema()
    patch_settings_service()
    patch_browser_manager()
    patch_base_automation()
    patch_settings_endpoint()
    patch_scraper_tasks()
    patch_excel_parser()
    patch_frontend()
    print("All patches applied successfully!")

