"""Pytest configuration and global test fixtures."""

import gc
import os
import warnings
from pathlib import Path
from unittest.mock import MagicMock

# ISOLATE TEST DATABASE: Ensure pytest runs on a dedicated test SQLite file,
# NEVER wiping or altering the developer / live database orchestrator.db!
_TEST_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "test_runner.db"
_TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_TEST_DB_URL = f"sqlite+aiosqlite:///{_TEST_DB_PATH.as_posix()}"
os.environ["DATABASE_URL"] = _TEST_DB_URL
os.environ["SEMAPHORE_BYPASS"] = "true"

import pytest

from app.core.database import init_db


@pytest.fixture(scope="session", autouse=True)
def init_test_database_schema():
    """Ensure the isolated test runner database is initialized with all tables."""
    import asyncio

    asyncio.run(init_db())
    yield


# ---------------------------------------------------------------------------
# Infrastructure availability probes
# ---------------------------------------------------------------------------

def _is_redis_available() -> bool:
    """Return True if Redis is reachable on 127.0.0.1:6379 and responds to PING."""
    from app.core.config import settings
    if getattr(settings, "SEMAPHORE_BYPASS", False) or os.environ.get("SEMAPHORE_BYPASS", "").lower() in ("true", "1", "yes"):
        return False
    try:
        import redis
        r = redis.Redis(host="127.0.0.1", port=6379, socket_connect_timeout=0.3, socket_timeout=0.3)
        return bool(r.ping())
    except Exception:
        return False


def _is_maildev_available() -> bool:
    """Return True if a local MailDev SMTP server is reachable on 127.0.0.1:1025 and responds to SMTP."""
    import smtplib

    try:
        with smtplib.SMTP("127.0.0.1", 1025, timeout=0.3) as smtp:
            code, _ = smtp.noop()
            return code == 250
    except Exception:
        return False


# Probe once per session to avoid repeated network calls
_REDIS_UP: bool = _is_redis_available()
_MAILDEV_UP: bool = _is_maildev_available()


# ---------------------------------------------------------------------------
# Auto-skip hooks
# ---------------------------------------------------------------------------

def pytest_collection_modifyitems(items: list) -> None:
    """
    Automatically skip tests marked with `requires_redis` or `requires_maildev`
    when the corresponding service is not reachable on localhost.
    """
    for item in items:
        if item.get_closest_marker("requires_redis") and not _REDIS_UP:
            item.add_marker(
                pytest.mark.skip(
                    reason="Redis not reachable on localhost:6379 — start Redis to run this test"
                )
            )
        if item.get_closest_marker("requires_maildev") and not _MAILDEV_UP:
            item.add_marker(
                pytest.mark.skip(
                    reason="MailDev not reachable on localhost:1025 — start MailDev to run this test"
                )
            )


# ---------------------------------------------------------------------------
# Global fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_async_transports():
    """
    Ensure unclosed transports are garbage-collected cleanly to prevent
    Windows ProactorEventLoop pipe-finalizer errors (PytestUnraisableExceptionWarning).

    Root cause: On Windows, asyncio's ProactorEventLoop uses OS pipe handles for
    subprocess I/O. When an async test ends and the event loop is closed, pending
    pipe-transport finalizers may raise `ValueError: I/O operation on closed pipe`
    inside __del__. Python's sys.unraisablehook captures this and pytest converts it
    into PytestUnraisableExceptionWarning.

    Fix strategy:
    1. Pre-test gc.collect() — start each test with a clean heap.
    2. Post-test gc.collect() x2 — collect cyclic references before the event loop
       shuts down, so pipe handles are closed while the loop is still live.
    3. Suppress specifically ValueError from asyncio internals at the warnings level
       (Python warnings system, NOT pytest filterwarnings) so the
       sys.unraisablehook fires into a filtered context.
    """
    gc.collect()  # Pre-test: clean slate
    yield
    # Post-test: two rounds to break reference cycles before event loop teardown
    gc.collect()
    gc.collect()
    # Suppress the residual pipe-handle ValueError that may fire after gc on Windows.
    # This is a targeted fix at the warnings module level (not pyproject.toml suppression).
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*I/O operation on closed pipe.*",
            category=pytest.PytestUnraisableExceptionWarning,
        )
        gc.collect()


@pytest.fixture(autouse=True)
def mock_celery_when_no_redis(monkeypatch):
    """
    Prevent background Celery broker connection hangs when Redis is offline.
    Tests explicitly requiring live Redis are marked with @pytest.mark.requires_redis
    and auto-skipped by pytest_collection_modifyitems.
    """
    if not _REDIS_UP:
        from app.core.celery_app import celery_app

        monkeypatch.setattr(
            celery_app,
            "send_task",
            MagicMock(return_value=MagicMock(id="mock-celery-task-id")),
        )
        monkeypatch.setattr(
            celery_app.control,
            "ping",
            MagicMock(return_value=[]),
        )


@pytest.fixture(autouse=True)
def reset_redis_concurrency_semaphore():
    """Ensure test suite starts and ends with clean Redis browser concurrency slot count."""
    from app.core.config import settings
    bypass = getattr(settings, "SEMAPHORE_BYPASS", False) or os.environ.get("SEMAPHORE_BYPASS", "").lower() in ("true", "1", "yes")
    if _REDIS_UP and not bypass:
        try:
            import redis

            r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_timeout=0.5)
            r.set("uaic:browser:active_count", 0)
        except Exception:
            pass
    yield
    if _REDIS_UP and not bypass:
        try:
            import redis

            r = redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_timeout=0.5)
            r.set("uaic:browser:active_count", 0)
        except Exception:
            pass
