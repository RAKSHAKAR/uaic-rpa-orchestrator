# UAIC — Proxy Test Endpoint + E2E Live Test Plan
## IMP-2026-0921-002 | 2026-09-21

**Implementation ID:** IMP-2026-0921-002  
**Date:** 2026-09-21  
**Status:** Awaiting User Approval  
**Scope:** Part A — Settings Proxy Test (code changes) + Part B — E2E Live Test (execution)

---

## Part A: Settings Page Proxy Test — Gap Fix

### Background

Full audit of all 21 settings endpoints and all `api.ts` functions reveals **one structural gap**:

| Feature | Backend Route | api.ts fn | UI Button |
|---|---|---|---|
| Guidewire Test | ✅ `/test-guidewire` | ✅ | ✅ |
| Portal Test | ✅ `/test-portal` | ✅ | ✅ |
| Browser Test | ✅ `/test-browser` | ✅ | ✅ |
| Fleet Test | ✅ `/test-fleet` | ✅ | ✅ |
| Storage Test | ✅ `/test-storage` | ✅ | ✅ |
| Email Test | ✅ `/email/test-connection` | ✅ | ✅ |
| AntiCaptcha Test | ✅ `/test-anticaptcha` | ✅ | ✅ |
| Extension Setup | ✅ `/setup-extension` | ✅ | ✅ |
| **Proxy Test** | ❌ **MISSING** | ❌ **MISSING** | ❌ **MISSING** |

> [!NOTE]
> Proxy configuration IS correctly saved in `SystemSettings.proxy` (host, port, username, password, enabled).
> It IS correctly passed to `ChromeSession` in both `/test-browser` and `/test-fleet` endpoints.  
> The only gap is: **no dedicated test button to verify the proxy server is reachable before starting automation.**

---

### Proposed Changes

---

#### FILE 1 — [MODIFY] [`backend/app/schemas/settings.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py)

**Insertion point:** After line 544 (end of `StorageTestResponse` class), add:

```python
class ProxyTestRequest(BaseModel):
    """Request to test proxy server connectivity."""
    host: str = Field(description="Proxy server hostname or IP address")
    port: int = Field(default=3128, description="Proxy server port number")
    username: str | None = Field(default=None, description="Proxy authentication username (optional)")
    password: str | None = Field(default=None, description="Proxy authentication password (optional)")
    test_url: str = Field(
        default="https://www.browardclerk.org/",
        description="Target URL to reach through the proxy (default: Broward court portal)"
    )
    timeout_seconds: float = Field(default=15.0, description="Request timeout in seconds")


class ProxyTestResponse(BaseModel):
    """Result of proxy server connectivity test."""
    success: bool = Field(description="True if proxy is reachable and returned HTTP response")
    host: str = Field(description="Proxy host that was tested")
    port: int = Field(description="Proxy port that was tested")
    authenticated: bool = Field(description="True if authentication credentials were provided")
    test_url: str = Field(description="URL that was requested through the proxy")
    http_status: int | None = Field(default=None, description="HTTP status code returned through proxy")
    duration_ms: float = Field(description="Round-trip latency in milliseconds")
    message: str = Field(description="Human-readable result summary")
    error_detail: str | None = Field(default=None, description="Error message if test failed")
```

---

#### FILE 2 — [MODIFY] [`backend/app/api/v1/endpoints/settings.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/api/v1/endpoints/settings.py)

**Change 1 — Import block** (around line 30–50, add `ProxyTestRequest, ProxyTestResponse` to schema imports):

```python
from app.schemas.settings import (
    BrandingSettings,
    BrowserTestRequest,
    BrowserTestResponse,
    EmailConnectionTestRequest,
    EmailConnectionTestResponse,
    ExtensionSetupResponse,
    FleetTestRequest,
    FleetTestResponse,
    FleetWorkerResult,
    GuidewireTestRequest,
    GuidewireTestResponse,
    PortalTestRequest,
    PortalTestResponse,
    ProxyTestRequest,      # NEW
    ProxyTestResponse,     # NEW
    StorageTestRequest,
    StorageTestResponse,
    SystemSettings,
    TestEmailSendRequest,
    TestEmailSendResponse,
)
```

