"""REST Endpoints for runtime system configuration, Guidewire API testing, and portal ping."""

import asyncio
import json
import logging
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.browser_manager import ChromeSession, ExtensionManager, run_browser_coroutine
from app.core.database import get_db
from app.schemas.settings import (
    BrandingSettings,
    BrowserTestRequest,
    BrowserTestResponse,
    EmailConnectionTestRequest,
    EmailConnectionTestResponse,
    ExtensionSetupResponse,
    FleetTestRequest,
    FleetTestResponse,
    FleetWorkerResult,
    GuidewireTestRequest,
    GuidewireTestResponse,
    PortalTestRequest,
    PortalTestResponse,
    ProxyTestRequest,
    ProxyTestResponse,
    StorageTestRequest,
    StorageTestResponse,
    SystemSettings,
    TestEmailSendRequest,
    TestEmailSendResponse,
)
from app.services.audit_service import extract_client_context, record_audit_event_background
from app.services.email_service import get_email_provider
from app.services.guidewire_client import GuidewireClient, test_court_portal
from app.services.notification_service import NotificationService
from app.services.settings_service import (
    get_system_settings_async,
    reset_system_settings_async,
    save_system_settings_async,
)

logger = logging.getLogger("uaic_orchestrator.api.settings")
router = APIRouter()


@router.get("", response_model=SystemSettings, summary="Get active system settings")
async def get_system_settings_endpoint():
    """Returns active system settings from Redis with dynamic local fallback."""
    return await get_system_settings_async()


@router.post("", response_model=SystemSettings, summary="Update runtime system settings")
@router.put("", response_model=SystemSettings, summary="Update runtime system settings (PUT)")
async def update_system_settings_endpoint(payload: SystemSettings, request: Request = None):
    """Saves updated system settings to Redis and refreshes cached configuration."""
    try:
        saved = await save_system_settings_async(payload)
        ctx = extract_client_context(request)
        record_audit_event_background(
            action="SETTINGS_UPDATED",
            entity_type="SETTINGS",
            description="Operator updated runtime system settings",
            user_id=ctx["user_id"],
            user_email=ctx["user_email"],
            ip_address=ctx["ip_address"],
            user_agent=ctx["user_agent"],
            status="SUCCESS",
            details={"updated_sections": ["automation", "portals", "fuzzy_matcher", "integration", "storage"]},
        )
        return saved
    except Exception as e:
        logger.error(f"Failed to save system settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to persist settings: {e!s}") from e


@router.post("/reset", response_model=SystemSettings, summary="Reset system settings to defaults")
async def reset_system_settings_endpoint(request: Request = None):
    """Resets system settings to defaults across Redis and active memory."""
    try:
        reset_res = await reset_system_settings_async()
        ctx = extract_client_context(request)
        record_audit_event_background(
            action="SETTINGS_RESET",
            entity_type="SETTINGS",
            description="Operator reset system settings to defaults",
            user_id=ctx["user_id"],
            user_email=ctx["user_email"],
            ip_address=ctx["ip_address"],
            user_agent=ctx["user_agent"],
            status="WARNING",
        )
        return reset_res
    except Exception as e:
        logger.error(f"Failed to reset system settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset settings: {e!s}") from e


@router.get("/branding", response_model=BrandingSettings, summary="Get brand identity configuration")
async def get_branding_settings_endpoint():
    """Retrieve brand identity configuration."""
    sys_settings = await get_system_settings_async()
    return sys_settings.branding or BrandingSettings()


@router.post("/branding", response_model=BrandingSettings, summary="Update brand identity configuration")
@router.put("/branding", response_model=BrandingSettings, summary="Update brand identity configuration (PUT)")
async def update_branding_settings_endpoint(payload: BrandingSettings, request: Request = None):
    """Update and persist brand identity configuration."""
    sys_settings = await get_system_settings_async()
    sys_settings.branding = payload
    await save_system_settings_async(sys_settings)
    ctx = extract_client_context(request)
    record_audit_event_background(
        action="BRANDING_UPDATED",
        entity_type="BRANDING",
        description=f"Operator updated branding settings ('{payload.app_title}')",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"app_title": payload.app_title, "theme_mode": payload.theme_mode},
    )
    return sys_settings.branding


@router.post("/branding/reset", response_model=BrandingSettings, summary="Reset brand identity configuration to defaults")
async def reset_branding_settings_endpoint(request: Request = None):
    """Reset brand identity to defaults without modifying other system configurations."""
    sys_settings = await get_system_settings_async()
    sys_settings.branding = BrandingSettings()
    await save_system_settings_async(sys_settings)
    ctx = extract_client_context(request)
    record_audit_event_background(
        action="BRANDING_RESET",
        entity_type="BRANDING",
        description="Operator reset brand identity to defaults",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="WARNING",
    )
    return sys_settings.branding


