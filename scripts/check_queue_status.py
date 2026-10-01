import json
import urllib.request

def main():
    try:
        req = urllib.request.urlopen("http://localhost:8000/api/v1/queue/live")
        data = json.loads(req.read())
        print(f"Total Pending Count: {data.get('total_pending_count')}")
        print(f"Total In Progress: {data.get('total_in_progress_count')}")
        print(f"Workers Online: {data.get('workers_online')}")
        print(f"Max Concurrency: {data.get('max_concurrency')}")
        print(f"Auto Queue Enabled: {data.get('auto_queue_enabled')}")
        pending = data.get("pending_items", [])
        print(f"Pending Items Returned: {len(pending)}")
        for idx, p in enumerate(pending[:15]):
            print(f"  #{idx+1} [Pos {p.get('position')}]: Claim #{p.get('claim_number')} | State: {p.get('policy_state')} | Status: {p.get('record_status')}")
    except Exception as e:
        print(f"Error querying queue status: {e}")

if __name__ == "__main__":
    main()
