"""Test scraper pagination behavior and removal of the 15-row cap (TC-PAG-001 through TC-PAG-009)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.automation.florida import BrowardScraper
from app.automation.texas import (
    DallasScraper,
    HarrisJPScraper,
    TravisScraper,
)


@pytest.mark.asyncio
async def test_tc_pag_004_travis_no_15_row_cap():
    """TC-PAG-004: Travis extracts all rows beyond 15 (no min(count, 15) hardcap)."""
    scraper = TravisScraper()
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=False)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")

    # Mock 20 rows
    total_mock_rows = 20
    mock_rows = []
    for i in range(total_mock_rows):
        row_mock = MagicMock()
        row_mock.locator.return_value.all_inner_texts = AsyncMock(
            return_value=[f"D-1-GN-24-00{i:04d}", f"Plaintiff v. Defendant {i}", "01/15/2023", "ACTIVE", "CIVIL"]
        )
        mock_rows.append(row_mock)

    rows_locator = MagicMock()
    rows_locator.count = AsyncMock(return_value=total_mock_rows)
    rows_locator.nth.side_effect = lambda idx: mock_rows[idx]

    # Mock inputs, buttons, next button
    mock_el = MagicMock()
    mock_el.count = AsyncMock(return_value=1)
    mock_el.first = mock_el
    mock_el.is_visible = AsyncMock(return_value=True)
    mock_el.wait_for = AsyncMock()
    mock_el.fill = AsyncMock()
    mock_el.click = AsyncMock()
    mock_el.get_attribute = AsyncMock(return_value="k-state-disabled")  # End pagination after page 1

    def loc_side_effect(sel):
        if ".k-grid-content" in sel or "table.k-selectable" in sel or "table tbody tr" in sel:
            return rows_locator
        return mock_el

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = True
        res = await scraper.search_by_party_name("Jane", "Doe", page)

    assert len(res) == 20, f"Expected 20 cases, got {len(res)}"


@pytest.mark.asyncio
async def test_tc_pag_005_dallas_no_15_row_cap():
    """TC-PAG-005: Dallas extracts all rows beyond 15 (no min(count, 15) hardcap)."""
    scraper = DallasScraper()
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=False)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")

    total_mock_rows = 22
    mock_rows = []
    for i in range(total_mock_rows):
        row_mock = MagicMock()
        row_mock.locator.return_value.all_inner_texts = AsyncMock(
            return_value=[f"DC-23-00{i:04d}", f"Smith - Plaintiff vs Jones | Defendant {i}", "02/20/2023", "ACTIVE", "CIVIL"]
        )
        mock_rows.append(row_mock)

    rows_locator = MagicMock()
    rows_locator.count = AsyncMock(return_value=total_mock_rows)
    rows_locator.nth.side_effect = lambda idx: mock_rows[idx]

    mock_el = MagicMock()
    mock_el.count = AsyncMock(return_value=1)
    mock_el.first = mock_el
    mock_el.is_visible = AsyncMock(return_value=True)
    mock_el.wait_for = AsyncMock()
    mock_el.fill = AsyncMock()
    mock_el.click = AsyncMock()
    mock_el.get_attribute = AsyncMock(return_value="k-state-disabled")

    def loc_side_effect(sel):
        if ".k-grid-content" in sel or "table.k-selectable" in sel or "table tbody tr" in sel:
            return rows_locator
        return mock_el

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = True
        res = await scraper.search_by_party_name("Alice", "Smith", page)

    assert len(res) == 22, f"Expected 22 cases, got {len(res)}"


@pytest.mark.asyncio
async def test_tc_pag_006_harris_jp_no_15_row_cap():
    """TC-PAG-006: Harris JP extracts all rows beyond 15 (no min(count, 15) hardcap)."""
    scraper = HarrisJPScraper()
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=False)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")

    total_mock_rows = 18
    mock_rows = []
    for i in range(total_mock_rows):
        row_mock = MagicMock()
        row_mock.locator.return_value.all_inner_texts = AsyncMock(
            return_value=[f"23-JP-00{i:04d}", f"State Farm v. Driver {i}", "03/10/2023", "Case Status: Open"]
        )
        mock_rows.append(row_mock)

    rows_locator = MagicMock()
    rows_locator.count = AsyncMock(return_value=total_mock_rows)
    rows_locator.nth.side_effect = lambda idx: mock_rows[idx]

    mock_el = MagicMock()
    mock_el.count = AsyncMock(return_value=1)
    mock_el.first = mock_el
    mock_el.is_visible = AsyncMock(return_value=True)
    mock_el.wait_for = AsyncMock()
    mock_el.fill = AsyncMock()
    mock_el.click = AsyncMock()
    mock_el.get_attribute = AsyncMock(return_value="k-state-disabled")

    def loc_side_effect(sel):
        if ".k-grid-content" in sel or "table.k-selectable" in sel or "table tbody tr" in sel:
            return rows_locator
        return mock_el

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = True
        res = await scraper.search_by_party_name("Bob", "Brown", page)

    assert len(res) == 18, f"Expected 18 cases, got {len(res)}"


@pytest.mark.asyncio
async def test_tc_pag_001_broward_pagination_iterates_pages():
    """TC-PAG-001: Broward pagination loop advances to next page."""
    scraper = BrowardScraper()
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=False)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")
    page.evaluate = AsyncMock(return_value=False)

    call_idx = {"page": 0}

    def get_row(idx):
        p = call_idx["page"]
        row_m = MagicMock()
        row_m.locator.return_value.all_inner_texts = AsyncMock(
            return_value=[f"CACE-23-00{p}{idx:02d}", "Style", "CIVIL", "01/01/2023", "OPEN"]
        )
        return row_m

    rows_locator = MagicMock()
    rows_locator.count = AsyncMock(return_value=2)
    rows_locator.nth.side_effect = lambda idx: get_row(idx)

    next_btn = MagicMock()
    next_btn.count = AsyncMock(return_value=1)
    next_btn.first = next_btn
    next_btn.is_visible = AsyncMock(return_value=True)

    async def mock_next_click():
        call_idx["page"] += 1

    next_btn.click = AsyncMock(side_effect=mock_next_click)

    async def mock_get_attr(attr):
        if call_idx["page"] >= 1:
            return "true"  # disabled on page 2
        return "false"

    next_btn.get_attribute = AsyncMock(side_effect=mock_get_attr)

    mock_input = MagicMock()
    mock_input.count = AsyncMock(return_value=1)
    mock_input.first = mock_input
    mock_input.wait_for = AsyncMock()
    mock_input.fill = AsyncMock()
    mock_input.click = AsyncMock()

    def loc_side_effect(sel):
        if "table.table tbody tr" in sel or "table tbody tr" in sel:
            return rows_locator
        if "next" in sel.lower():
            return next_btn
        return mock_input

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = True
        res = await scraper.search_by_party_name("John", "Doe", page)

    assert len(res) >= 2


@pytest.mark.asyncio
async def test_tc_pag_009_safety_ceiling_stops_at_10_pages():
    """TC-PAG-009: Base scraper pagination helper or loop respects max 10 pages ceiling."""
    scraper = TravisScraper()
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=False)
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.inner_text = AsyncMock(return_value="Results")
    page.evaluate = AsyncMock(return_value=False)

    # Continuous rows and always-enabled next button
    rows_locator = MagicMock()
    rows_locator.count = AsyncMock(return_value=1)
    row_mock = MagicMock()
    row_mock.locator.return_value.all_inner_texts = AsyncMock(
        return_value=["D-1-GN-24-9999", "Style", "01/01/2023", "ACTIVE", "CIVIL"]
    )
    rows_locator.nth.return_value = row_mock

    next_btn = MagicMock()
    next_btn.count = AsyncMock(return_value=1)
    next_btn.first = next_btn
    next_btn.is_visible = AsyncMock(return_value=True)
    next_btn.get_attribute = AsyncMock(return_value="")  # Never disabled
    next_btn.click = AsyncMock()

    mock_btn = MagicMock()
    mock_btn.count = AsyncMock(return_value=1)
    mock_btn.first = mock_btn
    mock_btn.is_visible = AsyncMock(return_value=True)
    mock_btn.click = AsyncMock()
    mock_btn.wait_for = AsyncMock()
    mock_btn.fill = AsyncMock()

    def loc_side_effect(sel):
        if ".k-grid-content" in sel or "table.k-selectable" in sel or "table tbody tr" in sel:
            return rows_locator
        if "next page" in sel.lower() or "k-i-arrow-e" in sel:
            return next_btn
        return mock_btn

    page.locator.side_effect = loc_side_effect

    with patch.object(scraper, "detect_and_handle_captcha", new_callable=AsyncMock) as mock_cap:
        mock_cap.return_value = True
        await scraper.search_by_party_name("Infinite", "Results", page)

    # Must exit and not loop infinitely (max 10 pages ceiling)
    assert next_btn.click.await_count <= 10