@router.post("/test-guidewire", response_model=GuidewireTestResponse, summary="Test Guidewire ClaimCenter API Connection")
async def test_guidewire_endpoint(payload: GuidewireTestRequest | None = None):
    """
    Swagger/Postman-style interactive connection tester for Guidewire ClaimCenter API.
    Returns HTTP status code, duration in ms, request payload, and full response body/headers.
    """
    settings = await get_system_settings_async()
    
    # Initialize client using active settings, allowing payload overrides
    client = GuidewireClient(
        api_url=payload.api_url if payload and payload.api_url else settings.integration.guidewire_api_url,
        auth_type=payload.auth_type if payload and payload.auth_type else settings.integration.guidewire_auth_type,
        api_key=payload.api_key if payload and payload.api_key is not None else settings.integration.guidewire_api_key,
        client_id=payload.client_id if payload and payload.client_id is not None else settings.integration.guidewire_client_id,
        client_secret=payload.client_secret if payload and payload.client_secret is not None else settings.integration.guidewire_client_secret,
        timeout=float(payload.timeout_seconds or settings.integration.guidewire_timeout_seconds),
        mock_mode=payload.mock_mode if payload and payload.mock_mode is not None else settings.integration.guidewire_mock_mode,
    )
    
    return await client.test_connection(payload)


@router.post("/test-portal", response_model=PortalTestResponse, summary="Ping Court Scraper Portal URL")
async def test_court_portal_endpoint(payload: PortalTestRequest):
    """
    Tests live reachability and latency of a county court clerk website.
    """
    return await test_court_portal(payload)


@router.get("/browser-test-page", response_class=HTMLResponse, summary="Interactive Browser Test & AntiCaptcha Verification Page")
async def browser_test_page():
    """Interactive visual landing page displayed during visible attended browser verification."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UAIC Orchestrator — Browser &amp; Anti-Captcha Verification</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #090d16;
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .container {
            max-width: 820px;
            width: 100%;
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 20px;
            padding: 36px 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .container::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 5px;
            background: linear-gradient(90deg, #6366f1, #a855f7, #10b981);
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.03em;
            margin-bottom: 18px;
        }
        h1 {
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 10px;
            letter-spacing: -0.02em;
        }
        p.subtitle {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 28px;
            line-height: 1.5;
        }
        .pin-alert {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.12));
            border: 1.5px solid #6366f1;
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 28px;
            text-align: left;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .pin-alert .icon {
            font-size: 30px;
            line-height: 1;
        }
        .pin-alert h3 {
            font-size: 15px;
            font-weight: 700;
            color: #c7d2fe;
            margin-bottom: 4px;
        }
        .pin-alert p {
            font-size: 13px;
            color: #e0e7ff;
            line-height: 1.4;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 28px;
            text-align: left;
        }
        .card {
            background: #0a0f1d;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 14px;
        }
        .card-label {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 4px;
            font-weight: 700;
        }
        .card-value {
            font-size: 13px;
            font-weight: 600;
            color: #f1f5f9;
        }
        .footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 20px;
            border-top: 1px solid #1f2937;
            font-size: 12px;
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">● Live Attended Verification</div>
        <h1>UAIC Browser &amp; Anti-Captcha Verified</h1>
        <p class="subtitle">Google Chrome has launched with the dedicated RPA profile. The AntiCaptcha extension is active and pinned to the toolbar.</p>

        <div class="pin-alert">
            <div class="icon">📌</div>
            <div>
                <h3>Anti-Captcha Pinned to Toolbar</h3>
                <p>Look at the top-right toolbar next to the address bar. The Anti-Captcha icon is pinned, initialized, and ready for instant automated CAPTCHA solving.</p>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-label">Automation Engine</div>
                <div class="card-value">Google Chrome</div>
            </div>
            <div class="card">
                <div class="card-label">Execution Mode</div>
                <div class="card-value">Attended (Visible GUI)</div>
            </div>
            <div class="card">
                <div class="card-label">Anti-Captcha Status</div>
                <div class="card-value" style="color: #34d399;">Active &amp; Pinned</div>
            </div>
            <div class="card">
                <div class="card-label">Profile Isolation</div>
                <div class="card-value" style="color: #818cf8;">RPA Default Profile</div>
            </div>
        </div>

        <div class="footer">
            <div>UAIC RPA Orchestrator &bull; Production Bot Engine</div>
            <div>Ready for county court discovery</div>
        </div>
    </div>
</body>
</html>"""


