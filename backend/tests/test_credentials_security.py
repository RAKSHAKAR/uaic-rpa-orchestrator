"""Test credentials security and elimination of hardcoded credentials (TC-SEC-001 through TC-SEC-004)."""

import inspect

from app.automation.florida import MiamiDadeScraper


def test_tc_sec_001_miami_init_defaults_none():
    """TC-SEC-001: MiamiDadeScraper initialized with no args has None credentials."""
    scraper = MiamiDadeScraper()
    assert scraper.username is None
    assert scraper.password is None


def test_tc_sec_002_miami_init_explicit_credentials():
    """TC-SEC-002: MiamiDadeScraper accepts and stores explicit credentials."""
    scraper = MiamiDadeScraper(username="admin@domain.com", password="SecurePassword123")
    assert scraper.username == "admin@domain.com"
    assert scraper.password == "SecurePassword123"


def test_tc_sec_003_no_hardcoded_email_in_miami_source():
    """TC-SEC-003: No hardcoded email strings in miami.py source."""
    miami_path = inspect.getfile(MiamiDadeScraper)
    with open(miami_path, encoding="utf-8") as f:
        content = f.read()
    assert "apoorvnigam" not in content.lower(), "Hardcoded email found in miami.py!"


def test_tc_sec_004_no_hardcoded_password_in_miami_source():
    """TC-SEC-004: No hardcoded password strings in miami.py source."""
    miami_path = inspect.getfile(MiamiDadeScraper)
    with open(miami_path, encoding="utf-8") as f:
        content = f.read()
    assert "apoorv@" not in content.lower(), "Hardcoded password found in miami.py!"
