"""Automation package exporting BaseScraper and county scrapers."""

from app.automation.base import BaseCourtScraper
from app.automation.browser_manager import (
    BrowserManager,
    CaptchaManager,
    ChromeSession,
    CountySiteAdapter,
    ExtensionManager,
    SiteAutomationManager,
    TabManager,
)
from app.automation.florida import (
    BrowardScraper,
    HillsboroughScraper,
    MiamiDadeScraper,
)
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)

__all__ = [
    "BaseCourtScraper",
    "BrowardScraper",
    "BrowserManager",
    "CaptchaManager",
    "ChromeSession",
    "CountySiteAdapter",
    "DallasScraper",
    "ExtensionManager",
    "HarrisCountyClerkScraper",
    "HarrisDistrictClerkScraper",
    "HarrisJPScraper",
    "HillsboroughScraper",
    "MiamiDadeScraper",
    "SiteAutomationManager",
    "TabManager",
    "TravisScraper",
]
