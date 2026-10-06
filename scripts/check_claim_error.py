import httpx

CLAIM_ID = "ffb9d367-9635-4bab-a5d8-b1de50e0d08d"

def check():
    client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=15.0)
    res = client.get(f"/claims/{CLAIM_ID}")
    if res.status_code == 200:
        c = res.json()
        print(f"Claim #{c.get('claim_number')}: Status={c.get('record_status')}, Error={c.get('error_message')}")
        print("Bot statuses:", [(b.get('name'), b.get('status')) for b in c.get('bots', [])])

if __name__ == "__main__":
    check()
