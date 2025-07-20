from playwright.sync_api import sync_playwright


def get_rendered_html(url: str):
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()

            # wait for js content to load
            page.goto(url, wait_until="networkidle")
            page.wait_for_function("document.readyState === 'complete'")

            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"error processing request: {e}")
        return ""
