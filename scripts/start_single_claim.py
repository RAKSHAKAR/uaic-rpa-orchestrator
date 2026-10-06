import httpx

CLAIM_ID = "c31c1be0-b911-4864-997e-7295cc615ce0" # 800221263 (Texas)

def test_run():
    client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=30.0)
    res = client.post(f"/claims/{CLAIM_ID}/start")
    print(f"Status: {res.status_code}")
    print(f"Text: {res.text}")

if __name__ == "__main__":
    test_run()
