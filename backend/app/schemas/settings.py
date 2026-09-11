"""Pydantic schemas for dynamic system, scraper portals, Guidewire, and automation settings."""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


def get_default_chrome_binary() -> str:
    """Dynamically resolve standard Google Chrome executable path on Windows."""
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("LocalAppData", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return str(c.resolve())
    return r"C:\Program Files\Google\Chrome\Application\chrome.exe"


CHROME_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
MSEDGE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
CHROMIUM_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def get_engine_user_agent(engine: str | None) -> str:
    """Return standard matching User-Agent string for the given browser engine."""
    eng = (engine or "chromium").lower()
    if eng == "msedge":
        return MSEDGE_USER_AGENT
    return CHROME_USER_AGENT


def get_default_extension_dir() -> str:
    """Return relative path for anticaptcha-plugin_v0.83 relative to solution root."""
    return ".\\anticaptcha-plugin_v0.83\\"


class AutomationSettings(BaseModel):
    """Browser automation and anti-captcha settings."""
    max_captcha_attempts: int = Field(default=2, ge=1, le=20, description="Max retry attempts for CAPTCHA solving with page reload")
    captcha_wait_seconds: int = Field(default=120, ge=5, le=300, description="Seconds to wait for CAPTCHA token resolution before timeout/reload")
    page_timeout_seconds: int = Field(default=60, ge=5, le=180, description="Browser page navigation timeout in seconds")
    reload_backoff_seconds: int = Field(default=2, ge=0, le=30, description="Cool-down delay in seconds before refreshing page on bot retry/throttle")
    headless_mode: bool = Field(default=False, description="Run browser in headless background mode (False for visible Chrome)")
    browser_engine: str = Field(
        default="chromium",
        description="Browser engine: chromium (Playwright default, recommended for extension support), chrome (host executable), or msedge",
    )
    use_chrome_browser: bool = Field(default=True, description="Always launch Google Chrome browser (supports Chrome extensions like AntiCaptcha)")
    chrome_binary_path: str | None = Field(default_factory=get_default_chrome_binary, description="Google Chrome executable path (default: Windows Program Files)")
    chrome_extension_dir: str | None = Field(default_factory=get_default_extension_dir, description="AntiCaptcha Chrome Extension Directory Path (default: relative)")
    anticaptcha_api_key: str | None = Field(default="28b486b8f31f74c6bf4453735815aa53", description="AntiCaptcha API Key for auto-solving")
    chrome_user_data_dir: str | None = Field(default="", description="Path to Chrome User Data for persistent extension settings (optional, keep blank by default)")
    user_agent: str = Field(
        default=CHROMIUM_USER_AGENT,
        description="Browser User-Agent header string",
    )
    max_concurrent_claims: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Concurrent claims scraped in parallel (1 = sequential FIFO, 2-10 = parallel multi-worker)",
    )


class PortalsSettings(BaseModel):
    """Court scraper portal endpoints and activation toggles."""
    # Florida
    broward_url: str = Field(default="https://www.browardclerk.org/", description="Broward County Clerk Portal URL")
    broward_enabled: bool = Field(default=True, description="Enable Broward County Scraper")
    
    hillsborough_url: str = Field(default="https://hover.hillsclerk.com/", description="Hillsborough County Clerk Portal URL")
    hillsborough_enabled: bool = Field(default=True, description="Enable Hillsborough County Scraper")
    
    miami_url: str = Field(default="https://www2.miamidadeclerk.gov/ocs", description="Miami-Dade County Clerk Portal URL")
    miami_enabled: bool = Field(default=True, description="Enable Miami-Dade County Scraper")
    miami_username: str = Field(default="apoorvnigam07@gmail.com", description="Miami-Dade OCS Portal Login Username/Email")
    miami_password: str = Field(default="Apoorv@12345", description="Miami-Dade OCS Portal Login Password")
    miami_requires_login: bool = Field(default=True, description="Requires authentication to scrape Miami-Dade OCS portal")
    
    # Texas
    travis_url: str = Field(default="https://odysseyweb.traviscountytx.gov/Portal/", description="Travis County Odyssey Portal URL")
    travis_enabled: bool = Field(default=True, description="Enable Travis County Scraper")
    
    dallas_url: str = Field(default="https://courtsportal.dallascounty.org/DALLASPROD/Home/", description="Dallas County Courts Portal URL")
    dallas_enabled: bool = Field(default=True, description="Enable Dallas County Scraper")
    
    harris_jp_url: str = Field(default="https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/", description="Harris County JP Courts Portal URL")
    harris_jp_enabled: bool = Field(default=True, description="Enable Harris County JP Scraper")
    
    harris_cclerk_url: str = Field(default="https://www.cclerk.hctx.net/Applications/WebSearch/", description="Harris County Clerk Portal URL")
    harris_cclerk_enabled: bool = Field(default=True, description="Enable Harris County Clerk Scraper")
    
    harris_district_url: str = Field(default="https://www.hcdistrictclerk.com/", description="Harris District Clerk Portal URL")
    harris_district_enabled: bool = Field(default=True, description="Enable Harris District Clerk Scraper")