**Change 2 — New endpoint** (insert after line 851, the `test-storage` endpoint):

```python
@router.post("/test-proxy", response_model=ProxyTestResponse, summary="Test Proxy Server Connectivity")
async def test_proxy_endpoint(req: ProxyTestRequest):
    """
    Tests HTTP connectivity through the configured proxy server by attempting to
    reach a known target URL (default: Broward county court portal).
    Returns HTTP status, authentication state, and round-trip latency.
    Validates the proxy is reachable and correctly routing traffic before enabling
    it for automated county court scraping sessions.
    """
    proxy_url = f"http://{req.host}:{req.port}"
    authenticated = bool(req.username and req.password)

    t0 = time.perf_counter()
    try:
        proxies = {"http://": proxy_url, "https://": proxy_url}
        auth = httpx.BasicAuth(req.username, req.password) if authenticated else None

        async with httpx.AsyncClient(
            proxies=proxies,
            auth=auth,
            timeout=req.timeout_seconds,
            verify=False,  # Court sites may have self-signed certs
            follow_redirects=True,
        ) as client:
            response = await client.get(req.test_url)
            dur_ms = round((time.perf_counter() - t0) * 1000, 1)
            auth_note = " (authenticated)" if authenticated else ""
            return ProxyTestResponse(
                success=True,
                host=req.host,
                port=req.port,
                authenticated=authenticated,
                test_url=req.test_url,
                http_status=response.status_code,
                duration_ms=dur_ms,
                message=f"Proxy reachable{auth_note}. HTTP {response.status_code} via {proxy_url} in {dur_ms}ms.",
            )
    except Exception as e:
        dur_ms = round((time.perf_counter() - t0) * 1000, 1)
        err = f"{type(e).__name__}: {e}"
        logger.warning(f"Proxy connectivity test failed for {proxy_url}: {err}")
        return ProxyTestResponse(
            success=False,
            host=req.host,
            port=req.port,
            authenticated=authenticated,
            test_url=req.test_url,
            http_status=None,
            duration_ms=dur_ms,
            message=f"Proxy connection failed: {err}",
            error_detail=err,
        )
```

---

#### FILE 3 — [MODIFY] [`frontend/src/types/index.ts`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts)

**Insertion point:** After line 418 (end of `StorageTestResponse` interface), add:

```typescript
export interface ProxyTestRequest {
  host: string;
  port: number;
  username?: string | null;
  password?: string | null;
  test_url?: string;
  timeout_seconds?: number;
}

export interface ProxyTestResponse {
  success: boolean;
  host: string;
  port: number;
  authenticated: boolean;
  test_url: string;
  http_status?: number | null;
  duration_ms: number;
  message: string;
  error_detail?: string | null;
}
```

---

#### FILE 4 — [MODIFY] [`frontend/src/lib/api.ts`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/lib/api.ts)

**Change 1 — Import block** (add `ProxyTestRequest, ProxyTestResponse` to the import list from `"../types"`):

```typescript
import {
  // ... existing imports ...
  StorageTestRequest,
  StorageTestResponse,
  ProxyTestRequest,        // NEW
  ProxyTestResponse,       // NEW
  // ... rest of imports ...
} from "../types";
```

**Change 2 — New API function** (add after `testStorageConnection` around line 512):

```typescript
  testProxyConnection: async (payload: ProxyTestRequest): Promise<ProxyTestResponse> => {
    const res = await apiClient.post("/settings/test-proxy", payload);
    return res.data;
  },
```

---

#### FILE 5 — [MODIFY] [`frontend/src/app/settings/page.tsx`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)

**Change 1 — Add types import** (add `ProxyTestRequest, ProxyTestResponse` to the type import at the top of the file).

**Change 2 — State variables** (add after line 181, after `browserTestResult` state):

