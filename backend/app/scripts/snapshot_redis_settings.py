"""Make a local, user-bound encrypted backup of the legacy Redis settings key.

The snapshot contains secrets, so this utility never prints the document and
uses Windows DPAPI CurrentUser encryption before writing to disk.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path

import redis
from dotenv import dotenv_values


class DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def protect_for_current_user(raw: bytes) -> bytes:
    """Encrypt bytes with the Windows account's DPAPI key."""
    source_buffer = ctypes.create_string_buffer(raw)
    source = DataBlob(len(raw), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_byte)))
    destination = DataBlob()
    crypt32 = ctypes.windll.crypt32
    if not crypt32.CryptProtectData(
        ctypes.byref(source), None, None, None, None, 0, ctypes.byref(destination)
    ):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(destination.pbData, destination.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(destination.pbData)


def main() -> None:
    if os.name != "nt":
        raise RuntimeError("This snapshot utility requires Windows DPAPI")
    repository_root = Path(__file__).resolve().parents[3]
    env_values = dotenv_values(repository_root / "backend" / ".env")
    redis_url = os.environ.get("REDIS_URL") or env_values.get("REDIS_URL") or "redis://localhost:6379/0"
    client = redis.Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
    try:
        raw = client.get("uaic:system:settings:v4")
    finally:
        client.close()
    if raw is None:
        print("Legacy Redis settings key is absent; no snapshot created")
        return
    encrypted = protect_for_current_user(raw)
    backup_dir = repository_root / "backend" / "data" / "settings_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    destination = backup_dir / f"pre_migration_{timestamp}.dpapi"
    with destination.open("xb") as stream:
        stream.write(encrypted)
    print(f"Encrypted Redis snapshot saved: {destination}; bytes={len(raw)}; sha256={hashlib.sha256(raw).hexdigest()}")


if __name__ == "__main__":
    main()