class FuzzyMatcherSettings(BaseModel):
    """RapidFuzz deduplication and eligibility settings."""
    auto_match_threshold: float = Field(default=0.60, ge=0.0, le=1.0, description="Similarity score threshold for automatic match approval")
    manual_review_threshold: float = Field(default=0.40, ge=0.0, le=1.0, description="Similarity score threshold for sending to human review")
    scorer_algorithm: str = Field(
        default="token_sort_ratio",
        description="Fuzzy matching algorithm (token_sort_ratio, token_set_ratio, partial_ratio, ratio)",
    )
    min_filing_date: str = Field(default="2010-01-01", description="Minimum court case filing date (YYYY-MM-DD)")
    clean_party_name_patterns: list[str] = Field(
        default_factory=lambda: [
            "LLC",
            "INC",
            "CORP",
            "CORPORATION",
            "CO.",
            "COMPANY",
            "ET AL",
            "INDIVIDUALLY",
            "A/A/O",
            "AS ASSIGNEE OF",
            "D/B/A",
            "PA",
            "P.A.",
            "L.L.C.",
        ],
        description="Corporate noise and suffix words to strip during party name normalization",
    )
    whitelisted_statuses: list[str] = Field(
        default_factory=lambda: ["OPEN", "PENDING", "ACTIVE", "FILED", "REOPENED"],
        description="Case statuses considered active and eligible",
    )
    whitelisted_case_types: list[str] = Field(
        default_factory=lambda: [
            "CIRCUIT CIVIL",
            "COUNTY CIVIL",
            "CIVIL",
            "AUTO NEGLIGENCE",
            "INSURANCE CLAIM",
            "CONTRACT AND INDEBTEDNESS",
            "DISTRICT COURTS – CIVIL",
            "JUSTICE OF THE PEACE – CIVIL",
        ],
        description="Case types eligible for automatic matching",
    )


class IntegrationSettings(BaseModel):
    """Guidewire ClaimCenter integration and downstream sync settings."""
    guidewire_mock_mode: bool = Field(default=True, description="Simulate Guidewire response without calling external endpoint")
    guidewire_api_url: str = Field(
        default="https://uaic-gwcp-prod-igoauthproxy.api.delta4-andromeda.guidewire.net/api/powerapps/caseupdate",
        description="Guidewire Case Update REST API endpoint URL",
    )
    guidewire_auth_type: str = Field(
        default="Bearer",
        description="Auth method: Bearer, ApiKey, Basic, OAuth2, None",
    )
    guidewire_api_key: str = Field(default="gw_demo_token_xyz890", description="Bearer token or API Key header value")
    guidewire_client_id: str = Field(default="uaic_service_account", description="Client ID / Username for Basic or OAuth2 auth")
    guidewire_client_secret: str = Field(default="sec_gw_secret_9981", description="Client Secret / Password for Basic or OAuth2 auth")
    guidewire_timeout_seconds: int = Field(default=30, ge=5, le=120, description="Guidewire HTTP timeout in seconds")
    auto_push_on_match: bool = Field(default=True, description="Automatically trigger Guidewire notification when match is confirmed")
    notification_dispatch_mode: str = Field(
        default="both",
        description="Match notification dispatch strategy: 'direct_system' (send email directly from Orchestrator), 'guidewire_activity' (push to Guidewire and trigger activity notification), or 'both' (both Guidewire push and direct system email)",
    )
    notification_email: str = Field(default="test@test.com", description="Alert email recipient for failed push notifications")