```tsx
// Proxy connectivity test states
const [isTestingProxy, setIsTestingProxy] = useState(false);
const [proxyTestResult, setProxyTestResult] = useState<ProxyTestResponse | null>(null);
```

**Change 3 — Handler function** (add near other `handleTest*` handler functions):

```tsx
const handleTestProxy = async () => {
  if (!settings?.proxy?.host?.trim()) {
    setFeedback({ type: "error", msg: "Enter a Proxy Host / IP address before testing." });
    return;
  }
  setIsTestingProxy(true);
  setProxyTestResult(null);
  try {
    const result = await api.testProxyConnection({
      host: settings.proxy.host,
      port: settings.proxy.port || 3128,
      username: settings.proxy.username || null,
      password: settings.proxy.password || null,
    });
    setProxyTestResult(result);
  } catch (e: any) {
    setProxyTestResult({
      success: false,
      host: settings?.proxy?.host || "",
      port: settings?.proxy?.port || 3128,
      authenticated: !!(settings?.proxy?.username && settings?.proxy?.password),
      test_url: "https://www.browardclerk.org/",
      duration_ms: 0,
      message: e?.response?.data?.detail || e?.message || "Request failed",
      error_detail: String(e),
    });
  } finally {
    setIsTestingProxy(false);
  }
};
```

**Change 4 — Proxy tab UI** (replace current proxy tab content at lines 4258–4361 with the enhanced version that adds the Test button and result card):

