#!/usr/bin/env python3
# WARM/core/urlscan.py — urlscan.io integration for additional threat intel

import os
import time
import requests
import warnings

from warm.core.config import (
    URLSCAN_API_KEY,
    URLSCAN_BASE,
    URLSCAN_POLL_INTERVAL,
    URLSCAN_MAX_RETRIES,
    HEADERS
)

API_HEADERS = HEADERS.copy()
if URLSCAN_API_KEY:
    API_HEADERS["API-Key"] = URLSCAN_API_KEY
else:
    warnings.warn("⚠️  URLSCAN_API_KEY is not set. URLScan functionality will be skipped.")

def submit_scan(target_url: str, visibility: str = "unlisted", tags: list = None) -> str:
    """
    Submit a URL for scanning on urlscan.io.

    Args:
        target_url: URL to scan
        visibility: public, unlisted, or private
        tags: list of tags (optional)

    Returns:
        UUID of the scan
    """
    if not URLSCAN_API_KEY:
        raise RuntimeError("URLSCAN_API_KEY not set in config.py")

    payload = {
        "url": target_url,
        "visibility": visibility,
        "tags": tags or ["warm-scan"]
    }

    endpoint = f"{URLSCAN_BASE}/scan/"
    response = requests.post(endpoint, headers=API_HEADERS, json=payload, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(f"[!] Scan submission failed: {response.status_code} {response.text}")

    result = response.json()
    return result["uuid"]

def fetch_scan_result(uuid: str) -> dict:
    """
    Poll urlscan.io until scan result is ready.

    Args:
        uuid: Scan UUID

    Returns:
        JSON result dict
    """
    endpoint = f"{URLSCAN_BASE}/result/{uuid}/"

    for attempt in range(1, URLSCAN_MAX_RETRIES + 1):
        response = requests.get(endpoint, headers=API_HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            time.sleep(URLSCAN_POLL_INTERVAL)
        else:
            raise RuntimeError(f"[!] Unexpected error while polling result: {response.status_code}")
    
    raise TimeoutError(f"URLScan result not ready after {URLSCAN_MAX_RETRIES} attempts")

def scan_url(target_url: str) -> dict:
    """
    Submit → Poll → Return result.

    Args:
        target_url: URL to scan

    Returns:
        Full scan JSON result
    """
    uuid = submit_scan(target_url)
    return fetch_scan_result(uuid)