class TaskQueueSettings(BaseModel):
    """Celery task queue & operational retry limits."""
    max_task_retries: int = Field(default=3, ge=0, le=10, description="Maximum Celery task retry attempts on unhandled exceptions")
    task_retry_delay_seconds: int = Field(default=30, ge=5, le=300, description="Exponential backoff delay in seconds between task retries")
    batch_chunk_size: int = Field(default=25, ge=5, le=100, description="Number of claims to process per Celery worker chunk")
    auto_retry_failed_scrapes: bool = Field(default=True, description="Automatically retrigger failed scraping tasks via Celery Beat")
    max_concurrent_claims: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Concurrent claims scraped in parallel (1 = sequential FIFO, 2-10 = parallel multi-worker)",
    )


class ThemePalette(BaseModel):
    """Semantic theme color tokens for light or dark mode."""
    primary: str = Field(default="#4f46e5", description="Primary brand accent color")
    secondary: str = Field(default="#0ea5e9", description="Secondary brand accent color")
    accent: str = Field(default="#6366f1", description="Accent highlight color")
    background: str = Field(default="#f8fafc", description="Main page background color")
    surface: str = Field(default="#ffffff", description="Surface background color")
    card: str = Field(default="#ffffff", description="Card background color")
    header: str = Field(default="#ffffff", description="Header / Navbar background color")
    sidebar: str = Field(default="#ffffff", description="Sidebar background color")
    text: str = Field(default="#0f172a", description="Primary text color")
    text_muted: str = Field(default="#64748b", description="Muted / secondary text color")
    border: str = Field(default="#e2e8f0", description="Border color")
    divider: str = Field(default="#e2e8f0", description="Divider line color")
    input_background: str = Field(default="#f8fafc", description="Input field background color")
    input_text: str = Field(default="#0f172a", description="Input text color")
    button: str = Field(default="#4f46e5", description="Primary button background color")
    button_text: str = Field(default="#ffffff", description="Primary button text color")
    link: str = Field(default="#4f46e5", description="Hyperlink text color")
    success: str = Field(default="#10b981", description="Success state color")
    warning: str = Field(default="#f59e0b", description="Warning state color")
    error: str = Field(default="#ef4444", description="Error state color")
    info: str = Field(default="#3b82f6", description="Informational state color")
    focus: str = Field(default="#6366f1", description="Focus outline ring color")
    hover: str = Field(default="#f1f5f9", description="Hover state background color")
    active: str = Field(default="#e2e8f0", description="Active state background color")
    selected: str = Field(default="#e0e7ff", description="Selected item highlight color")
    disabled: str = Field(default="#94a3b8", description="Disabled state color")


def get_default_light_palette() -> ThemePalette:
    return ThemePalette()


def get_default_dark_palette() -> ThemePalette:
    return ThemePalette(
        primary="#6366f1",
        secondary="#38bdf8",
        accent="#818cf8",
        background="#020617",
        surface="#0f172a",
        card="#0f172a",
        header="#020617",
        sidebar="#020617",
        text="#f8fafc",
        text_muted="#94a3b8",
        border="#1e293b",
        divider="#1e293b",
        input_background="#020617",
        input_text="#f8fafc",
        button="#4f46e5",
        button_text="#ffffff",
        link="#818cf8",
        success="#10b981",
        warning="#f59e0b",
        error="#ef4444",
        info="#38bdf8",
        focus="#818cf8",
        hover="#1e293b",
        active="#334155",
        selected="#312e81",
        disabled="#64748b",
    )


class BrandingSettings(BaseModel):
    """Visual branding, identity, and application titles."""
    app_title: str = Field(default="UAIC Orchestrator", description="Application Title displayed in header and navigation")
    app_subtitle: str = Field(default="RPA & Match Engine", description="Application Subtitle or tagline")
    app_logo_url: str = Field(default="/icon.png", description="Application logo / favicon icon URL")
    badge_letter: str = Field(default="U", description="Fallback badge letter or monogram")
    theme_accent: str = Field(default="indigo", description="Primary brand accent color tone")
    light_palette: ThemePalette = Field(default_factory=get_default_light_palette, description="Light Mode semantic color palette")
    dark_palette: ThemePalette = Field(default_factory=get_default_dark_palette, description="Dark Mode semantic color palette")


