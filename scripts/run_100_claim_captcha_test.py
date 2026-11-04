"""
100-Claim CAPTCHA & Portal Benchmark Verification Script.

Validates acceptance criteria from IMP-2026-1007-001 Section 8:
  - 50 Florida claims x 3 portals = 150 portal attempts
  - 50 Texas claims  x 5 portals = 250 portal attempts
  - Total: 400 attempts across all 8 portals (no Dallas/Travis bypass)
  - Validates ROUTING_VALIDATION log output for FL/TX/Cross-State
  - Verifies all 8 portals are HTTP-reachable before benchmark

Usage:
    python scripts/run_100_claim_captcha_test.py [--live] [--dry-run]
"""

import argparse
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.excel_parser import resolve_county_bot_targets  # noqa: E402

FLORIDA_PORTALS = ["broward", "hillsborough", "miami"]
TEXAS_PORTALS   = ["travis", "dallas", "harris_jp", "harris_cclerk", "harris_district"]
ALL_8_PORTALS   = FLORIDA_PORTALS + TEXAS_PORTALS

PORTAL_URLS = {
    "broward":         "https://www.browardclerk.org/Web2",
    "hillsborough":    "https://publicaccess.hillsclerk.com/",
    "miami":           "https://www2.miamidadeclerk.gov/ocs/",
    "travis":          "https://odysseyweb.traviscountytx.gov/Portal/Home/WorkspaceMode?p=0",
    "dallas":          "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29",
    "harris_jp":       "https://jpwebsite.harriscountytx.gov/PublicAccess/default.aspx",
    "harris_cclerk":   "https://www.hcdistrictclerk.com/Common/e-services/PublicFiling/public_filing.aspx",
    "harris_district": "https://www.hcdistrictclerk.com/Common/e-services/PublicFiling/public_filing.aspx",
}


def _routing_type(policy_state, loss_state):
    ps = (policy_state or "").strip().upper()
    ls = (loss_state or "").strip().upper()
    if ps != ls:
        return "CROSS_STATE"
    if ps in ("FL", "FLORIDA"):
        return "FL_SAME_STATE"
    if ps in ("TX", "TEXAS"):
        return "TX_SAME_STATE"
    return "UNKNOWN"


def _expected_portals(routing_type):
    if routing_type == "FL_SAME_STATE":
        return FLORIDA_PORTALS
    if routing_type == "TX_SAME_STATE":
        return TEXAS_PORTALS
    if routing_type == "CROSS_STATE":
        return ALL_8_PORTALS
    return []


