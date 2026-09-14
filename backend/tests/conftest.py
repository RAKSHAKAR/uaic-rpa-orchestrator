"""Pytest configuration and global test fixtures."""

import gc
import socket
import warnings
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Infrastructure availability probes
# ---------------------------------------------------------------------------

def _is_redis_available() -> bool:
    """Return True if Redis is reachable on 127.0.0.1:6379."""
    try:
        with socket.create_connection(("127.0.0.1", 6379), timeout=0.2):
            return True
    except OSError:
        return False


def _is_maildev_available() -> bool:
    """Return True if a local MailDev SMTP server is reachable on 127.0.0.1:1025."""
    try:
        with socket.create_connection(("127.0.0.1", 1025), timeout=0.2):
            return True
    except OSError:
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