class StorageSettings(BaseModel):
    """Storage provider configuration for error screenshots and failure diagnostics."""
    capture_error_screenshots: bool = Field(
        default=True,
        description="Enable/disable saving screenshots when portal scraping fails (toggle OFF to conserve storage)",
    )
    storage_provider: str = Field(
        default="local",
        description="Storage provider: local (server disk backend/screenshots/), s3 (AWS S3), azure_blob (Azure Blob), gcs (Google Cloud)",
    )
    # AWS S3 Settings
    s3_bucket_name: str = Field(default="", description="AWS S3 bucket name")
    s3_region: str = Field(default="us-east-1", description="AWS S3 region (e.g., us-east-1)")
    s3_access_key: str = Field(default="", description="AWS Access Key ID")
    s3_secret_key: str = Field(default="", description="AWS Secret Access Key")
    # Azure Blob Storage Settings
    azure_connection_string: str = Field(default="", description="Azure Blob Storage connection string")
    azure_container_name: str = Field(default="screenshots", description="Azure Blob container name")
    # Google Cloud Storage Settings
    gcs_bucket_name: str = Field(default="", description="Google Cloud Storage bucket name")
    gcs_project_id: str = Field(default="", description="GCP Project ID")
    gcs_credentials_json: str = Field(default="", description="Google Cloud Service Account JSON credentials")


class EmailSettings(BaseModel):
    """Enterprise email notification service and provider configuration."""
    email_notifications_enabled: bool = Field(default=True, description="Master toggle to enable/disable automated email notifications")
    provider: str = Field(default="local_mock", description="Email provider: local_mock, maildev, direct_mx, smtp, graph, sendgrid, ses")
    maildev_web_url: str = Field(default="http://localhost:1080", description="URL for local MailDev web interface")
    smtp_host: str = Field(default="localhost", description="SMTP server hostname or IP")
    smtp_port: int = Field(default=587, description="SMTP server port (e.g. 587, 465, 25, 1025)")
    smtp_username: str = Field(default="", description="SMTP username / email")
    smtp_password: str = Field(default="", description="SMTP password / app password (masked)")
    smtp_encryption: str = Field(default="tls", description="Encryption type: tls, ssl, none")
    from_name: str = Field(default="UAIC Claim Alerts", description="Sender display name")
    from_email: str = Field(default="notifications@test.com", description="Sender email address")
    reply_to: str = Field(default="", description="Optional reply-to email address")
    to_recipients: list[str] = Field(default_factory=lambda: ["claims-ops@test.com"], description="Default primary To recipients")
    cc_recipients: list[str] = Field(default_factory=list, description="Default CC recipients")
    bcc_recipients: list[str] = Field(default_factory=list, description="Default BCC recipients")
    timeout_seconds: int = Field(default=15, ge=2, le=60, description="Email provider connection timeout in seconds")
    retry_count: int = Field(default=3, ge=0, le=5, description="Max delivery retry attempts on transient failure")
    retry_delay_seconds: int = Field(default=30, ge=5, le=300, description="Initial retry delay in seconds")
    rules: dict[str, bool] = Field(
        default_factory=lambda: {
            "court_case_matched": True,
            "guidewire_activity_created": True,
            "guidewire_activity_failed": True,
            "scraper_failed": True,
            "claim_failed": True,
        },
        description="Per-event notification enablement rules",
    )


class SystemSettings(BaseModel):
    """Root configuration model containing all subsystem configurations."""
    automation: AutomationSettings = Field(default_factory=AutomationSettings)
    portals: PortalsSettings = Field(default_factory=PortalsSettings)
    matcher: FuzzyMatcherSettings = Field(default_factory=FuzzyMatcherSettings)
    integration: IntegrationSettings = Field(default_factory=IntegrationSettings)
    queue: TaskQueueSettings = Field(default_factory=TaskQueueSettings)
    branding: BrandingSettings = Field(default_factory=BrandingSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)