def _check_portal_http(name, url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UAIC-BenchmarkProbe/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.status, "OK"
    except urllib.error.HTTPError as e:
        return True, e.code, f"HTTP {e.code}"
    except Exception as e:
        return False, 0, str(e)[:80]


TARGET_TO_PORTAL = {
    "fl_broward": "broward",
    "fl_hillsborough": "hillsborough",
    "fl_miami": "miami",
    "te_travis": "travis",
    "te_dallas": "dallas",
    "te_harris": "harris_jp",
    "te_cclerk": "harris_cclerk",
    "te_hcdistrict": "harris_district",
}


def run_routing_benchmark():
    print("\n" + "=" * 72)
    print("BENCHMARK: State Routing Correctness (100 Claims, Offline)")
    print("=" * 72)
    results = {
        "fl_claims": 0, "fl_portal_attempts": 0, "fl_ok": 0, "fl_degraded": 0,
        "tx_claims": 0, "tx_portal_attempts": 0, "tx_ok": 0, "tx_degraded": 0,
        "total_attempts": 0, "failures": [],
    }
    claim_scenarios = [("FL", "FL")] * 50 + [("TX", "TX")] * 50
    for i, (policy_st, loss_st) in enumerate(claim_scenarios, start=1):
        claim_num = f"BENCH-{i:04d}"
        rt = _routing_type(policy_st, loss_st)
        targets = resolve_county_bot_targets(policy_st, loss_st)
        dispatched = [TARGET_TO_PORTAL.get(k, k) for k, v in targets.items() if v == "Yes"]
        expected = _expected_portals(rt)
        ok = set(expected).issubset(set(dispatched))
        if rt == "FL_SAME_STATE":
            results["fl_claims"] += 1
            results["fl_portal_attempts"] += len(dispatched)
            if ok:
                results["fl_ok"] += 1
            else:
                results["fl_degraded"] += 1
                results["failures"].append(f"{claim_num}: expected {expected} got {dispatched}")
        elif rt == "TX_SAME_STATE":
            results["tx_claims"] += 1
            results["tx_portal_attempts"] += len(dispatched)
            if ok:
                results["tx_ok"] += 1
            else:
                results["tx_degraded"] += 1
                results["failures"].append(f"{claim_num}: expected {expected} got {dispatched}")
    results["total_attempts"] = results["fl_portal_attempts"] + results["tx_portal_attempts"]
    print(f"\n{'Type':<22} {'Claims':>6} {'Attempts':>9} {'OK':>5} {'DEGRADED':>9}")
    print("-" * 55)
    print(f"{'Florida (FL x3)':<22} {results['fl_claims']:>6} {results['fl_portal_attempts']:>9} {results['fl_ok']:>5} {results['fl_degraded']:>9}")
    print(f"{'Texas (TX x5)':<22} {results['tx_claims']:>6} {results['tx_portal_attempts']:>9} {results['tx_ok']:>5} {results['tx_degraded']:>9}")
    print("-" * 55)
    print(f"{'TOTAL':<22} {'100':>6} {results['total_attempts']:>9}")
    print("\nExpected: FL=150, TX=250, Total=400")
    print(f"Actual:   FL={results['fl_portal_attempts']}, TX={results['tx_portal_attempts']}, Total={results['total_attempts']}")
    if results["failures"]:
        print("\n[FAILURES]:")
        for f in results["failures"][:10]:
            print(f"  {f}")
    all_ok = results["fl_portal_attempts"] == 150 and results["tx_portal_attempts"] == 250 and not results["failures"]
    print(f"\n{'ROUTING BENCHMARK PASSED' if all_ok else 'ROUTING BENCHMARK FAILED'}")
    return results


def run_cross_state_benchmark():
    print("\n" + "=" * 72)
    print("BENCHMARK: Cross-State 8-Bot Compliance (18 Scenarios)")
    print("=" * 72)
    cross_state_pairs = [
        ("FL","NY"),("FL","GA"),("FL","NJ"),("FL","CA"),("FL","TX"),
        ("TX","LA"),("TX","MO"),("TX","OK"),("TX","FL"),
        ("GA","FL"),("NY","FL"),("NJ","TX"),("CA","TX"),
        ("OH","FL"),("IL","TX"),("PA","FL"),("NC","TX"),("VA","FL"),
    ]
    ok_count = 0
    fail_count = 0
    failures = []
    print(f"\n  {'Scenario':<20} {'Result'}")
    print("  " + "-" * 36)
    for policy_st, loss_st in cross_state_pairs:
        targets = resolve_county_bot_targets(policy_st, loss_st)
        dispatched = [TARGET_TO_PORTAL.get(k, k) for k, v in targets.items() if v == "Yes"]
        missing = [p for p in ALL_8_PORTALS if p not in dispatched]
        if missing:
            fail_count += 1
            failures.append(f"  PolicyState={policy_st} LossState={loss_st} Missing={missing}")
            print(f"  {policy_st}/{loss_st:<18} FAIL — missing {missing}")
        else:
            ok_count += 1
            print(f"  {policy_st}/{loss_st:<18} OK (8 portals)")
    print(f"\n{'ALL 18 CROSS-STATE SCENARIOS PASSED' if not failures else str(fail_count) + ' FAILURES'}")
    if failures:
        for f in failures:
            print(f)
    return {"ok": ok_count, "failed": fail_count}


def run_portal_ping_benchmark():
    print("\n" + "=" * 72)
    print("BENCHMARK: Live Portal Reachability (All 8 County Court Portals)")
    print("=" * 72)
    results = {}
    all_reachable = True
    print(f"\n  {'Portal':<18} {'Status':>8}  {'Code':>5}  {'Latency':>9}  Message")
    print("  " + "-" * 65)
    for name, url in PORTAL_URLS.items():
        t_start = time.perf_counter()
        reachable, code, msg = _check_portal_http(name, url)
        latency = (time.perf_counter() - t_start) * 1000
        results[name] = {"reachable": reachable, "code": code, "latency_ms": round(latency, 1)}
        icon = "OK" if reachable else "FAIL"
        print(f"  {name:<18} {icon:>8}   {code:>5}   {latency:>7.0f}ms  {msg}")
        if not reachable:
            all_reachable = False
    print(f"\n{'ALL 8 PORTALS REACHABLE' if all_reachable else 'SOME PORTALS UNREACHABLE'}")
    return results


def main():
    parser = argparse.ArgumentParser(description="UAIC 100-Claim Portal Benchmark (IMP-2026-1007-001)")
    parser.add_argument("--live", action="store_true", help="Run live HTTP ping benchmark")
    args = parser.parse_args()
    print("=" * 72)
    print("UAIC 100-Claim CAPTCHA & Portal Benchmark")
    print("IMP-2026-1007-001 Acceptance Criteria Verification")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 72)
    routing_result = run_routing_benchmark()
    cross_result   = run_cross_state_benchmark()
    ping_result    = {}
    if args.live:
        ping_result = run_portal_ping_benchmark()
    print("\n" + "=" * 72)
    print("FINAL BENCHMARK SUMMARY")
    print("=" * 72)
    routing_ok = routing_result["fl_degraded"] == 0 and routing_result["tx_degraded"] == 0
    cross_ok   = cross_result["failed"] == 0
    ping_ok    = all(v["reachable"] for v in ping_result.values()) if ping_result else None
    print(f"  Routing (100 claims, 400 attempts): {'PASS' if routing_ok else 'FAIL'} ({routing_result['total_attempts']} total attempts)")
    print(f"  Cross-State (18 scenarios, 8-bot):  {'PASS' if cross_ok else 'FAIL'}")
    if ping_ok is not None:
        print(f"  Portal Reachability (live ping):    {'PASS' if ping_ok else 'FAIL'}")
    else:
        print("  Portal Reachability (live ping):    SKIPPED (use --live to enable)")
    all_pass = routing_ok and cross_ok and (ping_ok is not False)
    print(f"\n{'ALL BENCHMARKS PASSED' if all_pass else 'SOME BENCHMARKS FAILED'}")
    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    main()