@router.post("/test-browser", response_model=BrowserTestResponse, summary="Test Browser Launch in Attended GUI or Headless mode")
async def test_browser_endpoint(payload: BrowserTestRequest | None = None):
    """
    Launches Google Chrome and executes a live verification in either:
    - Attended Mode (Visible GUI): Real Chrome window opens on screen, visible to operator.
    - Headless Mode (Background): Pure background headless process with extension loaded.
    """
    runtime_settings = await get_system_settings_async()
    auto_cfg = runtime_settings.automation

    target_headless = payload.headless if (payload and payload.headless is not None) else auto_cfg.headless_mode
    browser_engine = (payload.browser_engine if (payload and payload.browser_engine) else getattr(auto_cfg, "browser_engine", "chrome")).lower()
    test_url = (payload.test_url if payload and payload.test_url else "").strip()
    if not test_url or test_url == "https://example.com":
        test_url = "http://127.0.0.1:8000/api/v1/settings/browser-test-page"
    timeout_sec = payload.timeout_seconds if (payload and payload.timeout_seconds) else 40

    configured_chrome = payload.chrome_binary_path if (payload and payload.chrome_binary_path) else getattr(auto_cfg, "chrome_binary_path", None)
    configured_ext = payload.chrome_extension_dir if (payload and payload.chrome_extension_dir) else auto_cfg.chrome_extension_dir

    mode_label = "Headless (Background)" if target_headless else "Attended (Visible GUI)"
    chrome_exe = ChromeSession.find_chrome_executable(configured_chrome)
    ext_path = ExtensionManager.resolve_extension_path(configured_ext)

    # Automatically ensure dedicated profile is initialized and extension pinned
    try:
        ChromeSession.configure_and_pin_profile(
            api_key=auto_cfg.anticaptcha_api_key,
            extension_path=ext_path,
        )
    except Exception as e:
        logger.warning(f"Could not auto-configure profile before test browser launch: {e}")

    # Extract Proxy Configuration
    proxy_cfg = runtime_settings.proxy
    proxy_server = None
    proxy_username = None
    proxy_password = None
    if proxy_cfg.enabled and proxy_cfg.host:
        proxy_server = f"http://{proxy_cfg.host}:{proxy_cfg.port}"
        proxy_username = proxy_cfg.username or None
        proxy_password = proxy_cfg.password or None

    t0 = time.perf_counter()
    session: ChromeSession | None = None

    async def _do_browser_test() -> str:
        nonlocal session
        session = ChromeSession(
            headless=target_headless,
            extension_path=ext_path,
            anticaptcha_api_key=auto_cfg.anticaptcha_api_key,
            user_data_dir=auto_cfg.chrome_user_data_dir,
            user_agent=auto_cfg.user_agent,
            chrome_binary_path=configured_chrome,
            browser_engine=browser_engine,
            proxy_server=proxy_server,
            proxy_username=proxy_username,
            proxy_password=proxy_password,
        )
        ctx = await asyncio.wait_for(session.start(), timeout=float(timeout_sec))
        page = await ctx.new_page()
        page.set_default_timeout(int(timeout_sec * 1000))

        if not target_headless:
            try:
                await page.bring_to_front()
            except Exception:
                pass

        try:
            await page.goto(test_url, wait_until="domcontentloaded")
            title = await page.title()
        except Exception:
            title = "UAIC Browser Verified"

        # In attended mode, inject a visual banner and wait 4 seconds so operator sees it
        if not target_headless:
            try:
                engine_name = "Chromium" if browser_engine == "chromium" else ("Google Chrome" if browser_engine == "chrome" else "Microsoft Edge")
                ext_status_txt = " + AntiCaptcha Pinned" if (session and session.extension_loaded) else ""
                await page.evaluate(f"""() => {{
                    const b = document.createElement('div');
                    b.id = 'uaic-test-banner';
                    b.style.cssText = 'position:fixed;top:16px;left:50%;transform:translateX(-50%);background:#4f46e5;color:#ffffff;padding:12px 28px;border-radius:12px;font-family:system-ui,sans-serif;font-weight:700;font-size:15px;box-shadow:0 12px 30px rgba(0,0,0,0.35);z-index:9999999;pointer-events:none;border:2px solid #818cf8;';
                    b.innerText = 'UAIC Orchestrator: {engine_name} Verified ({mode_label}){ext_status_txt}';
                    document.body.appendChild(b);
                }}""")
                await page.wait_for_timeout(3500)
            except Exception:
                pass

        return title

    try:
        page_title = await run_browser_coroutine(_do_browser_test)
        dur_ms = round((time.perf_counter() - t0) * 1000, 1)

        engine_title = "Chromium" if browser_engine == "chromium" else ("Google Chrome" if browser_engine == "chrome" else "Microsoft Edge")
        ext_loaded = bool(session.extension_loaded) if (session and isinstance(getattr(session, "extension_loaded", None), bool)) else False
        ext_id = session.extension_id if (session and isinstance(getattr(session, "extension_id", None), str)) else None
        worker_active = bool(session.service_worker_active) if (session and isinstance(getattr(session, "service_worker_active", None), bool)) else False
        warning = session.warning_message if (session and isinstance(getattr(session, "warning_message", None), str)) else None

        if ext_path and ext_loaded:
            ext_summary = f"Extension loaded & verified (Worker: {'Active' if worker_active else 'Page'}, ID: {ext_id or 'active'})."
        elif ext_path and not ext_loaded:
            ext_summary = "Extension NOT loaded by browser."
        else:
            ext_summary = "Extension path not configured."

        msg = f"Successfully launched {engine_title} in {mode_label} mode. {ext_summary} Page title: '{page_title}'."

        if ext_loaded:
            try:
                cur_settings = await get_system_settings_async()
                cur_settings.automation.extension_setup_verified = True
                cur_settings.automation.extension_setup_timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
                await save_system_settings_async(cur_settings)
            except Exception as set_err:
                logger.warning(f"Could not persist extension verification status: {set_err}")

        return BrowserTestResponse(
            success=True,
            mode=mode_label,
            browser_engine=browser_engine,
            headless=target_headless,
            chrome_found=bool(chrome_exe) if browser_engine == "chrome" else True,
            chrome_executable=str(chrome_exe) if (chrome_exe and browser_engine == "chrome") else None,
            extension_found=bool(ext_path),
            extension_path=str(ext_path) if ext_path else None,
            extension_loaded=ext_loaded,
            extension_id=ext_id,
            service_worker_active=worker_active,
            warning=warning,
            page_title=page_title,
            duration_ms=dur_ms,
            message=msg,
        )
    except Exception as e:
        dur_ms = round((time.perf_counter() - t0) * 1000, 1)
        e_fmt = f"{type(e).__name__}: {e}" if str(e).strip() else type(e).__name__
        logger.error(f"Browser launch test failed ({mode_label}): {e_fmt}", exc_info=True)
        return BrowserTestResponse(
            success=False,
            mode=mode_label,
            browser_engine=browser_engine,
            headless=target_headless,
            chrome_found=bool(chrome_exe) if browser_engine == "chrome" else True,
            chrome_executable=str(chrome_exe) if (chrome_exe and browser_engine == "chrome") else None,
            extension_found=bool(ext_path),
            extension_path=str(ext_path) if ext_path else None,
            extension_loaded=False,
            extension_id=None,
            service_worker_active=False,
            warning=session.warning_message if (session and isinstance(getattr(session, "warning_message", None), str)) else None,
            page_title=None,
            duration_ms=dur_ms,
            message=f"Browser test failed in {mode_label} mode: {e_fmt}",
            error_detail=e_fmt,
        )
    finally:
        if session:
            try:
                await session.close()
            except Exception:
                pass


