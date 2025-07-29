# fetcher.py — Module for WARM
# WARM/core/fetcher.py

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}


def init_browser():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"user-agent={HEADERS['User-Agent']}")
    driver_path = ChromeDriverManager().install()
    return webdriver.Chrome(driver_path, options=opts)


def fetch_html(url: str, use_browser=False):
    """
    Tries to fetch the HTML of a URL using requests first, then falls back to Selenium if needed.
    Returns: response object (or dummy), final URL, and HTML content.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code < 500:
            return resp, resp.url, resp.text
    except Exception as e:
        print(f"[!] Requests failed: {e}")

    if use_browser:
        try:
            driver = init_browser()
            driver.get(url)
            html = driver.page_source
            final = driver.current_url
            # Create dummy Response-like object
            class DummyResp:
                def __init__(self):
                    self.status_code = 200
                    self.headers = {}
                    self.elapsed = None
            return DummyResp(), final, html
        finally:
            driver.quit()
    else:
        return None, url, ""


def get_hostname(url):
    """Extracts hostname from URL."""
    return urlparse(url).netloc


if __name__ == "__main__":
    # Quick test
    url = input("Enter URL to fetch: ").strip()
    resp, final, html = fetch_html(url)
    print(f"[+] Final URL: {final}")
    print(f"[+] Status Code: {resp.status_code if resp else 'ERR'}")
    print(f"[+] Content Length: {len(html)} bytes")

