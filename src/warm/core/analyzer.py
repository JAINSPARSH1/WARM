#!/usr/bin/env python3
# WARM/core/analyzer.py — Central orchestration of fetch → extract → enrich

import sys
import json
from bs4 import BeautifulSoup

from warm.core.fetcher import fetch_html, get_hostname
from warm.core.extractor import extract_all
from warm.core.tls_whois import get_tls_whois_dns_summary
from warm.core.urlscan import scan_url
from warm.core.comparator import compare_dicts
from warm.core.scorer import (
    compute_risk_score,
    human_readable_score,
    log_score_details
)


def analyze_url(url: str, use_browser: bool = False) -> dict:
    """
    Step 1: Fetch site HTML + headers (requests or browser)
    Step 2: Extract page features (HTML, JS, forms, metadata)
    Step 3: Add TLS / WHOIS / DNS data
    """
    resp, final_url, html = fetch_html(url, use_browser=use_browser)
    soup = BeautifulSoup(html or "", "html.parser")

    page_data = extract_all(soup, final_url, html or "")
    tls_whois_dns = get_tls_whois_dns_summary(final_url)

    return {
        "requested_url": url,
        "final_url":     final_url,
        "http_status":   getattr(resp, "status_code", None),
        "load_time":     getattr(resp, "elapsed", None),
        **page_data,
        **tls_whois_dns,
    }


def analyze_with_fallback(url: str) -> dict:
    """
    Try fast request-based fetch. If it fails, fallback to browser-based fetch.
    """
    try:
        return analyze_url(url, use_browser=False)
    except Exception as e:
        print(f"  › Plain fetch failed: {e}", file=sys.stderr)

    try:
        print(f"  › Retrying with browser...")
        return analyze_url(url, use_browser=True)
    except Exception as e:
        print(f"  › Browser fetch failed: {e}", file=sys.stderr)
        sys.exit(1)


def enrich_with_urlscan(data: dict) -> dict:
    """
    Use urlscan.io enrichment if available.
    Adds `urlscan_verdict` and `urlscan_score` fields.
    """
    try:
        result = scan_url(data["final_url"])
        data["urlscan_verdict"] = result.get("verdict", "unknown")
        data["urlscan_score"] = result.get("page", {}).get("score", "")
        data["urlscan_domain"] = result.get("page", {}).get("domain", "")
        data["urlscan_result_url"] = result.get("task", {}).get("reportURL", "")
        data["urlscan_screenshot"] = result.get("task", {}).get("screenshotURL", "")
    except Exception as e:
        data["urlscan_error"] = str(e)
    return data


def full_analysis(url: str, use_browser: bool = False, do_urlscan: bool = False) -> dict:
    """
    Run all extractors + TLS/WHOIS enrichments + (optional) URLScan.
    """
    base = analyze_with_fallback(url)
    if do_urlscan:
        base = enrich_with_urlscan(base)
    return base


def compare_and_score(legit_data: dict, phish_data: dict) -> dict:
    """
    Compare two websites' extracted features.
    Output: comparison dict, risk score, readable % score, and log path.
    """
    diffs = compare_dicts(legit_data, phish_data)
    total, maximum = compute_risk_score(diffs)
    log_path = log_score_details(diffs)

    return {
        "comparisons": diffs,
        "raw_score": (total, maximum),
        "risk_score": human_readable_score(total, maximum),
        "log_file": log_path
    }


if __name__ == "__main__":
    url = input("URL to analyze: ").strip()
    result = full_analysis(url, use_browser=False, do_urlscan=True)
    print(json.dumps(result, indent=2, default=str))

