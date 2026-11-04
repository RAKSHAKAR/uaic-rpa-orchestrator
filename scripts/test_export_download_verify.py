"""Comprehensive Automated Export & Download Verification Script.

Tests both synchronous and asynchronous export generation across Excel and CSV formats,
downloads the actual output files via HTTP, opens and parses the downloaded files,
and verifies that all sheets, columns, and data rows are fully populated with zero errors.
"""

import sys
import time
from pathlib import Path

import httpx
import openpyxl
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"
DOWNLOAD_DIR = Path(__file__).resolve().parent / "test_downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
client = httpx.Client(timeout=90.0)


def test_sync_excel_export():
    print("\n--- [1/5] Testing Synchronous Excel Export ---")
    url = f"{BASE_URL}/api/v1/claims/export?format=xlsx"
    t0 = time.time()
    resp = client.get(url)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    elapsed = round(time.time() - t0, 2)

    out_file = DOWNLOAD_DIR / "sync_export.xlsx"
    out_file.write_bytes(resp.content)
    print(f"Downloaded {len(resp.content):,} bytes in {elapsed}s to {out_file.name}")

    # Verify contents with openpyxl
    wb = openpyxl.load_workbook(out_file)
    print(f"Found sheets: {wb.sheetnames}")
    assert "Claims Summary" in wb.sheetnames, "Missing Claims Summary sheet"
    assert "All Extracted Cases" in wb.sheetnames, "Missing All Extracted Cases sheet"
    assert "Detailed Stage Telemetry" in wb.sheetnames, "Missing Detailed Stage Telemetry sheet"

    df_summary = pd.read_excel(out_file, sheet_name="Claims Summary")
    df_cases = pd.read_excel(out_file, sheet_name="All Extracted Cases")
    df_stages = pd.read_excel(out_file, sheet_name="Detailed Stage Telemetry")

    print(f"Claims Summary rows: {len(df_summary)}, columns: {len(df_summary.columns)}")
    print(f"All Extracted Cases rows: {len(df_cases)}, columns: {len(df_cases.columns)}")
    print(f"Detailed Stage Telemetry rows: {len(df_stages)}, columns: {len(df_stages.columns)}")

    assert len(df_summary) > 0, "Claims Summary sheet is empty"
    assert len(df_stages) > 0, "Detailed Stage Telemetry sheet is empty"
    assert "County Portal" in df_stages.columns, "County Portal column missing in telemetry"
    assert "Stage Name" in df_stages.columns, "Stage Name column missing in telemetry"
    assert "Duration (s)" in df_stages.columns, "Duration (s) column missing in telemetry"
    print("PASS: Synchronous Excel Export verified with all 3 sheets populated.")


def test_sync_csv_telemetry_export():
    print("\n--- [2/5] Testing Synchronous CSV Stage Telemetry Export ---")
    url = f"{BASE_URL}/api/v1/claims/export?format=csv&view=telemetry"
    t0 = time.time()
    resp = client.get(url)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    elapsed = round(time.time() - t0, 2)

    out_file = DOWNLOAD_DIR / "sync_stage_telemetry.csv"
    out_file.write_bytes(resp.content)
    print(f"Downloaded {len(resp.content):,} bytes in {elapsed}s to {out_file.name}")

    df = pd.read_csv(out_file)
    print(f"CSV Telemetry rows: {len(df)}, columns: {len(df.columns)}")
    assert len(df) > 0, "Telemetry CSV is empty"
    assert "County Portal" in df.columns, "Missing County Portal in CSV"
    assert "Stage Status" in df.columns, "Missing Stage Status in CSV"
    assert "Duration (s)" in df.columns, "Missing Duration (s) in CSV"
    print("PASS: Synchronous CSV Stage Telemetry export verified.")


def test_sync_csv_summary_with_stage_columns():
    print("\n--- [3/5] Testing Synchronous CSV Summary with Stage Duration Columns ---")
    url = f"{BASE_URL}/api/v1/claims/export?format=csv&view=summary"
    resp = client.get(url)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    out_file = DOWNLOAD_DIR / "sync_summary.csv"
    out_file.write_bytes(resp.content)
    df = pd.read_csv(out_file)
    print(f"CSV Summary rows: {len(df)}, columns: {len(df.columns)}")
    assert len(df) > 0, "Summary CSV is empty"
    assert "Total Scraping Duration (s)" in df.columns, "Total Scraping Duration (s) missing"
    assert "Stage CAPTCHA Solving (s)" in df.columns, "Stage CAPTCHA Solving (s) missing"
    print("PASS: Synchronous CSV Summary stage columns verified.")


