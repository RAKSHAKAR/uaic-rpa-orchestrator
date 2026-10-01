"""Portal reachability checks use the same configured proxy egress as RPA."""

from unittest.mock import AsyncMock

import httpx
import pytest

from app.api.v1.endpoints import health
from app.schemas.settings import PortalTestRequest, ProxySettings, SystemSettings
from app.services import guidewire_client


class _PortalClient:
    def __init__(self, response: httpx.Response, *, error: Exception | None = None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def head(self, _url: str):
        if self.error:
            raise self.error
        return self.response

    async def get(self, _url: str, **_kwargs):
        if self.error:
            raise self.error
        return self.response


@pytest.mark.asyncio
@pytest.mark.parametrize("diagnostic", ["health", "settings"])
@pytest.mark.parametrize("enabled", [False, True])
async def test_portal_diagnostic_honors_configured_proxy(monkeypatch, diagnostic, enabled):
    proxy = ProxySettings(
        enabled=enabled,
        host="proxy.example" if enabled else "",
        port=3128,
        username="alice" if enabled else "",
        password="p@ss:word" if enabled else "",
    )
    runtime = SystemSettings(proxy=proxy)
    expected_proxy = "http://alice:p%40ss%3Aword@proxy.example:3128" if enabled else None
    captured: list[dict] = []
    response = httpx.Response(200, request=httpx.Request("GET", "https://www.browardclerk.org/Web2"))

    def client_factory(**kwargs):
        captured.append(kwargs)
        return _PortalClient(response)

    module = health if diagnostic == "health" else guidewire_client
    monkeypatch.setattr(module, "get_system_settings_async", AsyncMock(return_value=runtime))
    monkeypatch.setattr(module.httpx, "AsyncClient", client_factory)

    if diagnostic == "health":
        result = await health.ping_portal_endpoint("broward")
        assert result["reachable"] is True
    else:
        request = PortalTestRequest(portal_name="Broward", url="https://www.browardclerk.org/Web2")
        result = await guidewire_client.test_court_portal(request)
        assert result.reachable is True

    assert captured[0]["proxy"] == expected_proxy
    assert captured[0]["trust_env"] is False


@pytest.mark.asyncio
@pytest.mark.parametrize("diagnostic", ["health", "settings"])
async def test_portal_diagnostic_error_hides_proxy_password(monkeypatch, diagnostic):
    proxy = ProxySettings(enabled=True, host="proxy.example", password="top-secret")
    runtime = SystemSettings(proxy=proxy)
    response = httpx.Response(200, request=httpx.Request("GET", "https://www.browardclerk.org/Web2"))

    def client_factory(**_kwargs):
        return _PortalClient(response, error=httpx.ConnectError("proxy credential top-secret rejected"))

    module = health if diagnostic == "health" else guidewire_client
    monkeypatch.setattr(module, "get_system_settings_async", AsyncMock(return_value=runtime))
    monkeypatch.setattr(module.httpx, "AsyncClient", client_factory)

    if diagnostic == "health":
        result = await health.ping_portal_endpoint("broward")
        assert result["reachable"] is False
        detail = result["error"]
    else:
        request = PortalTestRequest(portal_name="Broward", url="https://www.browardclerk.org/Web2")
        result = await guidewire_client.test_court_portal(request)
        assert result.reachable is False
        detail = result.error_detail

    assert "top-secret" not in detail
