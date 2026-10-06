"""Runtime multi-version compatibility polyfills (Python 3.10 through 3.14)."""

from __future__ import annotations

import datetime as _dt
import enum as _enum

# Python 3.10 compatibility: backport datetime.UTC
if not hasattr(_dt, "UTC"):
    _dt.UTC = getattr(_dt, "timezone").utc  # noqa: UP017

# Python 3.10 compatibility: backport enum.StrEnum
if not hasattr(_enum, "StrEnum"):
    class StrEnum(str, _enum.Enum):  # noqa: UP042
        """Python 3.10 compatibility backport for StrEnum."""

        def __str__(self) -> str:
            return str(self.value)

        def __format__(self, format_spec: str) -> str:
            return str(self.value).__format__(format_spec)

    _enum.StrEnum = StrEnum
else:
    StrEnum = _enum.StrEnum


def utc_now() -> _dt.datetime:
    """Return timezone-naive UTC timestamp compatible with PostgreSQL TIMESTAMP WITHOUT TIME ZONE, asyncpg, and SQLite."""
    return _dt.datetime.now(_dt.timezone.utc).replace(tzinfo=None)  # noqa: UP017


__all__ = ["StrEnum", "utc_now"]
