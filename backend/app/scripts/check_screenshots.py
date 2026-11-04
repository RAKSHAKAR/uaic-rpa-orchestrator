from pathlib import Path

p = Path("backend/screenshots")
for cid in ["842acd27", "2b41c35b", "9a79524c"]:
    matches = list(p.glob(f"*{cid}*"))
    print(f"CID {cid}: {len(matches)} files found")
    for m in matches:
        print(f"  {m.name} ({m.stat().st_size} bytes)")