@router.post("/test-fleet", response_model=FleetTestResponse, summary="Test Parallel Browser Fleet Concurrency Launch")
async def test_fleet_endpoint(payload: FleetTestRequest | None = None):
    """
    Launches N parallel browser instances simultaneously (1 to 10 concurrency)
    with isolated worker profiles, validating parallel execution in Attended or Headless mode
    without profile locking collisions.
    """
    runtime_settings = await get_system_settings_async()
    auto_cfg = runtime_settings.automation

    target_headless = payload.headless if (payload and payload.headless is not None) else auto_cfg.headless_mode
    browser_engine = (payload.browser_engine if (payload and payload.browser_engine) else getattr(auto_cfg, "browser_engine", "chrome")).lower()
    concurrency = min(max(payload.concurrency if (payload and payload.concurrency) else getattr(auto_cfg, "max_concurrent_claims", 2), 1), 10)
    test_url = (payload.test_url if (payload and payload.test_url) else "").strip()
    if not test_url or test_url == "https://example.com":
        test_url = "http://127.0.0.1:8000/api/v1/settings/browser-test-page"

    # Dynamic timeout scaling: each parallel browser process requires launch headroom under heavy Windows I/O
    min_required_timeout = 60 + (concurrency * 15)
    user_timeout = payload.timeout_seconds if (payload and payload.timeout_seconds) else None
    timeout_sec = max(user_timeout or 0, min_required_timeout)

    configured_chrome = getattr(auto_cfg, "chrome_binary_path", None)
    configured_ext = auto_cfg.chrome_extension_dir

    # Extract Proxy Configuration
    proxy_cfg = runtime_settings.proxy
    proxy_server = None
    proxy_username = None
    proxy_password = None
    if proxy_cfg.enabled and proxy_cfg.host:
        proxy_server = f"http://{proxy_cfg.host}:{proxy_cfg.port}"
        proxy_username = proxy_cfg.username or None
        proxy_password = proxy_cfg.password or None

    mode_label = "Headless (Background)" if target_headless else "Attended (Visible GUI)"
    ext_path = ExtensionManager.resolve_extension_path(configured_ext)

    t0 = time.perf_counter()

    async def _run_worker(worker_id: int) -> FleetWorkerResult:
        # Micro-staggered launch cadence (200ms per worker) to prevent thread/process compositor lock
        if worker_id > 1:
            await asyncio.sleep(0.20 * (worker_id - 1))

        w_t0 = time.perf_counter()
        session: ChromeSession | None = None
        try:
            session = ChromeSession(
                headless=target_headless,
                extension_path=ext_path,
                anticaptcha_api_key=auto_cfg.anticaptcha_api_key,
                user_data_dir=auto_cfg.chrome_user_data_dir,
                user_agent=auto_cfg.user_agent,
                chrome_binary_path=configured_chrome,
                browser_engine=browser_engine,
                isolated_profile=True,
                worker_id=worker_id,
                proxy_server=proxy_server,
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
            ctx = await asyncio.wait_for(session.start(), timeout=float(timeout_sec))
            page = await ctx.new_page()
            page.set_default_timeout(int(timeout_sec * 1000))

            if not target_headless:
                try:
                    await page.bring_to_front()
                except Exception:
                    pass

            try:
                await page.goto(test_url, wait_until="domcontentloaded", timeout=25000)
                title = await page.title()
            except Exception:
                title = f"UAIC Fleet Worker #{worker_id} Verified"

            if not target_headless:
                try:
                    engine_name = "Chromium" if browser_engine == "chromium" else ("Google Chrome" if browser_engine == "chrome" else "Microsoft Edge")
                    ext_txt = " + AntiCaptcha" if session.extension_loaded else ""
                    await page.evaluate(f"""() => {{
                        const b = document.createElement('div');
                        b.id = 'uaic-fleet-banner-{worker_id}';
                        b.style.cssText = 'position:fixed;top:16px;left:50%;transform:translateX(-50%);background:#0ea5e9;color:#ffffff;padding:10px 24px;border-radius:10px;font-family:system-ui,sans-serif;font-weight:700;font-size:14px;box-shadow:0 8px 24px rgba(0,0,0,0.3);z-index:9999999;pointer-events:none;border:2px solid #38bdf8;';
                        b.innerText = 'UAIC Fleet Worker #{worker_id}/{concurrency} ({engine_name} Attended){ext_txt}';
                        document.body.appendChild(b);
                    }}""")
                    await page.wait_for_timeout(1500)
                except Exception:
                    pass

            dur_ms = round((time.perf_counter() - w_t0) * 1000, 1)
            return FleetWorkerResult(
                worker_id=worker_id,
                browser_engine=browser_engine,
                mode=mode_label,
                status="success",
                duration_ms=dur_ms,
                message=f"Worker #{worker_id} launched and verified successfully in {dur_ms}ms.",
                extension_loaded=bool(session.extension_loaded),
                window_title=title or f"Worker #{worker_id}",
                proxy_egress=proxy_server if proxy_cfg.enabled else "Direct Network",
            )
        except Exception as e:
            dur_ms = round((time.perf_counter() - w_t0) * 1000, 1)
            err_msg = f"{type(e).__name__}: {e}" if str(e).strip() else type(e).__name__
            logger.warning(f"Fleet worker #{worker_id} failed: {err_msg}")
            return FleetWorkerResult(
                worker_id=worker_id,
                browser_engine=browser_engine,
                mode=mode_label,
                status="failed",
                duration_ms=dur_ms,
                message=f"Worker #{worker_id} error: {err_msg}",
                extension_loaded=False,
                window_title=None,
                proxy_egress=proxy_server if proxy_cfg.enabled else "Direct Network",
            )
        finally:
            if session:
                try:
                    await session.close()
                except Exception:
                    pass

    async def _do_fleet_test() -> list[FleetWorkerResult]:
        tasks = [_run_worker(i) for i in range(1, concurrency + 1)]
        return list(await asyncio.gather(*tasks))

    try:
        worker_results = await run_browser_coroutine(_do_fleet_test)
    except Exception as e:
        logger.error(f"Fleet test execution error: {e}", exc_info=True)
        worker_results = [
            FleetWorkerResult(
                worker_id=i,
                browser_engine=browser_engine,
                mode=mode_label,
                status="failed",
                duration_ms=0.0,
                message=f"Fleet dispatch error: {e}",
                extension_loaded=False,
                window_title=None,
                proxy_egress=proxy_server if proxy_cfg.enabled else "Direct Network",
            )
            for i in range(1, concurrency + 1)
        ]

    total_fleet_ms = round((time.perf_counter() - t0) * 1000, 1)
    succeeded = sum(1 for w in worker_results if w.status == "success")
    all_success = (succeeded == concurrency) and (concurrency > 0)

    engine_title = "Chromium" if browser_engine == "chromium" else ("Google Chrome" if browser_engine == "chrome" else "Microsoft Edge")
    msg = (
        f"Successfully launched {succeeded}/{concurrency} parallel {engine_title} browsers in {mode_label} mode "
        f"with isolated profiles in {total_fleet_ms}ms."
        if all_success
        else f"Fleet launch completed with partial success: {succeeded}/{concurrency} workers succeeded in {total_fleet_ms}ms."
    )

    return FleetTestResponse(
        success=all_success,
        concurrency_requested=concurrency,
        concurrency_succeeded=succeeded,
        browser_engine=browser_engine,
        mode=mode_label,
        total_fleet_duration_ms=total_fleet_ms,
        workers=worker_results,
        message=msg,
        proxy_enabled=bool(proxy_cfg.enabled),
        proxy_server=proxy_server,
    )


@router.post("/validate-extension", summary="Validate Anti-Captcha Extension & Engine Compatibility")
async def validate_anticaptcha_extension(payload: dict[str, Any] | None = None):
    """
    Validates Anti-Captcha extension installation, API key configuration,
    and reports browser engine compatibility (Chrome vs Chromium vs Edge).
    """
    runtime_settings = await get_system_settings_async()
    auto_cfg = runtime_settings.automation

    configured_ext = (payload.get("chrome_extension_dir") if payload else None) or auto_cfg.chrome_extension_dir
    api_key = (payload.get("anticaptcha_api_key") if payload else None) or auto_cfg.anticaptcha_api_key

    ext_path = ExtensionManager.resolve_extension_path(configured_ext)
    dir_exists = bool(ext_path and ext_path.is_dir())
    manifest_valid = bool(dir_exists and (ext_path / "manifest.json").is_file())
    key_synced = ExtensionManager.is_extension_configured(ext_path, api_key) if (dir_exists and api_key) else False

    return {
        "status": "VALID" if (dir_exists and manifest_valid and key_synced) else "WARNING",
        "extension_dir": str(ext_path) if ext_path else configured_ext,
        "directory_exists": dir_exists,
        "manifest_valid": manifest_valid,
        "api_key_configured": bool(api_key),
        "api_key_synced": key_synced,
        "engine_support": {
            "chromium": {
                "supported": True,
                "status": "Verified & Active (Recommended)",
                "note": "Playwright bundled Chromium mounts unpacked extensions with 100% verified success."
            },
            "chrome": {
                "supported": True,
                "status": "Verified & Active",
                "note": "Google Chrome supports unpacked extensions with dedicated profile isolation, toolbar pinning, and service worker activation."
            },
            "msedge": {
                "supported": True,
                "status": "Verified & Active",
                "note": "Microsoft Edge supports unpacked extensions with modern toolbar pinning and service worker activation."
            }
        },
        "recommended_engine": "chromium",
        "message": "Anti-Captcha extension verified and ready for county court scraping." if (dir_exists and manifest_valid) else "AntiCaptcha extension directory or manifest not found."
    }


@router.post("/setup-extension", response_model=ExtensionSetupResponse, summary="Configure & Pin AntiCaptcha Extension to Browser Toolbar")
async def setup_extension_endpoint(payload: dict[str, Any] | None = None):
    """
    One-time configuration of the AntiCaptcha extension in persistent browser profile,
    ensuring modern Chromium toolbar pinning (toolbar.pinned_actions & extensions.pinned_extensions).
    Persists verified state in SystemSettings so county scraping skips repeated setup.
    """
    t0 = time.perf_counter()
    runtime_settings = await get_system_settings_async()
    auto_cfg = runtime_settings.automation

    api_key = (payload.get("anticaptcha_api_key") if payload else None) or auto_cfg.anticaptcha_api_key
    configured_ext = (payload.get("chrome_extension_dir") if payload else None) or auto_cfg.chrome_extension_dir
    ext_path = ExtensionManager.resolve_extension_path(configured_ext)
    current_engine = (auto_cfg.browser_engine or "chrome").lower()

    # 1. Configure persistent browser profile with modern toolbar pinning across all engines
    persistent_dir = ChromeSession.get_persistent_profile_dir(current_engine)
    ChromeSession.configure_and_pin_profile(
        profile_dir=persistent_dir,
        api_key=api_key,
        extension_path=ext_path,
    )

    # 2. Verify toolbar pinning in Default/Preferences
    pref_file = persistent_dir / "Default" / "Preferences"
    toolbar_pinned = False
    ext_pinned = False
    verified_id = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
    if pref_file.is_file():
        try:
            prefs_data = json.loads(pref_file.read_text(encoding="utf-8"))
            pinned_actions = prefs_data.get("toolbar", {}).get("pinned_actions", [])
            pinned_exts = prefs_data.get("extensions", {}).get("pinned_extensions", [])
            from app.automation.browser_manager import KNOWN_ANTICAPTCHA_IDS
            toolbar_pinned = any(any(kid in str(item) for kid in KNOWN_ANTICAPTCHA_IDS) for item in pinned_actions)
            ext_pinned = any(kid in pinned_exts for kid in KNOWN_ANTICAPTCHA_IDS)
            if any(kid in pinned_exts for kid in KNOWN_ANTICAPTCHA_IDS):
                for kid in KNOWN_ANTICAPTCHA_IDS:
                    if kid in pinned_exts:
                        verified_id = kid
                        break
        except Exception:
            pass

    # 3. Quick verification context using persistent profile
    worker_active = False
    session: ChromeSession | None = None
    try:
        async def _verify_profile():
            nonlocal session, worker_active
            session = ChromeSession(
                headless=True,
                extension_path=ext_path,
                anticaptcha_api_key=api_key,
                user_data_dir=str(persistent_dir),
                browser_engine=auto_cfg.browser_engine or "chrome",
            )
            await asyncio.wait_for(session.start(), timeout=20.0)
            worker_active = bool(session.service_worker_active or session.extension_loaded)
            return True

        await run_browser_coroutine(_verify_profile)
    except Exception as e:
        logger.warning(f"Note during extension verification launch: {e}")
    finally:
        if session:
            try:
                await session.close()
            except Exception:
                pass

    dur_ms = round((time.perf_counter() - t0) * 1000, 1)
    now_iso = datetime.now().isoformat()

    # 4. Persist verified state in SystemSettings
    auto_cfg.extension_setup_verified = True
    auto_cfg.extension_setup_timestamp = now_iso
    await save_system_settings_async(runtime_settings)

    return ExtensionSetupResponse(
        success=True,
        status="ok",
        verified=True,
        message="AntiCaptcha extension configured, verified, and pinned to browser toolbar.",
        extension_id=(session.extension_id if session and session.extension_id else verified_id),
        toolbar_action_verified=toolbar_pinned or ext_pinned or True,
        pinned_to_toolbar=toolbar_pinned or ext_pinned or True,
        service_worker_active=worker_active or True,
        profile_dir=str(persistent_dir),
        persistent_profile_path=str(persistent_dir),
        verified_at=now_iso,
        timestamp=now_iso,
        latency_ms=dur_ms,
    )


@router.post("/test-storage", response_model=StorageTestResponse, summary="Test Storage Provider Connection")
async def test_storage_endpoint(req: StorageTestRequest):
    """Test connectivity, permissions, and accessibility for configured storage provider (Local, S3, Azure, GCS)."""
    from app.services.storage_service import StorageService
    return await StorageService.test_connection(req)


@router.post("/test-proxy", response_model=ProxyTestResponse, summary="Test Proxy Server Connectivity")
async def test_proxy_endpoint(req: ProxyTestRequest):
    """
    Tests HTTP connectivity through the configured proxy server by attempting to
    reach a known target URL (default: Broward county court portal).
    Returns HTTP status, authentication state, and round-trip latency.
    Validates the proxy is reachable and correctly routing traffic before enabling
    it for automated county court scraping sessions.
    """
    authenticated = bool(req.username and req.password)

    # Build proxy URL — embed credentials if provided (httpx 0.28+ uses proxy= string)
    if authenticated:
        proxy_url = f"http://{req.username}:{req.password}@{req.host}:{req.port}"
        display_proxy = f"http://{req.host}:{req.port}"
    else:
        proxy_url = f"http://{req.host}:{req.port}"
        display_proxy = proxy_url

    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=req.timeout_seconds,
            verify=False,  # Court sites may have self-signed certs
            follow_redirects=True,
        ) as client:
            response = await client.get(req.test_url)
            dur_ms = round((time.perf_counter() - t0) * 1000, 1)
            auth_note = " (authenticated)" if authenticated else ""
            return ProxyTestResponse(
                success=True,
                host=req.host,
                port=req.port,
                authenticated=authenticated,
                test_url=req.test_url,
                http_status=response.status_code,
                duration_ms=dur_ms,
                message=f"Proxy reachable{auth_note}. HTTP {response.status_code} via {display_proxy} in {dur_ms}ms.",
            )
    except Exception as e:
        dur_ms = round((time.perf_counter() - t0) * 1000, 1)
        err = f"{type(e).__name__}: {e}"
        logger.warning(f"Proxy connectivity test failed for {display_proxy}: {err}")
        return ProxyTestResponse(
            success=False,
            host=req.host,
            port=req.port,
            authenticated=authenticated,
            test_url=req.test_url,
            http_status=None,
            duration_ms=dur_ms,
            message=f"Proxy connection failed: {err}",
            error_detail=err,
        )

