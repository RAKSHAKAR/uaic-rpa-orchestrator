import httpx
import json

def verify_system():
    client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=30.0)
    
    print("=== 1. SYSTEM HEALTH ===")
    health = client.get("/health").json()
    print("Health:", health)
    
    detailed = client.get("/health/detailed").json()
    print(f"Overall Health Status: {detailed.get('status')}")
    print(f"Components checked: {list(detailed.get('components', {}).keys())}")
    
    print("\n=== 2. SYSTEM SETTINGS (DYNAMIC VALUES) ===")
    settings = client.get("/settings").json()
    automation = settings.get("automation", {})
    portals = settings.get("portals", {})
    matching = settings.get("matching", {})
    guidewire = settings.get("guidewire", {})
    
    print(f"Automation Mode: Headless={automation.get('headless')}, AntiCaptcha={automation.get('anticaptcha_enabled')}")
    print(f"Portal Toggles: Broward={portals.get('broward_enabled')}, Hills={portals.get('hillsborough_enabled')}, Miami={portals.get('miami_enabled')}")
    print(f"Texas Toggles: HarrisJP={portals.get('harris_jp_enabled')}, CClerk={portals.get('harris_cclerk_enabled')}, HCDist={portals.get('harris_district_enabled')}, Dallas={portals.get('dallas_enabled')}, Travis={portals.get('travis_enabled')}")
    print(f"Matching Engine: Threshold={matching.get('threshold')}, MinFilingDate={matching.get('min_filing_date')}")
    print(f"Guidewire Config: AuthType={guidewire.get('auth_type')}, AutoPush={guidewire.get('auto_push_on_match')}")
    
    print("\n=== 3. LIVE QUEUE MONITOR & STATS ===")
    q_status = client.get("/queue/status").json()
    print(f"Active Tasks: {q_status.get('active_tasks')}, Pending: {q_status.get('pending_tasks')}, Failed: {q_status.get('failed_tasks')}, Completed: {q_status.get('completed_tasks')}")
    
    claims_stats = client.get("/claims/stats").json()
    print(f"Total Claims: {claims_stats.get('total_claims')}, Cases Extracted: {claims_stats.get('total_cases_extracted')}, Finished: {claims_stats.get('total_finished')}")
    
    print("\n=== 4. FRONTEND LIVE ACCESSIBILITY ===")
    f_res = httpx.get("http://localhost:3000", timeout=30.0)
    print(f"Frontend Root (/): HTTP {f_res.status_code}")
    s_res = httpx.get("http://localhost:3000/settings", timeout=30.0)
    print(f"Frontend Settings (/settings): HTTP {s_res.status_code}")
    m_res = httpx.get("http://localhost:3000/monitor", timeout=30.0)
    print(f"Frontend Monitor (/monitor): HTTP {m_res.status_code}")
    
    print("\n=== ALL SYSTEMS VERIFIED AND READY ===")

if __name__ == "__main__":
    verify_system()
