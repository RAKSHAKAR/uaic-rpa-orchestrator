from playwright.sync_api import sync_playwright


def check():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto("http://localhost:3000", wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.screenshot(path="docs/dashboard_zero_inprogress_verified.png", full_page=True)
        print("Page loaded. Title:", page.title())

        # Inspect cards
        stat_cards = page.locator("div.border.rounded-xl").all()
        for i, card in enumerate(stat_cards[:8]):
            text = " ".join([l.strip() for l in card.all_text_contents()[0].split() if l.strip()])
            print(f"Card {i}: {text}")
        browser.close()


if __name__ == "__main__":
    check()