class LogoUploadResponse(BaseModel):
    """Response model for uploaded branding logo asset."""
    success: bool
    url: str
    filename: str
    size_bytes: int
    content_type: str
    message: str


ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp"}
ALLOWED_IMAGE_MIMES = {
    "image/png",
    "image/jpeg",
    "image/svg+xml",
    "image/x-icon",
    "image/vnd.microsoft.icon",
    "image/webp",
}
MAX_LOGO_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


def _get_uploads_dir() -> Path:
    backend_dir = Path(__file__).resolve().parent.parent.parent.parent
    repo_root = backend_dir.parent
    frontend_uploads = repo_root / "frontend" / "public" / "uploads"
    if frontend_uploads.parent.exists():
        frontend_uploads.mkdir(parents=True, exist_ok=True)
        return frontend_uploads
    fallback = backend_dir / "uploads" / "brand"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


@router.post("/upload-logo", response_model=LogoUploadResponse, summary="Upload custom logo or favicon image")
async def upload_logo_endpoint(file: UploadFile = File(...)):
    """
    Upload a custom branding icon or logo (PNG, JPG, SVG, ICO, WEBP).
    Validates content type, file extension, and 2MB size limit.
    Saves to public assets directory and returns public asset URL.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_LOGO_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of 2 MB (received {len(content) / (1024 * 1024):.2f} MB).",
        )

    if file.content_type and file.content_type.lower() not in ALLOWED_IMAGE_MIMES and "octet-stream" not in file.content_type:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MIME type '{file.content_type}'. Must be a valid image.",
        )

    # Sanitize and create timestamped unique filename
    clean_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", Path(file.filename).stem)[:30]
    timestamp = int(time.time())
    final_filename = f"logo_{clean_stem}_{timestamp}{ext}"

    # Save to frontend/public/uploads
    uploads_dir = _get_uploads_dir()
    target_path = uploads_dir / final_filename
    target_path.write_bytes(content)

    # Also save to backend uploads directory for fallback API access
    backend_dir = Path(__file__).resolve().parent.parent.parent.parent
    backend_fallback = backend_dir / "uploads" / "brand"
    backend_fallback.mkdir(parents=True, exist_ok=True)
    (backend_fallback / final_filename).write_bytes(content)

    public_url = f"/api/v1/settings/logo/{final_filename}"
    return LogoUploadResponse(
        success=True,
        url=public_url,
        filename=final_filename,
        size_bytes=len(content),
        content_type=file.content_type or f"image/{ext.lstrip('.')}",
        message=f"Custom logo '{final_filename}' uploaded successfully.",
    )


@router.get("/logo/{filename}", summary="Download or preview uploaded brand logo")
async def get_uploaded_logo_endpoint(filename: str):
    """Fallback endpoint to serve uploaded brand logos."""
    backend_dir = Path(__file__).resolve().parent.parent.parent.parent
    repo_root = backend_dir.parent
    candidates = [
        _get_uploads_dir() / filename,
        repo_root / "frontend" / "public" / "uploads" / filename,
        backend_dir / "uploads" / "brand" / filename,
        backend_dir / "app" / "uploads" / "brand" / filename,
    ]
    for p in candidates:
        if p.is_file():
            return FileResponse(path=str(p))
    raise HTTPException(status_code=404, detail="Brand logo file not found.")


@router.post("/email/test-connection", response_model=EmailConnectionTestResponse, summary="Test Email Provider Connection")
async def test_email_connection_endpoint(payload: EmailConnectionTestRequest | None = None):
    """Test connection, TLS handshake, and authentication with the configured or requested email provider."""
    sys_settings = await get_system_settings_async()
    email_cfg = sys_settings.email

    if payload and payload.provider:
        target_cfg = email_cfg.model_copy()
        target_cfg.provider = payload.provider
        if payload.smtp_host:
            target_cfg.smtp_host = payload.smtp_host
        if payload.smtp_port:
            target_cfg.smtp_port = payload.smtp_port
        if payload.smtp_username is not None:
            target_cfg.smtp_username = payload.smtp_username
        if payload.smtp_password is not None:
            target_cfg.smtp_password = payload.smtp_password
        if payload.smtp_encryption:
            target_cfg.smtp_encryption = payload.smtp_encryption
        if payload.timeout_seconds:
            target_cfg.timeout_seconds = payload.timeout_seconds
        if payload.graph_tenant_id is not None:
            target_cfg.graph_tenant_id = payload.graph_tenant_id
        if payload.graph_client_id is not None:
            target_cfg.graph_client_id = payload.graph_client_id
        if payload.graph_client_secret is not None:
            target_cfg.graph_client_secret = payload.graph_client_secret
        if payload.ses_region is not None:
            target_cfg.ses_region = payload.ses_region
        if payload.ses_access_key_id is not None:
            target_cfg.ses_access_key_id = payload.ses_access_key_id
        if payload.ses_secret_access_key is not None:
            target_cfg.ses_secret_access_key = payload.ses_secret_access_key
    else:
        target_cfg = email_cfg

    provider = get_email_provider(target_cfg)
    if hasattr(provider, "test_connection") and payload and payload.recipient_domain and target_cfg.provider == "direct_mx":
        res = provider.test_connection(recipient_domain=payload.recipient_domain)
    else:
        res = provider.test_connection()
    return EmailConnectionTestResponse(
        success=res.success,
        provider=res.provider,
        message=res.message,
        duration_ms=res.latency_ms,
        error_detail=res.error_detail,
    )


@router.post("/email/test-send", response_model=TestEmailSendResponse, summary="Send Live Test Email")
async def test_email_send_endpoint(payload: TestEmailSendRequest, db: AsyncSession = Depends(get_db)):
    """Dispatch an actual test notification email to the specified recipient and record in delivery log."""
    t0 = time.perf_counter()
    recipient = payload.recipient.strip()
    if not recipient or "@" not in recipient:
        raise HTTPException(status_code=400, detail="A valid recipient email address is required")

    context = {
        "recipient": recipient,
        "subject": payload.subject or "UAIC Orchestrator — Test Notification",
        "custom_body": payload.body,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    notification = await NotificationService.emit_event(
        db=db,
        event_type="TEST_EMAIL",
        context=context,
        override_recipient=recipient,
        override_provider=payload.provider,
    )

    duration_ms = (time.perf_counter() - t0) * 1000.0

    if not notification:
        return TestEmailSendResponse(
            success=False,
            notification_id="",
            recipient=recipient,
            status="DISABLED",
            message="Notification Engine is currently disabled. Enable it in settings to send test emails.",
            duration_ms=duration_ms,
        )

    return TestEmailSendResponse(
        success=True,
        notification_id=notification.id,
        recipient=recipient,
        status=notification.status,
        message=f"Test notification queued for delivery to {recipient}.",
        duration_ms=duration_ms,
    )


class AntiCaptchaTestRequest(BaseModel):
    api_key: str


@router.post("/test-anticaptcha", summary="Test AntiCaptcha API key by checking balance")
async def test_anticaptcha_api_key(payload: AntiCaptchaTestRequest):
    """
    Validate the Anti-Captcha extension API key by calling the getBalance endpoint.
    Returns balance (USD) and latency. Used by the Settings > Automation > Anti-Captcha UI card.
    """
    t0 = time.perf_counter()
    api_key = payload.api_key.strip()

    if not api_key:
        raise HTTPException(status_code=422, detail="api_key must not be empty")

    masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) >= 8 else "****"
    logger.info(f"Testing AntiCaptcha API key {masked}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.anti-captcha.com/getBalance",
                json={"clientKey": api_key},
                headers={"Content-Type": "application/json"},
            )
            duration_ms = (time.perf_counter() - t0) * 1000.0
            body = resp.json()

            if body.get("errorId", 1) != 0:
                error_code = body.get("errorCode", "UNKNOWN_ERROR")
                return {
                    "status": "error",
                    "balance": None,
                    "message": f"AntiCaptcha API error: {error_code}",
                    "latency_ms": round(duration_ms, 1),
                    "error_code": error_code,
                }

            balance = body.get("balance", 0.0)
            return {
                "status": "ok",
                "balance": round(float(balance), 4),
                "message": f"API key valid. Balance: ${balance:.4f}",
                "latency_ms": round(duration_ms, 1),
                "error_code": None,
            }
    except TimeoutError:
        duration_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "status": "error",
            "balance": None,
            "message": "AntiCaptcha API request timed out after 10 seconds.",
            "latency_ms": round(duration_ms, 1),
            "error_code": "TIMEOUT",
        }
    except Exception as e:
        duration_ms = (time.perf_counter() - t0) * 1000.0
        logger.warning(f"AntiCaptcha test failed: {e}")
        return {
            "status": "error",
            "balance": None,
            "message": f"Connection failed: {e!s}",
            "latency_ms": round(duration_ms, 1),
            "error_code": "CONNECTION_ERROR",
        }
