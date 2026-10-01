"""Configured network egress for public court portal diagnostics."""

from urllib.parse import quote

from app.schemas.settings import ProxySettings


def portal_proxy_url(proxy: ProxySettings) -> str | None:
    """Return the configured HTTP proxy URL, including encoded authentication."""
    if not proxy.enabled:
        return None
    if not proxy.host:
        raise ValueError("Enabled proxy is missing a host")

    authority = f"{proxy.host}:{proxy.port}"
    if proxy.username or proxy.password:
        username = quote(proxy.username, safe="")
        password = quote(proxy.password, safe="")
        authority = f"{username}:{password}@{authority}"
    return f"http://{authority}"
