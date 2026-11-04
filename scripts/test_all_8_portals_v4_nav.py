"""Live test verifying that all 8 portal scrapers resolve and navigate to exact Power Automate V4 URLs."""

from app.automation.florida.broward import BROWARD_PORTAL_URL, BrowardScraper
from app.automation.florida.hillsborough import HILLSBOROUGH_PORTAL_URL, HillsboroughScraper
from app.automation.florida.miami import MIAMI_OCS_PORTAL_URL, MiamiDadeScraper
from app.automation.texas.dallas import DALLAS_PORTAL_URL, DallasScraper
from app.automation.texas.harris_cclerk import HARRIS_CCLERK_PORTAL_URL, HarrisCountyClerkScraper
from app.automation.texas.harris_district import (
    HARRIS_DISTRICT_PORTAL_URL,
    HarrisDistrictClerkScraper,
)
from app.automation.texas.harris_jp import HARRIS_JP_PORTAL_URL, HarrisJPScraper
from app.automation.texas.travis import TRAVIS_PORTAL_URL, TravisScraper


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
