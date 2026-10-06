import asyncio
import json
import sys
from pathlib import Path

# Ensure backend root is on sys.path for IDE analyzer and standalone execution
backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.core.database import AsyncSessionLocal  # type: ignore[import-not-found]
except ImportError:
    from backend.app.core.database import AsyncSessionLocal  # type: ignore[import-not-found]
from sqlalchemy import text

async def inspect_tx():
    async with AsyncSessionLocal() as s:
        # Get Texas claims that were scraped
        query = """
            SELECT claim_number, policy_state, loss_location_state,
                   te_botstatus_cclerk, te_botstatus_dallas, te_botstatus_harris, te_botstatus_hcdistrict, te_botstatus_travis,
                   te_jsonbody_cclerk, te_jsonbody_dallas, te_jsonbody_harris, te_jsonbody_hcdistrict, te_jsonbody_travis,
                   last_error, id
            FROM claim_records
            WHERE te_jsonbody_cclerk IS NOT NULL
            LIMIT 10;
        """
        r = await s.execute(text(query))
        rows = r.fetchall()
        for row in rows:
            def parse_val(v):
                if isinstance(v, list): return v
                if isinstance(v, str) and v.strip():
                    try: return json.loads(v)
                    except: return []
                return []
            cclerk_cases = parse_val(row[8])
            dallas_cases = parse_val(row[9])
            harris_jp_cases = parse_val(row[10])
            hcdistrict_cases = parse_val(row[11])
            travis_cases = parse_val(row[12])

            print(f"--- Claim: {row[0]} | State: {row[1]} / {row[2]} | ID: {row[14]} ---")
            print(f"  Statuses: cclerk={row[3]}, dallas={row[4]}, harris_jp={row[5]}, hcdistrict={row[6]}, travis={row[7]}")
            print(f"  Cases: cclerk={len(cclerk_cases)}, dallas={len(dallas_cases)}, harris_jp={len(harris_jp_cases)}, hcdistrict={len(hcdistrict_cases)}, travis={len(travis_cases)}")
            if row[13]:
                print(f"  Last Error: {row[13]}")
            if len(hcdistrict_cases) > 0:
                print(f"  HCDistrict Cases Sample: {hcdistrict_cases[:1]}")

        # Check total scraped court cases in court_cases table
        r_cases = await s.execute(text("SELECT county_portal, count(*) FROM scraped_court_cases GROUP BY county_portal;"))
        print("\n=== Cases in scraped_court_cases Table ===")
        for c in r_cases.fetchall():
            print(f"  {c[0]}: {c[1]} cases")

if __name__ == "__main__":
    asyncio.run(inspect_tx())
