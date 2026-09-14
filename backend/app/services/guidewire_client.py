"""Guidewire Activity Creation, Live Test Connection, and Portal Ping Client."""

import base64
import logging
import time
import uuid
from typing import Any

import httpx

from app.core.config import settings
from app.core.http_client import HTTPClient
from app.schemas.settings import (
    GuidewireTestRequest,
    GuidewireTestResponse,
    PortalTestRequest,
    PortalTestResponse,
)

logger = logging.getLogger("uaic_orchestrator.guidewire_client")


def format_claim_number(claim_num: str) -> str:
    """If claim number is 9 digits, prefix with '0' as required by legacy Guidewire integration."""
    clean = str(claim_num).strip()
    if len(clean) == 9:
        return f"0{clean}"
    return clean


class GuidewireClient:
    """Async HTTP Client for posting verified court match activity records to Guidewire."""

    def __init__(
        self,
        api_url: str | None = None,
        auth_type: str = "Bearer",
        api_key: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: float = 30.0,
        mock_mode: bool = True,
    ):
        self.api_url = api_url or getattr(settings, "GUIDEWIRE_API_URL", "https://api.guidewire.example.com/cc/rest/v1/caseupdate")
        self.auth_type = auth_type or "Bearer"
        self.api_key = api_key or getattr(settings, "GUIDEWIRE_API_KEY", "")
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""
        self.timeout = timeout
        self.mock_mode = mock_mode

    def _build_headers(self) -> dict[str, str]:
        """Build request headers according to configured authentication type."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "UAIC-Claim-Orchestrator/2.0",
        }

        if self.auth_type == "Bearer" and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.auth_type == "ApiKey" and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.auth_type == "Basic" and self.client_id and self.client_secret:
            token = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        elif self.auth_type == "OAuth2" and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def send_case_update(
        self,
        claim_number: str,
        exposure_number: str | None,
        matched_cases: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Sends formatted match payload to Guidewire caseupdate endpoint."""
        formatted_claim_num = format_claim_number(claim_number)
        
        # Build normalized CaseItems
        case_items = []
        for case in matched_cases:
            case_items.append({
                "CaseNumber": case.get("CaseNumber") or case.get("case_number") or "",
                "CaseStyle": case.get("CaseStyle") or case.get("case_style") or "",
                "CountyWebsite": case.get("CountyWebsite") or case.get("county_website") or "",
                "SuitFiledDate": case.get("SuitFiledDate") or case.get("filing_date") or "",
            })

        payload = {
            "TransactionId": str(uuid.uuid4()),
            "SourceSystem": "UAIC_ORCHESTRATOR",
            "ClaimNumber": formatted_claim_num,
            "ExposureNumber": exposure_number or "",
            "CaseItems": case_items,
        }

        if self.mock_mode:
            logger.info(f"[MOCK] Guidewire case update simulated for Claim {formatted_claim_num}")
            return {
                "success": True,
                "status_code": 200,
                "response": {
                    "status": "success",
                    "mock": True,
                    "activityId": f"MOCK-ACT-{int(time.time())}",
                    "claimNumber": formatted_claim_num,
                    "message": "Activity successfully registered in simulated Guidewire ClaimCenter.",
                },
                "payload_sent": payload,
            }

        headers = self._build_headers()
        logger.info(f"Sending Guidewire case update for Claim {formatted_claim_num} ({len(case_items)} cases)")

        client = HTTPClient.get_client(timeout=self.timeout)
        try:
            response = await client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json() if response.content else {"status": "success"}
            logger.info(f"Guidewire case update succeeded for Claim {formatted_claim_num}: {result}")
            return {
                "success": True,
                "status_code": response.status_code,
                "response": result,
                "payload_sent": payload,
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Guidewire HTTP error {e.response.status_code}: {e.response.text}")
            return {
                "success": False,
                "status_code": e.response.status_code,
                "error": str(e),
                "response_body": e.response.text,
                "payload_sent": payload,
            }
        except Exception as e:
            logger.error(f"Guidewire request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "payload_sent": payload,
            }

    async def test_connection(self, request_data: GuidewireTestRequest | None = None) -> GuidewireTestResponse:
        """Interactive Swagger-style Guidewire API tester."""
        url = (request_data.api_url if request_data and request_data.api_url else self.api_url).strip()
        auth_type = request_data.auth_type if request_data and request_data.auth_type else self.auth_type
        api_key = request_data.api_key if request_data and request_data.api_key is not None else self.api_key
        client_id = request_data.client_id if request_data and request_data.client_id is not None else self.client_id
        client_secret = request_data.client_secret if request_data and request_data.client_secret is not None else self.client_secret
        mock_mode = request_data.mock_mode if request_data and request_data.mock_mode is not None else self.mock_mode
        timeout = float(request_data.timeout_seconds or self.timeout)

        # Preset test payload if none provided
        test_payload = (
            request_data.custom_payload
            if request_data and request_data.custom_payload
            else {
                "ClaimNumber": "0100234567",
                "ExposureNumber": "1",
                "CaseItems": [
                    {
                        "CaseNumber": "COCE-23-019482",
                        "CaseStyle": "JOHN DOE VS JANE SMITH",
                        "CountyWebsite": "https://www.browardclerk.org/Web2/",
                        "SuitFiledDate": "2023-05-14",
                    }
                ],
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "UAIC-Claim-Orchestrator/2.0",
        }
        masked_headers = dict(headers)

        if auth_type == "Bearer" and api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            masked_headers["Authorization"] = f"Bearer {api_key[:4]}***{api_key[-4:] if len(api_key) > 8 else ''}"
        elif auth_type == "ApiKey" and api_key:
            headers["X-API-Key"] = api_key
            masked_headers["X-API-Key"] = f"{api_key[:4]}***{api_key[-4:] if len(api_key) > 8 else ''}"
        elif auth_type == "Basic" and client_id and client_secret:
            token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
            masked_headers["Authorization"] = f"Basic {client_id}:******"

        start_time = time.perf_counter()

        if mock_mode:
            duration_ms = round((time.perf_counter() - start_time) * 1000 + 35.2, 2)
            mock_body = {
                "status": "success",
                "mode": "MOCK_SIMULATION",
                "transactionId": f"GW-TEST-{int(time.time())}",
                "activityId": "act_test_98371290",
                "claimNumber": test_payload.get("ClaimNumber", "0100234567"),
                "statusMessage": "Guidewire simulated connection verified successfully. Activity ready to attach.",
                "responseHeaders": {
                    "content-type": "application/json; charset=utf-8",
                    "server": "Guidewire-ClaimCenter-Mock/10.0",
                    "x-request-id": f"req-{int(time.time() * 1000)}",
                },
            }
            return GuidewireTestResponse(
                success=True,
                status_code=200,
                status_text="200 OK (Mock Simulation)",
                duration_ms=duration_ms,
                request_url=url,
                request_method="POST",
                request_headers=masked_headers,
                request_body=test_payload,
                response_headers={
                    "Content-Type": "application/json",
                    "Server": "Guidewire-ClaimCenter-Mock",
                    "X-Simulation-Mode": "active",
                },
                response_body=mock_body,
                error_detail=None,
            )

        # Real Live Request
        try:
            client = HTTPClient.get_client(timeout=timeout)
            res = await client.post(url, json=test_payload, headers=headers)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            try:
                resp_body = res.json()
            except Exception:
                resp_body = res.text

            res_headers = {k: v for k, v in res.headers.items()}
            is_ok = 200 <= res.status_code < 300

            return GuidewireTestResponse(
                success=is_ok,
                status_code=res.status_code,
                status_text=f"{res.status_code} {res.reason_phrase or 'Response'}",
                duration_ms=duration_ms,
                request_url=url,
                request_method="POST",
                request_headers=masked_headers,
                request_body=test_payload,
                response_headers=res_headers,
                response_body=resp_body,
                error_detail=None if is_ok else f"HTTP Status {res.status_code}",
            )
        except httpx.ConnectError as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return GuidewireTestResponse(
                success=False,
                status_code=0,
                status_text="Connection Refused / Network Error",
                duration_ms=duration_ms,
                request_url=url,
                request_method="POST",
                request_headers=masked_headers,
                request_body=test_payload,
                response_headers={},
                response_body={"error": f"Failed to connect to host: {e!s}"},
                error_detail=str(e),
            )
        except httpx.TimeoutException as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return GuidewireTestResponse(
                success=False,
                status_code=408,
                status_text="408 Request Timeout",
                duration_ms=duration_ms,
                request_url=url,
                request_method="POST",
                request_headers=masked_headers,
                request_body=test_payload,
                response_headers={},
                response_body={"error": f"Request timed out after {timeout} seconds"},
                error_detail=str(e),
            )
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return GuidewireTestResponse(
                success=False,
                status_code=500,
                status_text="500 Internal Test Error",
                duration_ms=duration_ms,
                request_url=url,
                request_method="POST",
                request_headers=masked_headers,
                request_body=test_payload,
                response_headers={},
                response_body={"error": str(e)},
                error_detail=str(e),
            )


async def test_court_portal(request_data: PortalTestRequest) -> PortalTestResponse:
    """Tests connectivity to a public county clerk court portal."""
    url = request_data.url.strip()
    timeout = float(request_data.timeout_seconds)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    start = time.perf_counter()
    try:
        client = HTTPClient.get_client(timeout=timeout)
        res = await client.get(url, headers=headers, follow_redirects=True)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        is_reachable = res.status_code < 500

        return PortalTestResponse(
            portal_name=request_data.portal_name,
            url=url,
            reachable=is_reachable,
            status_code=res.status_code,
            status_text=f"{res.status_code} {res.reason_phrase or 'OK'}",
            duration_ms=duration_ms,
            error_detail=None if is_reachable else f"Server error: {res.status_code}",
        )
    except httpx.ConnectError as e:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return PortalTestResponse(
            portal_name=request_data.portal_name,
            url=url,
            reachable=False,
            status_code=0,
            status_text="Host Unreachable",
            duration_ms=duration_ms,
            error_detail=str(e),
        )
    except httpx.TimeoutException:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return PortalTestResponse(
            portal_name=request_data.portal_name,
            url=url,
            reachable=False,
            status_code=408,
            status_text="Connection Timeout",
            duration_ms=duration_ms,
            error_detail=f"Timed out after {timeout} seconds",
        )
    except Exception as e:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        return PortalTestResponse(
            portal_name=request_data.portal_name,
            url=url,
            reachable=False,
            status_code=500,
            status_text="Request Error",
            duration_ms=duration_ms,
            error_detail=str(e),
        )
