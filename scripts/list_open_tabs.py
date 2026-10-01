from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp('http://localhost:9222')
        ctx = b.contexts[0]
        print(f"Total pages in Chrome: {len(ctx.pages)}")
        for idx, page in enumerate(ctx.pages):
            try:
                title = page.title()
            except Exception:
                title = "Unknown"
            print(f"Tab {idx+1}: {page.url} | Title: {title}")

if __name__ == "__main__":
    main()
