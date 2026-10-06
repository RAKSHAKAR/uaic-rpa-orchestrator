import asyncio
import json
import os
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

async def check():
    async with AsyncSessionLocal() as s:
        # Check claim counts by state
        res = await s.execute(text("SELECT policy_state, loss_location_state, count(*) FROM claim_records GROUP BY policy_state, loss_location_state;"))
        print("Claims by state:", res.fetchall())
        
        # Check portal json body non-empty counts
        portals = [
            ("Miami-Dade (FL)", "fl_jsonbody_miami"),
            ("Broward (FL)", "fl_jsonbody_broward"),
            ("Hillsborough (FL)", "fl_jsonbody_hillsborough"),
            ("Harris County Clerk (TX)", "te_jsonbody_cclerk"),
            ("Dallas County (TX)", "te_jsonbody_dallas"),
            ("Harris JP (TX)", "te_jsonbody_harris"),
            ("Harris District Clerk (TX)", "te_jsonbody_hcdistrict"),
            ("Travis County (TX)", "te_jsonbody_travis"),
        ]
        
        for name, col in portals:
            r = await s.execute(text(f"SELECT {col} FROM claim_records WHERE {col} IS NOT NULL;"))
            rows = r.fetchall()
            total_cases = 0
            claims_with_cases = 0
            for row in rows:
                val = row[0]
                if isinstance(val, str) and val.strip():
                    try:
                        parsed = json.loads(val)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            total_cases += len(parsed)
                            claims_with_cases += 1
                    except Exception:
                        pass
                elif isinstance(val, list) and len(val) > 0:
                    total_cases += len(val)
                    claims_with_cases += 1
            print(f"{name} ({col}): Scraped={len(rows)}, ClaimsWithCases={claims_with_cases}, TotalCasesExtracted={total_cases}")

if __name__ == "__main__":
    asyncio.run(check())
