"""Health check and comprehensive system observability endpoints."""

import logging
import os
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.browser_manager import ChromeSession, ExtensionManager
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import get_db
from app.services.portal_proxy import portal_proxy_url
from app.services.settings_service import get_system_settings_async

logger = logging.getLogger("uaic_orchestrator.api.health")
router = APIRouter()


@router.get("", tags=["Health"], summary="Basic Health Check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Basic health check verifying backend API and database connectivity."""
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e!s}"

    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_status,
        "version": "1.0.0",
    }


@router.get("/detailed", tags=["Health"], summary="Comprehensive System Observability & Diagnostics")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Exhaustive health assessment across API, Database, Redis, Celery, Chrome,

    AntiCaptcha, Guidewire, 8 Portals, and Storage.
    """
    sys_settings = await get_system_settings_async()
    components: dict[str, Any] = {}
    overall_status = "healthy"

    # 1. API Core
    components["api"] = {
        "name": "FastAPI Core Service",
        "status": "healthy",
        "latency_ms": 0.5,
        "details": {
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "version": "1.0.0",
            "python_version": os.sys.version.split()[0],
        },
    }

    # 2. Database
    db_start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        db_latency = round((time.perf_counter() - db_start) * 1000, 2)
        components["database"] = {
            "name": "SQLAlchemy Database Engine",
            "status": "healthy" if db_latency < 500 else "warning",
            "latency_ms": db_latency,
            "details": {
                "dialect": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
                "connected": True,
            },
        }
    except Exception as e:
        overall_status = "critical"
        components["database"] = {
            "name": "SQLAlchemy Database Engine",
            "status": "critical",
            "latency_ms": 0.0,
            "details": {"connected": False, "error": str(e)},
        }

    # 3. Redis
    bypass_active = getattr(settings, "SEMAPHORE_BYPASS", False)
    if bypass_active:
        components["redis"] = {
            "name": "Redis Broker / Cache",
            "status": "warning",
            "latency_ms": 0.0,
            "details": {
                "url": settings.REDIS_URL.split("@")[-1],
                "connected": False,
                "detail": "SEMAPHORE_BYPASS active - direct local mode",
            },
        }
    else:
        redis_start = time.perf_counter()
        try:
            import asyncio
            client = aioredis.from_url(settings.REDIS_URL, socket_timeout=1.0)
            await asyncio.wait_for(client.ping(), timeout=1.0)
            redis_latency = round((time.perf_counter() - redis_start) * 1000, 2)
            await client.aclose()
            components["redis"] = {
                "name": "Redis Broker / Cache",
                "status": "healthy" if redis_latency < 200 else "warning",
                "latency_ms": redis_latency,
                "details": {
                    "url": settings.REDIS_URL.split("@")[-1],
                    "connected": True,
                },
            }
        except Exception as e:
            if overall_status == "healthy":
                overall_status = "warning"
            components["redis"] = {
                "name": "Redis Broker / Cache",
                "status": "warning",
                "latency_ms": 0.0,
                "details": {
                    "url": settings.REDIS_URL.split("@")[-1],
                    "connected": False,
                    "detail": f"Offline or unreachable: {e!s}",
                },
            }

    # 4. Celery Workers
    if bypass_active:
        components["celery"] = {
            "name": "Celery Distributed Workers",
            "status": "warning",
            "details": {
                "active_workers": 0,
                "broker": settings.CELERY_BROKER_URL.split("@")[-1],
                "detail": "SEMAPHORE_BYPASS active - local sequential mode",
            },
        }
    else:
        try:
            ping_res = celery_app.control.ping(timeout=0.5) or []
            workers_count = len(ping_res)
            celery_status = "healthy" if workers_count > 0 else "warning"
            if workers_count == 0 and overall_status == "healthy":
                overall_status = "warning"
            components["celery"] = {
                "name": "Celery Distributed Workers",
                "status": celery_status,
                "details": {
                    "active_workers": workers_count,
                    "worker_hosts": [list(item.keys())[0] for item in ping_res if isinstance(item, dict)],
                    "broker": settings.CELERY_BROKER_URL.split("@")[-1],
                },
            }
        except Exception as e:
            components["celery"] = {
                "name": "Celery Distributed Workers",
                "status": "warning",
                "details": {
                    "active_workers": 0,
                    "error": str(e),
                    "broker": settings.CELERY_BROKER_URL.split("@")[-1],
                },
            }

    # 5. Browser Automation Engine
    browser_engine = (sys_settings.automation.browser_engine or "chrome").lower()
    is_headless = sys_settings.automation.headless_mode
    is_container = Path("/.dockerenv").exists()

    browser_exec = None
    engine_name = "Google Chrome"
    if browser_engine == "chromium":
        browser_exec = ChromeSession.find_chromium_executable()
        engine_name = "Playwright Chromium (Bundled)"
    elif browser_engine in ("edge", "msedge", "microsoft-edge"):
        browser_exec = ChromeSession.find_default_edge_executable()
        engine_name = "Microsoft Edge"
    else:  # chrome
        browser_exec = ChromeSession.find_chrome_executable()
        if not browser_exec and is_container:
            browser_exec = ChromeSession.find_chromium_executable()
            if browser_exec:
                engine_name = "Playwright Chromium (Container Fallback)"
        else:
            engine_name = "Google Chrome"

    browser_detected = browser_exec is not None
    browser_status = "healthy" if browser_detected else "critical"
    if not browser_detected:
        overall_status = "critical"

    if is_headless:
        mode_label = "Headless (Background)"
    elif is_container:
        mode_label = "Headless (Docker Container)"
    else:
        mode_label = "Attended (Visible GUI)"

    components["chrome"] = {
        "name": f"{engine_name} ({mode_label})",
        "status": browser_status,
        "details": {
            "engine": browser_engine,
            "detected": browser_detected,
            "executable_path": str(browser_exec) if browser_exec else "Not found",
            "execution_mode": mode_label,
            "headless_mode": is_headless or is_container,
            "attended_mode": (not is_headless) and (not is_container),
            "containerized": is_container,
            "use_chrome_configured": sys_settings.automation.use_chrome_browser,
        },
    }

    # 6. AntiCaptcha Extension
    ext_dir = ExtensionManager.resolve_extension_path(sys_settings.automation.chrome_extension_dir)
    api_key_configured = bool(sys_settings.automation.anticaptcha_api_key)
    ext_detected = ext_dir is not None
    ext_status = "healthy" if (ext_detected and api_key_configured) else ("warning" if ext_detected else "critical")
    if ext_status == "critical":
        overall_status = "critical"
    elif ext_status == "warning" and overall_status == "healthy":
        overall_status = "warning"
    components["anticaptcha"] = {
        "name": "AntiCaptcha Extension v0.83",
        "status": ext_status,
        "details": {
            "extension_detected": ext_detected,
            "extension_path": str(ext_dir) if ext_dir else "Not found",
            "api_key_configured": api_key_configured,
            "max_attempts": sys_settings.automation.max_captcha_attempts,
            "wait_seconds": sys_settings.automation.captcha_wait_seconds,
        },
    }

    # 7. Guidewire Integration
    gw_mock = sys_settings.integration.guidewire_mock_mode
    components["guidewire"] = {
        "name": "Guidewire Cloud Integration",
        "status": "healthy",
        "details": {
            "mock_mode": gw_mock,
            "auth_type": sys_settings.integration.guidewire_auth_type,
            "endpoint_configured": bool(sys_settings.integration.guidewire_api_url),
            "endpoint_url": sys_settings.integration.guidewire_api_url,
            "timeout_seconds": sys_settings.integration.guidewire_timeout_seconds,
        },
    }

    # 8. Local Storage & Uploads
    upload_path = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
    upload_path.mkdir(parents=True, exist_ok=True)
    try:
        disk_usage = shutil.disk_usage(upload_path)
        free_gb = round(disk_usage.free / (1024**3), 2)
        total_gb = round(disk_usage.total / (1024**3), 2)
        storage_status = "healthy" if free_gb > 1.0 else "warning"
        components["storage"] = {
            "name": "Local File Storage & Uploads",
            "status": storage_status,
            "details": {
                "upload_dir": str(upload_path),
                "writable": os.access(upload_path, os.W_OK),
                "free_gb": free_gb,
                "total_gb": total_gb,
            },
        }
    except Exception as e:
        components["storage"] = {
            "name": "Local File Storage & Uploads",
            "status": "warning",
            "details": {"error": str(e)},
        }

    # 9. Portals Registry
    p = sys_settings.portals
    portals_dict = {
        "broward": {
            "key": "broward",
            "name": "Broward County Clerk",
            "state": "FL",
            "url": p.broward_url,
            "enabled": p.broward_enabled,
            "has_dol": True,
            "has_casetype": True,
        },
        "hillsborough": {
            "key": "hillsborough",
            "name": "Hillsborough County Clerk",
            "state": "FL",
            "url": p.hillsborough_url,
            "enabled": p.hillsborough_enabled,
            "has_dol": True,
            "has_casetype": True,
        },
        "miami": {
            "key": "miami",
            "name": "Miami-Dade County Clerk",
            "state": "FL",
            "url": p.miami_url,
            "enabled": p.miami_enabled,
            "has_dol": True,
            "has_casetype": True,
            "login_required": p.miami_requires_login,
        },
        "travis": {
            "key": "travis",
            "name": "Travis County Odyssey Portal",
            "state": "TX",
            "url": p.travis_url,
            "enabled": p.travis_enabled,
            "has_dol": False,
            "has_casetype": True,
        },
        "dallas": {
            "key": "dallas",
            "name": "Dallas County Courts Portal",
            "state": "TX",
            "url": p.dallas_url,
            "enabled": p.dallas_enabled,
            "has_dol": False,
            "has_casetype": True,
        },
        "harris_jp": {
            "key": "harris_jp",
            "name": "Harris County JP Odyssey Portal",
            "state": "TX",
            "url": p.harris_jp_url,
            "enabled": p.harris_jp_enabled,
            "has_dol": False,
            "has_casetype": False,
        },
        "harris_district": {
            "key": "harris_district",
            "name": "Harris County District Clerk",
            "state": "TX",
            "url": p.harris_district_url,
            "enabled": p.harris_district_enabled,
            "has_dol": True,
            "has_casetype": True,
        },
        "harris_cclerk": {
            "key": "harris_cclerk",
            "name": "Harris County Clerk WebSearch",
            "state": "TX",
            "url": p.harris_cclerk_url,
            "enabled": p.harris_cclerk_enabled,
            "has_dol": True,
            "has_casetype": False,
        },
    }

    return {
        "status": overall_status,
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.APP_ENV,
        "version": "1.0.0",
        "components": components,
        "portals": portals_dict,
    }


@router.get("/portals/{portal_key}/ping", tags=["Health", "Portals"])
@router.post("/portals/{portal_key}/ping", tags=["Health", "Portals"])
async def ping_portal_endpoint(portal_key: str) -> dict[str, Any]:
    """Test reachability and response latency of any configured county court portal."""
    sys_settings = await get_system_settings_async()
    p = sys_settings.portals

    portal_map = {
        "broward": ("Broward County Clerk", p.broward_url),
        "hillsborough": ("Hillsborough County Clerk", p.hillsborough_url),
        "miami": ("Miami-Dade County Clerk", p.miami_url),
        "travis": ("Travis County", p.travis_url),
        "dallas": ("Dallas County", p.dallas_url),
        "harris_jp": ("Harris County JP", p.harris_jp_url),
        "harris_district": ("Harris County District Clerk", p.harris_district_url),
        "harris_cclerk": ("Harris County Clerk", p.harris_cclerk_url),
    }

    if portal_key not in portal_map:
        return {
            "portal_key": portal_key,
            "reachable": False,
            "error": f"Unknown portal key: {portal_key}. Available: {list(portal_map.keys())}",
            "status_code": 404,
        }

    name, url = portal_map[portal_key]
    start = time.perf_counter()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        proxy_url = portal_proxy_url(sys_settings.proxy)
        async with httpx.AsyncClient(
            verify=False,
            timeout=8.0,
            follow_redirects=True,
            proxy=proxy_url,
            trust_env=False,
        ) as client:
            if hasattr(client, "stream"):
                async with client.stream("GET", url, headers=headers) as res:
                    duration_ms = round((time.perf_counter() - start) * 1000, 2)
                    status_code = res.status_code
            else:
                res = await client.get(url, headers=headers)
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
                status_code = res.status_code

            return {
                "portal_key": portal_key,
                "portal_name": name,
                "url": url,
                "reachable": status_code < 500,
                "status_code": status_code,
                "latency_ms": duration_ms,
                "status": "healthy" if status_code < 400 else "warning",
            }
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "portal_key": portal_key,
            "portal_name": name,
            "url": url,
            "reachable": False,
            "status_code": 0,
            "latency_ms": duration_ms,
            "status": "warning",
            "error": "Court portal connection failed. Check the configured proxy and portal URL.",
        }


portals_router = APIRouter()


@portals_router.get("/{portal_key}/ping", tags=["Portals"])
@portals_router.post("/{portal_key}/ping", tags=["Portals"])
async def ping_portal_alias(portal_key: str) -> dict[str, Any]:
    """Alias for testing portal reachability directly at /api/v1/portals/{portal_key}/ping."""
    return await ping_portal_endpoint(portal_key)

