from playwright.sync_api import sync_playwright
from pathlib import Path

template = Path(__file__).parent / "render_template.html"
template = template.as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("console", lambda m: print(f"[console.{m.type}]", m.text))
    page.on("pageerror", lambda e: print("[pageerror]", e))
    page.on("requestfailed", lambda r: print("[reqfail]", r.url, r.failure))
    page.goto(template)
    try:
        page.wait_for_function("window.__moduleReady === true", timeout=15000)
        print("MODULE READY")
    except Exception as e:
        print("TIMEOUT:", e)
        ready = page.evaluate("typeof window.__moduleReady")
        print("__moduleReady type:", ready)
    browser.close()
