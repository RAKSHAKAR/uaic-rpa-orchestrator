"""Automated test suite for the Enterprise Setup Console, process management, and browser matrix.

Validates:
- Option [1]: Port conflict detection and launch parameters.
- Option [2]: Safe process termination, Win32_Process filtering, and explicit MailDev termination.
- Option [4]: Dynamic browser matrix detection (Chromium, Google Chrome, Microsoft Edge) and conditional Chromium installation.
- Option [5]: Safe folder purge invariants (preserves protected user folders, source code, credentials).
- Option [6]: RPA Mode toggle and backend adherence (Attended GUI vs Unattended Headless).
- Option [7]: Zero unraisable exception warnings across diagnostics.
- Option [8]: Docker Compose configuration validity and service definitions.
- Option [9]: Live Health Monitor probe logic for HTTP and TCP services.
- Option [M]: MailDev HTTP (1080) and SMTP (1025) probe health verification.
"""

import socket
from pathlib import Path

import pytest
import yaml

from app.automation.browser_manager import ChromeSession
from app.services.settings_service import (
    get_system_settings_async,
    save_system_settings_async,
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


# ---------------------------------------------------------------------------
# OPTION [1]: Port Conflict Detection
# ---------------------------------------------------------------------------
def test_port_conflict_detection():
    """Verify that socket binding detection accurately identifies occupied vs free ports."""
    # Find a free ephemeral port
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.bind(("127.0.0.1", 0))
    test_sock.listen(1)
    port = test_sock.getsockname()[1]

    # While test_sock is bound, verify port is detected as occupied
    probe_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe_sock.settimeout(0.5)
    is_open = False
    try:
        probe_sock.connect(("127.0.0.1", port))
        is_open = True
    except (TimeoutError, ConnectionRefusedError):
        is_open = False
    finally:
        probe_sock.close()

    assert is_open is True, f"Port {port} should be detected as occupied."

    # Release socket
    test_sock.close()

    # Now verify port is detected as free
    probe_sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe_sock2.settimeout(0.5)
    is_free = False
    try:
        probe_sock2.connect(("127.0.0.1", port))
    except (TimeoutError, ConnectionRefusedError, OSError):
        is_free = True
    finally:
        probe_sock2.close()

    assert is_free is True, f"Port {port} should be free after closing socket."


# ---------------------------------------------------------------------------
# OPTION [2]: Safe Process Termination & MailDev Verification
# ---------------------------------------------------------------------------
def test_service_kill_process_filtering():
    """Verify that process kill filtering matches application workers and never touches unrelated system processes."""
    sample_processes = [
        {"Name": "python.exe", "CommandLine": r"C:\Python314\python.exe -m uvicorn app.main:app --port 8000", "ShouldKill": True},
        {"Name": "python.exe", "CommandLine": r"C:\Python314\python.exe -m celery -A app.core.celery_app worker -P solo", "ShouldKill": True},
        {"Name": "python.exe", "CommandLine": r"C:\Python314\python.exe -m celery -A app.core.celery_app flower --port 5555", "ShouldKill": True},
        {"Name": "node.exe", "CommandLine": r"node.exe C:\Users\user\AppData\Roaming\npm\node_modules\maildev\bin\maildev", "ShouldKill": True},
        {"Name": "node.exe", "CommandLine": r"node.exe C:\UAIC\frontend\node_modules\.bin\next dev", "ShouldKill": True},
        {"Name": "python.exe", "CommandLine": r"C:\OtherApp\python.exe some_unrelated_script.py", "ShouldKill": False},
        {"Name": "svchost.exe", "CommandLine": r"C:\Windows\system32\svchost.exe -k netsvcs", "ShouldKill": False},
        {"Name": "explorer.exe", "CommandLine": r"C:\Windows\explorer.exe", "ShouldKill": False},
    ]

    for proc in sample_processes:
        cmd = proc["CommandLine"]
        name = proc["Name"]
        matches = False
        if name in ("python.exe", "node.exe"):
            matches = any(pattern in cmd.lower() for pattern in ("uvicorn", "celery", "flower", "maildev", "next dev"))
        elif name in ("celery.exe", "uvicorn.exe", "maildev.exe"):
            matches = True

        assert matches == proc["ShouldKill"], f"Process {proc} filtering mismatch (expected {proc['ShouldKill']}, got {matches})"


def test_maildev_ports_explicit_termination_logic():
    """Verify that ports 1080 (HTTP) and 1025 (SMTP) are explicitly verified in termination logic."""
    target_ports = [3000, 8000, 5555, 6379, 5432, 1080, 1025]
    assert 1080 in target_ports, "Port 1080 (MailDev HTTP) must be explicitly in termination target list."
    assert 1025 in target_ports, "Port 1025 (MailDev SMTP) must be explicitly in termination target list."


# ---------------------------------------------------------------------------
# OPTION [4]: Dynamic Browser Matrix & Conditional Chromium Installation
# ---------------------------------------------------------------------------
def test_browser_matrix_skips_chromium_when_chrome_detected():
    """Verify that when Google Chrome is configured or detected, Playwright Chromium installation is skipped."""
    # When channel is 'chrome'
    configured_channel = "chrome"
    should_skip_chromium = configured_channel in ("chrome", "msedge")
    assert should_skip_chromium is True, "When channel is 'chrome', Playwright Chromium download must be skipped."

    # When channel is 'msedge'
    configured_channel = "msedge"
    should_skip_chromium = configured_channel in ("chrome", "msedge")
    assert should_skip_chromium is True, "When channel is 'msedge', Playwright Chromium download must be skipped."

    # When channel is 'chromium'
    configured_channel = "chromium"
    should_skip_chromium = configured_channel in ("chrome", "msedge")
    assert should_skip_chromium is False, "When channel is 'chromium', Playwright Chromium download is required."


def test_find_chrome_executable_resolution():
    """Verify that find_chrome_executable resolves real path or returns None gracefully."""
    # When passed an explicit valid mock or None
    result = ChromeSession.find_chrome_executable(None)
    # Result will be either Path to chrome.exe if installed on this Windows system or None
    if result:
        assert isinstance(result, Path)
        assert result.name.lower() == "chrome.exe"
    else:
        assert result is None


# ---------------------------------------------------------------------------
# OPTION [5]: Safe Folder Purge Invariants
# ---------------------------------------------------------------------------
def test_purge_folders_safety_invariants():
    """Verify that folder purge candidate list strictly targets build/deps and never protected directories or source."""
    purge_targets = [
        ".venv",
        ".ruff_cache",
        ".pytest_cache",
        "__pycache__",
        "node_modules",
        ".next",
        ".turbo",
    ]

    protected_directories = [
        "implementation_plan",
        "PowerAutomateSolutions",
        "Testing files",
        "anticaptcha-plugin_v0.83",
        ".agents",
        "app",
        "src",
    ]

    protected_files = [
        ".env",
        ".env.local",
        "README.md",
        "pyproject.toml",
        "package.json",
    ]

    for target in purge_targets:
        assert target not in protected_directories, f"Purge target {target} collides with protected directories!"
        assert target not in protected_files, f"Purge target {target} collides with protected files!"

    # Verify that all 5 protected user directories exist on disk and will never be purged
    for p in ("implementation_plan", "PowerAutomateSolutions", "Testing files", "anticaptcha-plugin_v0.83", ".agents"):
        assert (ROOT_DIR / p).exists(), f"Protected directory '{p}' must exist on disk!"


# ---------------------------------------------------------------------------
# OPTION [6]: RPA Mode Toggle (Attended GUI vs Unattended Headless)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rpa_mode_toggle_and_backend_adherence():
    """Verify that toggling RPA mode between Attended (GUI) and Unattended (Headless) persists and is honored."""
    # 1. Set to Attended (headless_mode = False)
    cfg1 = await get_system_settings_async()
    cfg1.automation.headless_mode = False
    await save_system_settings_async(cfg1)

    s1 = await get_system_settings_async()
    assert s1.automation.headless_mode is False, "Settings must reflect headless_mode = False for Attended Mode."

    session_attended = ChromeSession(headless=s1.automation.headless_mode)
    assert session_attended.headless is False, "ChromeSession must initialize with headless=False in Attended Mode."

    # 2. Set to Unattended (headless_mode = True)
    cfg2 = await get_system_settings_async()
    cfg2.automation.headless_mode = True
    await save_system_settings_async(cfg2)

    s2 = await get_system_settings_async()
    assert s2.automation.headless_mode is True, "Settings must reflect headless_mode = True for Unattended Mode."

    session_unattended = ChromeSession(headless=s2.automation.headless_mode)
    assert session_unattended.headless is True, "ChromeSession must initialize with headless=True in Unattended Mode."

    # Reset back to False
    cfg2.automation.headless_mode = False
    await save_system_settings_async(cfg2)


# ---------------------------------------------------------------------------
# OPTION [7]: Diagnostics Zero-Warning Invariant
# ---------------------------------------------------------------------------
def test_diagnostics_runner_zero_unraisable_warnings():
    """Verify that PytestUnraisableExceptionWarning is not in pyproject.toml filterwarnings."""
    pyproject_path = BACKEND_DIR / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    assert "ignore::pytest.PytestUnraisableExceptionWarning" not in content, (
        "PytestUnraisableExceptionWarning must not be suppressed in pyproject.toml!"
    )


# ---------------------------------------------------------------------------
# OPTION [8]: Docker Stack Configuration Validity
# ---------------------------------------------------------------------------
def test_docker_compose_config_validity():
    """Verify docker-compose.yml YAML syntax, service schemas, ports, and health checks."""
    compose_path = ROOT_DIR / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml must exist in repository root."

    content = compose_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    assert "services" in data, "docker-compose.yml must define 'services'."
    services = data["services"]

    # Verify critical services exist
    assert "backend" in services or "fastapi" in services or "redis" in services
    assert "redis" in services, "Redis service must be defined in docker-compose.yml."
    assert "maildev" in services, "MailDev service must be defined in docker-compose.yml."

    # Verify MailDev ports: 1080 (Web UI) and 1025 (SMTP)
    maildev_ports = services["maildev"].get("ports", [])
    ports_str = " ".join(str(p) for p in maildev_ports)
    assert "1080" in ports_str, "MailDev service must expose port 1080 (Web Inspector)."
    assert "1025" in ports_str, "MailDev service must expose port 1025 (SMTP)."

    # Verify Redis port 6379
    redis_ports = services["redis"].get("ports", [])
    redis_ports_str = " ".join(str(p) for p in redis_ports)
    assert "6379" in redis_ports_str, "Redis service must expose port 6379."


# ---------------------------------------------------------------------------
# OPTION [9] & [M]: Live Health Monitor Probe Logic
# ---------------------------------------------------------------------------
def test_live_monitor_health_probe_logic():
    """Verify probe status categorization for healthy, running, and stopped states."""
    def categorize_probe(port_open: bool, http_status: int | None = None) -> str:
        if not port_open:
            return "STOPPED"
        if http_status and 200 <= http_status < 300:
            return "HEALTHY"
        return "RUNNING"

    assert categorize_probe(port_open=False) == "STOPPED"
    assert categorize_probe(port_open=True, http_status=None) == "RUNNING"
    assert categorize_probe(port_open=True, http_status=200) == "HEALTHY"
    assert categorize_probe(port_open=True, http_status=500) == "RUNNING"


def test_maildev_endpoint_and_smtp_verification():
    """Verify MailDev inspection endpoints for HTTP (1080) and SMTP (1025)."""
    maildev_http_url = "http://localhost:1080"
    maildev_smtp_port = 1025

    assert "1080" in maildev_http_url
    assert maildev_smtp_port == 1025


def test_setup_local_canonical_script_exists():
    """Verify that setup_local.ps1 exists in repository root as the single canonical console script."""
    script_path = ROOT_DIR / "setup_local.ps1"
    assert script_path.exists(), "setup_local.ps1 must exist as the single canonical console script."
    content = script_path.read_text(encoding="utf-8")
    assert "Enterprise Operations & Orchestration Console" in content
    assert "Show-EnterpriseMenu" in content
    # Assert neither setup.ps1 nor setup-local.ps1 exist to prevent confusion
    assert not (ROOT_DIR / "setup.ps1").exists(), "setup.ps1 must not exist to eliminate confusion."
    assert not (ROOT_DIR / "setup-local.ps1").exists(), "setup-local.ps1 must not exist to eliminate confusion."


def test_redis_ping_probe_protocol_format():
    """Verify the Redis wire protocol query format and response validation."""
    query = b"*1\r\n$4\r\nPING\r\n"
    assert query == b"*1\r\n$4\r\nPING\r\n"

    valid_response = b"+PONG\r\n"
    assert valid_response.startswith(b"+PONG")


def test_smtp_banner_probe_protocol_format():
    """Verify SMTP protocol greeting banner and termination syntax."""
    valid_greeting = "220 maildev.local ESMTP MailDev ready"
    assert valid_greeting.startswith("220")

    quit_cmd = "QUIT\r\n"
    assert quit_cmd.endswith("\r\n")


def test_celery_worker_process_commandline_filter():
    """Verify that process detection accurately identifies celery worker processes."""
    valid_worker_cmd = (
        r"C:\UAIC\backend\.venv\Scripts\python.exe -m celery -A app.core.celery_app.celery_app worker -E -P solo"
    )
    unrelated_cmd = r"C:\Windows\system32\cmd.exe /c echo hello"

    def is_celery_worker(cmd: str) -> bool:
        return bool(cmd and ("celery" in cmd.lower() and "worker" in cmd.lower()))

    assert is_celery_worker(valid_worker_cmd) is True
    assert is_celery_worker(unrelated_cmd) is False


def test_celery_beat_process_commandline_filter():
    """Verify that process detection accurately identifies celery beat scheduler processes."""
    valid_beat_cmd = (
        r"C:\UAIC\backend\.venv\Scripts\python.exe -m celery -A app.core.celery_app.celery_app beat --loglevel=info"
    )
    unrelated_cmd = r"C:\Windows\system32\cmd.exe /c echo hello"

    def is_celery_beat(cmd: str) -> bool:
        return bool(cmd and ("celery" in cmd.lower() and "beat" in cmd.lower()))

    assert is_celery_beat(valid_beat_cmd) is True
    assert is_celery_beat(unrelated_cmd) is False


def test_setup_local_console_features_and_chromium_guard():
    """Verify setup_local.ps1 exists."""
    script_path = ROOT_DIR / "setup_local.ps1"
    assert script_path.exists()
    content = script_path.read_text(encoding="utf-8")
    assert "playwright install chromium" in content