```tsx
{activeTab === "proxy" && (
  <div className="space-y-6 w-full">
    {/* Header banner */}
    <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-6 text-white shadow-lg shadow-slate-900/20">
      <div className="flex items-center gap-3 mb-2">
        <Network className="w-6 h-6 text-slate-300" />
        <h3 className="text-xl font-bold">Proxy Pool Settings</h3>
      </div>
      <p className="text-sm text-slate-300 max-w-2xl">
        Configure a dedicated proxy server to route all automation traffic through.
        This helps distribute requests and avoid IP bans from county court portals.
      </p>
    </div>

    {/* Connection details card */}
    <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
      <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800/80">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-indigo-500" />
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">Proxy Connection Details</h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Configure and validate your proxy server before enabling automation traffic routing.
            </p>
          </div>
        </div>
        {/* Test Proxy Button — only shown when enabled and host is set */}
        {settings?.proxy?.enabled && settings?.proxy?.host && (
          <button
            type="button"
            onClick={handleTestProxy}
            disabled={isTestingProxy}
            className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition-all cursor-pointer inline-flex items-center gap-2 shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isTestingProxy ? "animate-spin" : ""}`} />
            {isTestingProxy ? "Testing Proxy..." : "Test Proxy Connection"}
          </button>
        )}
      </div>

      <div className="space-y-6 w-full">
        {/* Enable toggle */}
        <label className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-800 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors w-full">
          <input
            type="checkbox"
            checked={settings?.proxy?.enabled ?? false}
            onChange={(e) =>
              setSettings({
                ...settings,
                proxy: { ...(settings?.proxy || { host: "", port: 3128 }), enabled: e.target.checked },
              } as SystemSettings)
            }
            className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
          />
          <div className="flex-1">
            <div className="text-sm font-medium text-slate-900 dark:text-slate-100">Enable Proxy Server</div>
            <div className="text-xs text-slate-500">Route all scraping traffic through this proxy</div>
          </div>
        </label>

        {settings?.proxy?.enabled && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
            {/* Host */}
            <div className="w-full">
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Proxy Host / IP</label>
              <input
                type="text"
                value={settings?.proxy?.host || ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    proxy: { ...(settings?.proxy || {}), host: e.target.value },
                  } as SystemSettings)
                }
                placeholder="e.g. 192.168.1.50 or proxy.example.com"
                className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
              />
            </div>
            {/* Port */}
            <div className="w-full">
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Port</label>
              <input
                type="number"
                value={settings?.proxy?.port || 3128}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    proxy: { ...(settings?.proxy || {}), port: parseInt(e.target.value) || 3128 },
                  } as SystemSettings)
                }
                className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
              />
            </div>
            {/* Username */}
            <div className="w-full">
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Username (Optional)</label>
              <input
                type="text"
                value={settings?.proxy?.username || ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    proxy: { ...(settings?.proxy || {}), username: e.target.value },
                  } as SystemSettings)
                }
                placeholder="Proxy Username"
                className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
              />
            </div>
            {/* Password */}
            <div className="w-full">
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">Password (Optional)</label>
              <input
                type="password"
                value={settings?.proxy?.password || ""}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    proxy: { ...(settings?.proxy || {}), password: e.target.value },
                  } as SystemSettings)
                }
                placeholder="Proxy Password"
                className="w-full text-sm px-3 py-2 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>
        )}
      </div>

      {/* Proxy Test Result Card */}
      {proxyTestResult && (
        <div className={`mt-4 p-4 rounded-xl border text-xs space-y-2 ${
          proxyTestResult.success
            ? "bg-emerald-500/10 border-emerald-500/30 dark:bg-emerald-950/20 dark:border-emerald-800/50"
            : "bg-rose-500/10 border-rose-500/30 dark:bg-rose-950/20 dark:border-rose-800/50"
        }`}>
          <div className="flex items-center gap-2 font-bold">
            {proxyTestResult.success
              ? <CheckCircle className="w-4 h-4 text-emerald-500" />
              : <AlertTriangle className="w-4 h-4 text-rose-500" />
            }
            <span className={proxyTestResult.success ? "text-emerald-700 dark:text-emerald-300" : "text-rose-700 dark:text-rose-300"}>
              {proxyTestResult.success ? "Proxy Reachable" : "Proxy Connection Failed"}
            </span>
            <span className="ml-auto font-mono text-slate-500 dark:text-slate-400">
              {proxyTestResult.duration_ms}ms
            </span>
          </div>
          <p className="text-slate-700 dark:text-slate-300">{proxyTestResult.message}</p>
          {proxyTestResult.http_status && (
            <div className="font-mono text-slate-500 dark:text-slate-400">
              HTTP {proxyTestResult.http_status} · via {proxyTestResult.host}:{proxyTestResult.port}
              {proxyTestResult.authenticated ? " (authenticated)" : " (no auth)"}
            </div>
          )}
          {proxyTestResult.error_detail && (
            <pre className="mt-1 p-2 bg-rose-950/30 rounded text-[10px] text-rose-300 overflow-x-auto whitespace-pre-wrap">
              {proxyTestResult.error_detail}
            </pre>
          )}
        </div>
      )}
    </div>

    {/* Info callout when proxy is disabled */}
    {!settings?.proxy?.enabled && (
      <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/30 text-xs text-slate-500 dark:text-slate-400 flex items-start gap-2">
        <Network className="w-4 h-4 mt-0.5 shrink-0 text-slate-400" />
        <span>
          Proxy routing is <strong>disabled</strong>. Scraper bots will use your direct internet connection.
          Enable the proxy above to route all Playwright traffic through a dedicated proxy server.
        </span>
      </div>
    )}
  </div>
)}
```

---

### Verification Plan — Part A

```bash
# Backend
cd backend
.venv\Scripts\pytest --tb=short -q           # 453 tests must pass
.venv\Scripts\ruff check app tests           # 0 errors

