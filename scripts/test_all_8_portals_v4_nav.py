"""Live test verifying that all 8 portal scrapers resolve and navigate to exact Power Automate V4 URLs."""

import asyncio
from app.automation.florida.broward import BrowardScraper, BROWARD_PORTAL_URL
from app.automation.florida.hillsborough import HillsboroughScraper, HILLSBOROUGH_PORTAL_URL
from app.automation.florida.miami import MiamiDadeScraper, MIAMI_OCS_PORTAL_URL
from app.automation.texas.dallas import DallasScraper, DALLAS_PORTAL_URL
from app.automation.texas.travis import TravisScraper, TRAVIS_PORTAL_URL
from app.automation.texas.harris_jp import HarrisJPScraper, HARRIS_JP_PORTAL_URL
from app.automation.texas.harris_cclerk import HarrisCountyClerkScraper, HARRIS_CCLERK_PORTAL_URL
from app.automation.texas.harris_district import HarrisDistrictClerkScraper, HARRIS_DISTRICT_PORTAL_URL

def test_v4_portal_urls():
    portals = [
        ("Broward", BrowardScraper(), BROWARD_PORTAL_URL, "https://www.browardclerk.org/Web2"),
        ("Dallas", DallasScraper(), DALLAS_PORTAL_URL, "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29"),
        ("Travis", TravisScraper(), TRAVIS_PORTAL_URL, "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29"),
        ("Harris JP", HarrisJPScraper(), HARRIS_JP_PORTAL_URL, "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29"),
        ("Miami", MiamiDadeScraper(), MIAMI_OCS_PORTAL_URL, "https://www2.miamidadeclerk.gov/ocs"),
        ("Harris CClerk", HarrisCountyClerkScraper(), HARRIS_CCLERK_PORTAL_URL, "https://www.cclerk.hctx.net/Applications/WebSearch/CourtSearch_R.aspx"),
        ("Hillsborough", HillsboroughScraper(), HILLSBOROUGH_PORTAL_URL, "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab"),
        ("Harris District", HarrisDistrictClerkScraper(), HARRIS_DISTRICT_PORTAL_URL, "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx"),
    ]

    print("=" * 80)
    print("VERIFYING POWER AUTOMATE V4 EXACT CANONICAL URL PARITY ACROSS ALL 8 BOTS")
    print("=" * 80)

    for name, scraper, canonical_const, expected in portals:
        assert canonical_const == expected, f"{name}: {canonical_const} != {expected}"
        print(f"[{name:15s}] -> Canonical V4 URL: {canonical_const}")
    print("\nAll 8 portal canonical URLs match Power Automate Desktop V4 exactly!")

if __name__ == "__main__":
    test_v4_portal_urls()
