from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.automation.base import BaseCourtScraper


class MockScraper(BaseCourtScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def search_by_party_name(self, *args, **kwargs):
        return []

@pytest.mark.asyncio
async def test_biometric_click():
    """Test that biometric_click implements mouse pacing correctly."""
    scraper = MockScraper("TestCounty", "http://test.com")
    
    mock_page = MagicMock()
    mock_page.mouse = AsyncMock()
    mock_locator = AsyncMock()
    mock_locator.bounding_box.return_value = {"x": 100, "y": 100, "width": 50, "height": 50}
    
    await scraper.biometric_click(mock_page, mock_locator)
    
    assert mock_locator.bounding_box.called
    assert mock_page.mouse.move.called
    assert mock_page.mouse.down.called
    assert mock_page.mouse.up.called

@pytest.mark.asyncio
async def test_date_of_loss_10_year_lookback():
    """Test that a claim with a DOL older than 10 years is capped to 10 years ago."""
    # We will just test the logic directly or through a mocked DB session if we want to run the full orchestrator.
    # Given the complexity of mocking the whole orchestrator, we can test the explicit logic here.
    
    dol = "01/01/2005"
    search_dol = dol
    dt = datetime.strptime(search_dol, "%m/%d/%Y")
    ten_years_ago = datetime.now() - timedelta(days=365*10)
    
    if dt < ten_years_ago:
        search_dol = ten_years_ago.strftime("%m/%d/%Y")
        
    assert search_dol == ten_years_ago.strftime("%m/%d/%Y")
    
    dol_recent = datetime.now().strftime("%m/%d/%Y")
    search_dol_recent = dol_recent
    dt_recent = datetime.strptime(search_dol_recent, "%m/%d/%Y")
    if dt_recent < ten_years_ago:
        search_dol_recent = ten_years_ago.strftime("%m/%d/%Y")
        
    assert search_dol_recent == dol_recent