# Frontend
cd frontend
npx tsc --noEmit                             # 0 TypeScript errors
npm run lint                                 # 0 errors
npm run build                                # build succeeds
```

**Manual UI checks:**
1. Settings → Proxy tab → Enable proxy → enter `127.0.0.1:3128` → "Test Proxy" button appears
2. Click "Test Proxy" → spinner → result card renders (success green OR failure red)
3. Enter invalid host → error_detail card renders cleanly
4. Both Light and Dark mode verified
5. Save settings → proxy host/port/auth persists in DB
6. Settings → Automation → Test Fleet → confirm proxy is forwarded to ChromeSession (verify in backend logs)

---

## Part B: E2E Live Test Plan

> [!IMPORTANT]
> This plan supersedes `2026-09-21_uaic_e2e_live_test_plan_v1.md` which contained stale assumptions (empty settings DB).  
> Per user confirmation: Settings ARE configured, Celery worker IS running, DB was cleaned to 0 claims.

### Current System State (Confirmed)
| Component | Status |
|-----------|--------|
| FastAPI (8000) | ✅ Running |
| Next.js (3000) | ✅ Running |
| Redis (6379) | ✅ Running |
| Celery Worker | ✅ Running |
| Settings DB | ✅ Configured (AntiCaptcha key, mock mode, etc.) |
| Claims DB | ✅ Cleaned (0 records) |

### Test Files
| File | Location |
|------|----------|
| `sample_claims - Florida.xlsx` | `Testing files\sample_claims - Florida.xlsx` |
| `5RecordsTexas.xlsx` | `Testing files\5RecordsTexas.xlsx` |

---

### Phase 0 — Pre-Flight Verification (browser subagent)

1. Navigate `http://localhost:3000/settings`
2. **Guidewire tab** → confirm Mock Simulation Mode is ON → click "Test Guidewire" → must pass
3. **Automation tab** → confirm AntiCaptcha key is set → click "Test AntiCaptcha Balance" → verify balance
4. **Automation tab** → Parallel Fleet = **1** for Phase 1
5. **Browser test** → Headless → confirm Chrome launches
6. Navigate `http://localhost:3000/health` → all services green

---

### Phase 1 — Florida Upload + Fleet=1 Extraction

1. Navigate `http://localhost:3000/upload`
2. Upload `Testing files\sample_claims - Florida.xlsx`
3. Verify preview: DOL dates, claimant names, FL state
4. Import → claims enter DB as `NEW`
5. Dashboard → select all Florida claims → **Bulk Start**
6. Fleet=1: 1 browser at a time; watch sequential processing
7. Monitor `/monitor` queue
8. Post-extraction: review claim details (Broward/Hillsborough/Miami JSON)
9. Guidewire push (Mock mode): status → `COMPLETED`

---

### Phase 2 — Texas Upload + Fleet=2 Extraction

1. Settings → Automation → change Fleet to **2** → Save
2. Upload `Testing files\5RecordsTexas.xlsx`
3. Verify 5 TX claims imported
4. Dashboard → Bulk Start all Texas claims
5. Fleet=2: 2 browsers open simultaneously
6. Verify claim 3–5 remain `NEW` until slot opens
7. Portal coverage: Harris Clerk + Dallas + Harris JP + Harris District + Travis (5 portals)
8. Guidewire push (Mock mode) for completed claims

---

### Success Criteria

| Criterion | Expected |
|-----------|----------|
| Florida claims processed | All complete or manual review |
| Texas claims processed | All complete or manual review |
| Fleet=1 isolation | Max 1 `SCRAPING_IN_PROGRESS` at any time |
| Fleet=2 concurrency | Exactly 2 `SCRAPING_IN_PROGRESS` simultaneously |
| Portal routing FL | Broward + Hillsborough + Miami only |
| Portal routing TX | Harris Clerk + Dallas + Harris JP + Harris District + Travis |
| Guidewire mock push | `200 OK` with `{"status": "mock_success"}` |
| Claim number rule | 9-digit claim gets `0` prefix in payload |
| DOL date format | `MM/dd/yyyy` stored correctly |

---

### Recordings & Evidence
- Browser recording saved to `implementation_plan/Recording/`
- Screenshots saved to `implementation_plan/Images/`
- Backend logs captured inline

---

## Execution Order

```
Part A: Code changes (5 files, ~2 min)
  ↓
Run: pytest + ruff + tsc + lint (validation)
  ↓
Part B: E2E Live Test (browser subagent)
  Phase 0: Pre-flight → Settings verification
  Phase 1: Florida upload → Fleet=1 → extraction → Guidewire mock
  Phase 2: Texas upload → Fleet=2 → extraction → Guidewire mock
  ↓
Implementation Record saved to implementation_plan/
```

---

*Saved: 2026-09-21 | IMP-2026-0921-002*
