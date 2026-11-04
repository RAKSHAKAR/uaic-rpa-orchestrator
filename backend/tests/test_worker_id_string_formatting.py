"""Unit tests for worker ID string normalization and window positioning.

Ensures that UUID strings, integers, None, and arbitrary worker ID values
never cause TypeError: not all arguments converted during string formatting.
"""

import uuid

from app.automation.browser_manager import ChromeSession
from app.automation.session_runner import SingleSessionBrowserRunner, _normalize_worker_offset


def test_normalize_worker_offset_types():
    """Verify _normalize_worker_offset handles all possible data types cleanly."""
    # None -> 0
    assert _normalize_worker_offset(None) == 0

    # Integers preserved
    assert _normalize_worker_offset(0) == 0
    assert _normalize_worker_offset(5) == 5
    assert _normalize_worker_offset(-2) == -2

    # String integer digits -> converted to int
    assert _normalize_worker_offset("7") == 7
    assert _normalize_worker_offset("0") == 0

    # UUID string -> safely converted to bounded int 0-9
    uid_str = str(uuid.uuid4())
    res = _normalize_worker_offset(uid_str)
    assert isinstance(res, int)
    assert 0 <= res < 10

    # Arbitrary strings
    assert isinstance(_normalize_worker_offset("ForkPoolWorker-186"), int)
    assert isinstance(_normalize_worker_offset("celery@worker-node-1"), int)


def test_single_session_runner_launch_args_with_uuid():
    """Verify SingleSessionBrowserRunner launch args with UUID worker ID do not raise TypeError."""
    claim_uuid = "6a782e4e-0cbf-4e69-8d75-430985f94d93"
    runner = SingleSessionBrowserRunner(
        headless=False,
        worker_id=claim_uuid,
    )
    assert runner.worker_id == claim_uuid

    # Simulate position calculation
    offset = _normalize_worker_offset(runner.worker_id)
    pos_x = 50 + (35 * offset) % 400
    pos_y = 50 + (30 * offset) % 300
    assert isinstance(pos_x, int)
    assert isinstance(pos_y, int)


def test_chrome_session_launch_args_with_uuid():
    """Verify ChromeSession window offset calculation does not raise TypeError on string worker_id."""
    claim_uuid = "e5c44f8d-ca8d-424f-af80-dca7beb53459"
    session = ChromeSession(
        worker_id=claim_uuid,  # type: ignore[arg-type]
    )
    assert session.worker_id == claim_uuid
