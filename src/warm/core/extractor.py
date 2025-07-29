# extractor.py — Module for WARM
# modules/extractor.py

import re
import hashlib
import ssdeep
import mmh3
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests


def compute_hashes(html: str) -> dict:
    """Compute SHA256 and ssdeep fuzzy hash of HTML content."""
    html_bytes = html.encode("utf-8", errors="ignore")
    return {
        "html_sha256": hashlib.sha256(html_bytes).hexdigest(),
        "html_ssdeep": ssdeep.hash(html_bytes),
        "html_size": len(html_bytes),
    }


def extract_title(soup: BeautifulSoup) -> str:
    """Extract the page title, with fallback if .string is None."""
    if not soup.title:
        return "-"
    title_tag = soup.title
    text = title_tag.string.strip() if title_tag.string else ""
    if text:
        return text
    return soup.title.get_text(strip=True) or "-"


def extract_favicon_hash(soup: BeautifulSoup, base_url: str) -> tuple:
    """
    Find favicon link, fetch it once, and return its URL and mmh3 hash.
    Returns ("ERR") for hash on error.
    """
    icon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    href = icon["href"] if icon and icon.get("href") else "/favicon.ico"
    full_url = href if href.startswith(("http://", "https://")) else urljoin(base_url, href)
    fav_hash = "ERR"
    try:
        resp = requests.get(full_url, timeout=8)
        if resp.status_code == 200:
            fav_hash = mmh3.hash_bytes(resp.content).hex()
    except Exception:
        pass
    return full_url, fav_hash


def extract_form_data(soup: BeautifulSoup) -> dict:
    """Count total forms and forms with password fields."""
    forms = soup.find_all("form")
    password_forms = sum(
        1 for f in forms for _ in f.find_all("input", {"type": "password"})
    )
    return {
        "form_count": len(forms),
        "password_fields": password_forms,
    }


def extract_resource_counts(soup: BeautifulSoup, page_url: str) -> dict:
    """
    Count JS, CSS, IMG resources and distinguish external ones.
    Only counts .js scripts, .css links (with rel=stylesheet), and img tags.
    """
    host = urlparse(page_url).netloc
    counts = {k: 0 for k in ("js", "css", "img", "ext_js", "ext_css", "ext_img")}

    for tag, attr, key in [
        ("script", "src", "js"),
        ("link", "href", "css"),
        ("img", "src", "img"),
    ]:
        for t in soup.find_all(tag):
            url = t.get(attr)
            if not url:
                continue

            # For <link>, ensure it's a stylesheet
            if tag == "link" and "stylesheet" not in (t.get("rel") or []):
                continue

            full = url if url.startswith(("http://", "https://")) else urljoin(page_url, url)
            is_external = urlparse(full).netloc != host

            if tag == "script" and full.lower().endswith(".js"):
                counts["js"] += 1
                if is_external:
                    counts["ext_js"] += 1

            elif tag == "link" and full.lower().endswith(".css"):
                counts["css"] += 1
                if is_external:
                    counts["ext_css"] += 1

            elif tag == "img":
                counts["img"] += 1
                if is_external:
                    counts["ext_img"] += 1

    return counts


def extract_meta(soup: BeautifulSoup) -> dict:
    """Extract meta description length and robots directives."""
    desc = soup.find("meta", {"name": "description"})
    robots = soup.find("meta", {"name": "robots"})
    return {
        "meta_description_len": len(desc["content"]) if desc and desc.get("content") else 0,
        "meta_robots": robots["content"] if robots and robots.get("content") else "-",
    }


def extract_title_font(soup: BeautifulSoup) -> str:
    """
    Return the CSS font-family of the <title> element (or BODY fallback).
    Relies on inline/style tags only; for computed styles you’d need Selenium.
    """
    # Look for inline style on the <title> tag
    title_tag = soup.title
    if title_tag and title_tag.has_attr("style"):
        style = title_tag["style"]
        for decl in style.split(";"):
            if "font-family" in decl:
                return decl.split(":", 1)[1].strip()

    # Otherwise scan <style> blocks for “title” or “.page-title” rules:
    for style_block in soup.find_all("style"):
        text = style_block.get_text()
        m = re.search(
            r"(?:title|\.page-title)[^\{]*\{[^}]*font-family\s*:\s*([^;]+);",
            text,
            re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()

    # Fallback: no explicit font found
    return "-"


def extract_all(soup: BeautifulSoup, base_url: str, html: str) -> dict:
    """
    Run all extractors and return a combined dictionary of:
      - title, hashes, favicon info,
      - form data, resource counts, meta info, and title font
    """
    title = extract_title(soup)
    hashes = compute_hashes(html)
    fav_url, fav_hash = extract_favicon_hash(soup, base_url)
    forms = extract_form_data(soup)
    resources = extract_resource_counts(soup, base_url)
    meta = extract_meta(soup)
    title_font = extract_title_font(soup)

    return {
        "title": title,
        **hashes,
        "favicon_url": fav_url,
        "favicon_hash": fav_hash,
        **forms,
        **resources,
        **meta,
        "title_font": title_font,
    }

