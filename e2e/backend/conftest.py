import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def _is_redis_available() -> bool:
    try:
        from app.core.config import settings
        if getattr(settings, "SEMAPHORE_BYPASS", False):
            return False
        import redis
        r = redis.Redis(host="127.0.0.1", port=6379, socket_connect_timeout=0.3, socket_timeout=0.3)
        return bool(r.ping())
    except Exception:
        return False


_REDIS_UP = _is_redis_available()


@pytest.fixture(autouse=True)
def mock_celery_when_no_redis(monkeypatch):
    if not _REDIS_UP:
        from app.core.celery_app import celery_app
        monkeypatch.setattr(celery_app, "send_task", MagicMock(return_value=MagicMock(id="mock-celery-task-id")))
        monkeypatch.setattr(celery_app.control, "ping", MagicMock(return_value=[]))

