"""Test script to immediately launch Chrome with visible GUI and perform a real court search."""

import asyncio
import os
import sys

# Ensure backend is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.automation.florida.hillsborough import HillsboroughScraper
from app.automation.florida.miami import MiamiDadeScraper


async def run_live_gui():
    print("==========================================================")
    print("  LAUNCHING VISIBLE CHROME IN ATTENDED GUI MODE")
    print("==========================================================")
    print("Starting Hillsborough County Court Portal search for party: 'JOHN DOE'...")
    
    scraper = HillsboroughScraper(
        headless=False,
        max_attempts=3,
        timeout_ms=30000,
        use_chrome=True,
    )
    
    results = await scraper.run_search(first_name="JOHN", last_name="DOE")
    print(f"\n[DONE] Extraction finished! Found {len(results)} court cases.")
    for r in results[:5]:
        print(f" - Case: {r.get('case_number')} | Style: {r.get('case_style')} | Date: {r.get('filing_date')}")


if __name__ == "__main__":
    asyncio.run(run_live_gui())
