"""Application settings and environment configuration using Pydantic Settings."""

import json
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB_FILE = (_BACKEND_DIR / "orchestrator.db").resolve()
_DEFAULT_DB_URL = f"sqlite+aiosqlite:///{_DEFAULT_DB_FILE.as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General App Config
    APP_NAME: str = "UAIC Claim & RPA Orchestrator"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "supersecretdevelopmentkeyfororchestrator"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: list[str] | str = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # Database (PostgreSQL default or SQLite local anchored to backend/orchestrator.db)
    DATABASE_URL: str = _DEFAULT_DB_URL

    # Redis & Celery Message Broker
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://127.0.0.1:6379/1"

    # Fuzzy Matching Engine Parameters
    FUZZY_MATCH_DEFAULT_THRESHOLD: float = 0.60
    FUZZY_MATCH_BORDERLINE_THRESHOLD: float = 0.40

    # Downstream Guidewire Integration
    GUIDEWIRE_MOCK_MODE: bool = True
    GUIDEWIRE_API_URL: str = "https://uaic-gwcp-prod-igoauthproxy.api.delta4-andromeda.guidewire.net/api/powerapps/caseupdate"
    GUIDEWIRE_API_KEY: str = ""

    # Web Automation (Playwright)
    PLAYWRIGHT_HEADLESS: bool = False
    PLAYWRIGHT_USE_CHROME: bool = True
    PLAYWRIGHT_TIMEOUT_MS: int = 30000
    PLAYWRIGHT_VIEWPORT_WIDTH: int = 1280
    PLAYWRIGHT_VIEWPORT_HEIGHT: int = 800
    SCREENSHOTS_DIR: Path = (_BACKEND_DIR / "screenshots").resolve()
    LOGS_DIR: Path = (_BACKEND_DIR / "logs").resolve()

    # Portals
    PORTAL_BROWARD_URL: str = "https://www.browardclerk.org/Web2"
    PORTAL_HILLSBOROUGH_URL: str = "https://hover.hillsclerk.com/html/caseSearch.html"
    PORTAL_MIAMI_URL: str = "https://onlineservices.miami-dadeclerk.com/civil/"
    PORTAL_TRAVIS_URL: str = "https://odysseypa.traviscountytx.gov/CourtDirectorySearch/"
    PORTAL_DALLAS_URL: str = "https://courtsportal.dallascounty.org/DALLASPROD/"
    PORTAL_HARRIS_JP_URL: str = "https://jpwebsite.harriscountytx.gov/Public/CivilSearch.aspx"
    PORTAL_HARRIS_CCLERK_URL: str = "https://www.cclerk.hctx.net/applications/websearch/courtsearch.aspx?CaseType=Civil"
    PORTAL_HARRIS_DISTRICT_URL: str = "https://www.hcdistrictclerk.com/edocs/public/CaseDetails.aspx"

    # Whitelisted Legacy Case Types & Statuses
    ALLOWED_CASE_STATUSES: list[str] = [
        "ACTIVE",
        "REOPENED ACTIVE",
        "OPEN",
        "REOPEN",
        "EXTENDED",
        "HEARING SCHEDULED",
        "NONSUIT",
        "OPEN / MISSING FILE DOCUMENTS",
        "RE-OPENED",
        "RESTORED",
        "TRANSFERRED",
        "READY DOCKET",
        "ACTIVE – CIVIL",
        "IN TRIAL",
        "PC1: ACTIVE CASE ON DOCKET",
    ]

    ALLOWED_CASE_TYPES: list[str] = [
        "CIVIL ACTION CENTRAL",
        "COUNTY CIVIL CENTRAL",
        "COUNTY CIVIL NORTH",
        "COUNTY CIVIL SOUTH",
        "COUNTY CIVIL WEST",
        "CIRCUIT CIVIL",
        "COUNTY CIVIL",
        "SMALL CLAIMS",
        "SUMMARY PROCEDURE",
        "COUNTY COURTS – CIVIL",
        "DISTRICT COURTS – CIVIL",
        "OTHER CIVIL",
        "BILL OF REVIEW",
        "BREACH OF CONTRACT",
        "CONSTRUCTION DAMAGES",
        "DAMAGES – AUTO",
        "DAMAGES – OTHER",
        "DECLARATORY JUDGMENT",
        "DTPA – DECEPTIVE TRADE PRACTICE",
        "INSURANCE",
        "INSURANCE POLICY",
        "INSURANCE POLICY – HURRICANE",
        "OTHER PROPERTY",
        "PERSONAL INJURY – AUTO",
    ]


settings = Settings()
