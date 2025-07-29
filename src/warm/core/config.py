#!/usr/bin/env python3
# WARM/config.py — Central configuration for WARM

import os

# ──────────────────────────── Fetcher Settings ──────────────────────────────

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}

FETCH_TIMEOUT       = 10
BROWSER_TIMEOUT     = 20

# ──────────────────────────── Urlscan Settings ──────────────────────────────

# Provide your API Key here or via environment variable
URLSCAN_API_KEY = os.getenv("URLSCAN_API_KEY", "01981e78-55fe-763f-bab9-e84b360a0177")
URLSCAN_BASE = "https://urlscan.io/api/v1"
URLSCAN_POLL_INTERVAL = 5  # seconds
URLSCAN_MAX_RETRIES = 10   # retries (max 50s wait)
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "WARM/1.0 (Phishing Detector)"
}

# ───────────────────────────── Scorer Settings ──────────────────────────────

DEFAULT_METRIC_WEIGHT = 1
METRIC_WEIGHTS = {
    "html_sha256":        5,
    "html_ssdeep":        4,
    "favicon_hash":       4,
    "dns_ips":            3,
    "DNS TTL":            2,
    "issuer":             3,
    "days_left":          1,
    "protocol":           1,
    "registrar":          2,
    "created_on":         2,
    "expiry_date":        2,
    "urlscan_verdict":    4,
    "urlscan_score":      3,
    "urlscan_domain":     2,
    "HSTS":               1,
    "CSP":                1,
    "XFO":                1,
    "XXP":                1,
    "XCTO":               1,
}

