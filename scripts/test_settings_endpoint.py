import httpx

def test_endpoint():
    client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=30.0)
    
    get_res = client.get("/settings")
    print(f"GET /settings status: {get_res.status_code}")
    data = get_res.json()
    data["clear_secrets"] = []
    
    post_res = client.post("/settings", json=data)
    print(f"POST /settings status: {post_res.status_code}")
    print(f"Response: {post_res.text}")

if __name__ == "__main__":
    test_endpoint()