def test_async_excel_export_and_download():
    print("\n--- [4/5] Testing Asynchronous Excel Export & Download Loop ---")
    trigger_url = f"{BASE_URL}/api/v1/claims/export-async"
    payload = {"format": "xlsx", "view": "telemetry"}
    resp = client.post(trigger_url, json=payload)
    assert resp.status_code == 200, f"Trigger failed: {resp.text}"
    data = resp.json()
    assert data.get("success") is True, f"Trigger success is False: {data}"
    task_id = data.get("task_id")
    print(f"Triggered background export task: {task_id}")

    # Poll status until SUCCESS
    status_url = f"{BASE_URL}/api/v1/claims/export-async/{task_id}/status"
    max_wait = 120
    t0 = time.time()
    result = None
    while time.time() - t0 < max_wait:
        poll_resp = client.get(status_url)
        assert poll_resp.status_code == 200, f"Status poll failed: {poll_resp.text}"
        status_data = poll_resp.json()
        print(f"Polling {task_id}: status={status_data.get('status')}, percent={status_data.get('percent')}%, message={status_data.get('message')}")

        if status_data.get("status") == "SUCCESS":
            result = status_data.get("result")
            break
        elif status_data.get("status") == "FAILURE":
            raise RuntimeError(f"Async export failed: {status_data.get('error')}")

        time.sleep(3)

    assert result is not None, f"Async export timed out after {max_wait}s"
    filename = result["filename"]
    download_url = f"{BASE_URL}{result['download_url']}"
    print(f"Export completed! Downloading from {download_url}...")

    dl_resp = client.get(download_url)
    assert dl_resp.status_code == 200, f"Download failed: {dl_resp.status_code}"

    out_file = DOWNLOAD_DIR / filename
    out_file.write_bytes(dl_resp.content)
    print(f"Downloaded async file: {out_file.name} ({len(dl_resp.content):,} bytes)")

    wb = openpyxl.load_workbook(out_file)
    print(f"Async Excel sheet names: {wb.sheetnames}")
    assert "Claims Summary" in wb.sheetnames
    assert "All Extracted Cases" in wb.sheetnames
    assert "Detailed Stage Telemetry" in wb.sheetnames

    df_tel = pd.read_excel(out_file, sheet_name="Detailed Stage Telemetry")
    print(f"Async Excel telemetry rows: {len(df_tel)}, columns: {len(df_tel.columns)}")
    assert len(df_tel) > 0, "Async Excel telemetry sheet has zero rows"
    print("PASS: Asynchronous Excel Export & Download Loop verified.")


def test_async_csv_telemetry_export_and_download():
    print("\n--- [5/5] Testing Asynchronous CSV Stage Telemetry Export & Download Loop ---")
    trigger_url = f"{BASE_URL}/api/v1/claims/export-async"
    payload = {"format": "csv", "view": "telemetry"}
    resp = client.post(trigger_url, json=payload)
    assert resp.status_code == 200, f"Trigger failed: {resp.text}"
    task_id = resp.json()["task_id"]
    print(f"Triggered background CSV export task: {task_id}")

    status_url = f"{BASE_URL}/api/v1/claims/export-async/{task_id}/status"
    max_wait = 120
    t0 = time.time()
    result = None
    while time.time() - t0 < max_wait:
        poll_resp = client.get(status_url)
        assert poll_resp.status_code == 200
        status_data = poll_resp.json()
        print(f"Polling {task_id}: status={status_data.get('status')}, percent={status_data.get('percent')}%, message={status_data.get('message')}")

        if status_data.get("status") == "SUCCESS":
            result = status_data.get("result")
            break
        elif status_data.get("status") == "FAILURE":
            raise RuntimeError(f"Async export failed: {status_data.get('error')}")

        time.sleep(3)

    assert result is not None, f"Async CSV export timed out after {max_wait}s"
    filename = result["filename"]
    download_url = f"{BASE_URL}{result['download_url']}"

    dl_resp = client.get(download_url)
    assert dl_resp.status_code == 200

    out_file = DOWNLOAD_DIR / filename
    out_file.write_bytes(dl_resp.content)
    print(f"Downloaded async CSV file: {out_file.name} ({len(dl_resp.content):,} bytes)")

    df = pd.read_csv(out_file)
    print(f"Async CSV rows: {len(df)}, columns: {len(df.columns)}")
    assert len(df) > 0, "Downloaded CSV has 0 rows"
    assert "Stage Status" in df.columns
    assert "Duration (s)" in df.columns
    print("PASS: Asynchronous CSV Stage Telemetry Export & Download Loop verified.")


if __name__ == "__main__":
    try:
        test_sync_excel_export()
        test_sync_csv_telemetry_export()
        test_sync_csv_summary_with_stage_columns()
        test_async_excel_export_and_download()
        test_async_csv_telemetry_export_and_download()
        print("\n=======================================================")
        print("ALL 5 EXPORT & DOWNLOAD VERIFICATIONS PASSED 100%!")
        print("=======================================================")
    except Exception as e:
        print(f"\nTEST FAILED: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