# Test Connection Request & Response DTOs
class GuidewireTestRequest(BaseModel):
    """Payload to test Guidewire connectivity from the UI."""
    api_url: str | None = None
    auth_type: str | None = None
    api_key: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    mock_mode: bool | None = None
    timeout_seconds: int | None = None
    custom_payload: dict[str, Any] | None = None


class GuidewireTestResponse(BaseModel):
    """Result of Guidewire test connection."""
    success: bool
    status_code: int
    status_text: str
    duration_ms: float
    request_url: str
    request_method: str
    request_headers: dict[str, str]
    request_body: dict[str, Any]
    response_headers: dict[str, str]
    response_body: Any
    error_detail: str | None = None


class PortalTestRequest(BaseModel):
    """Payload to ping a court portal from the UI."""
    portal_name: str
    url: str
    timeout_seconds: int | None = 10


class PortalTestResponse(BaseModel):
    """Result of court portal reachability check."""
    portal_name: str
    url: str
    reachable: bool
    status_code: int | None = None
    status_text: str
    duration_ms: float
    error_detail: str | None = None


class BrowserTestRequest(BaseModel):
    """Payload to test browser launch in Attended or Headless mode."""
    headless: bool | None = None
    browser_engine: str | None = "chromium"
    test_url: str | None = "https://example.com"
    timeout_seconds: int | None = 25
    chrome_binary_path: str | None = None
    chrome_extension_dir: str | None = None


class BrowserTestResponse(BaseModel):
    """Result of browser launch and execution test."""
    success: bool
    mode: str
    browser_engine: str = "chromium"
    headless: bool
    chrome_found: bool
    chrome_executable: str | None = None
    extension_found: bool
    extension_path: str | None = None
    extension_loaded: bool = False
    extension_id: str | None = None
    service_worker_active: bool = False
    warning: str | None = None
    page_title: str | None = None
    duration_ms: float
    message: str
    error_detail: str | None = None


class StorageTestRequest(BaseModel):
    """Payload to test storage provider connectivity and permissions."""
    storage_provider: str = "local"
    s3_bucket_name: str | None = None
    s3_region: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    azure_connection_string: str | None = None
    azure_container_name: str | None = None
    gcs_bucket_name: str | None = None
    gcs_project_id: str | None = None
    gcs_credentials_json: str | None = None


class StorageTestResponse(BaseModel):
    """Result of storage provider connectivity and permission test."""
    success: bool
    storage_provider: str
    message: str
    duration_ms: float = 0.0
    details: dict[str, Any] = Field(default_factory=dict)
    error_detail: str | None = None


# Email Notification Test DTOs
class EmailConnectionTestRequest(BaseModel):
    """Payload to test email provider connectivity and authentication."""
    provider: str = "local_mock"
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_encryption: str | None = "tls"
    timeout_seconds: int | None = 10
    recipient_domain: str | None = None


class EmailConnectionTestResponse(BaseModel):
    """Result of email provider connection test."""
    success: bool
    provider: str
    message: str
    duration_ms: float
    error_detail: str | None = None


class TestEmailSendRequest(BaseModel):
    """Payload to dispatch a live test notification email."""
    recipient: str
    subject: str | None = "UAIC Orchestrator — Test Notification"
    body: str | None = "This is a live test notification verifying the UAIC Email & Notification Engine."
    provider: str | None = None


class TestEmailSendResponse(BaseModel):
    """Result of live test email dispatch."""
    success: bool
    notification_id: str
    recipient: str
    status: str
    message: str
    duration_ms: float
    error_detail: str | None = None


class NotificationResponseSchema(BaseModel):
    """Schema for returning notification delivery records."""
    id: str
    event_type: str
    claim_id: str | None = None
    claim_number: str | None = None
    recipient: str
    cc: str | None = None
    bcc: str | None = None
    subject: str
    provider: str
    status: str
    error_message: str | None = None
    retry_count: int = 0
    created_at: str
    sent_at: str | None = None
    failed_at: str | None = None
    delivery_receipt: dict[str, Any] | None = None
    details: dict[str, Any] | None = None


class NotificationTemplateSchema(BaseModel):
    """Schema for dynamic email notification templates."""
    id: str
    name: str
    event_type: str
    subject_template: str
    body_template_html: str
    body_template_text: str | None = None
    is_active: bool = True

