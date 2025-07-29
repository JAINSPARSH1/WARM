#!/usr/bin/env python3
# WARM/core/scorer.py — Compute a simple risk-of-phishiness score with logging

import os
import json
import datetime
from typing import Dict, Tuple, Any
from warm.core.config import METRIC_WEIGHTS as CONFIG_METRIC_WEIGHTS, DEFAULT_METRIC_WEIGHT

# Merged weights from config + custom overrides
WEIGHTS: Dict[str, float] = {
    **CONFIG_METRIC_WEIGHTS,
    "title_font": 2.0,  # heavier penalty for font mismatches
}

def metric_weight(metric: str) -> float:
    """Return the weight for a metric, fallback to default."""
    return WEIGHTS.get(metric, DEFAULT_METRIC_WEIGHT)

def compute_risk_score(
    comparisons: Dict[str, Tuple[Any, Any, bool]]
) -> Tuple[float, float]:
    """
    Calculates total and maximum possible risk scores.
    Only counts mismatches.
    """
    total = 0.0
    maximum = 0.0

    for metric, (_, _, match) in comparisons.items():
        weight = metric_weight(metric)
        maximum += weight
        if not match:
            total += weight

    return total, maximum

def human_readable_score(score: float, maximum: float) -> str:
    """
    Converts raw score to percentage string.
    """
    if maximum == 0:
        return "N/A"
    return f"{(score / maximum) * 100:.0f}%"

def make_serializable(value: Any) -> Any:
    """
    Ensures values like timedelta, datetime, etc. are stringified for JSON.
    """
    if isinstance(value, (datetime.timedelta, datetime.date, datetime.datetime)):
        return str(value)
    return value

def log_score_details(
    comparisons: Dict[str, Tuple[Any, Any, bool]],
    output_dir: str = "data/reports",
    filename_prefix: str = "log_"
) -> str:
    """
    Logs only mismatched metrics with weights and values.
    Returns the JSON log file path.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, f"{filename_prefix}{timestamp}.json")

    mismatches = {}

    for metric, (val_legit, val_phish, match) in comparisons.items():
        if not match:
            mismatches[metric] = {
                "legit": make_serializable(val_legit),
                "phish": make_serializable(val_phish),
                "weight": metric_weight(metric)
            }

    try:
        with open(log_path, "w") as f:
            json.dump(mismatches, f, indent=2)
    except Exception as e:
        print(f"[!] Error writing mismatch log file: {e}")
        return ""

    return log_path

def log_all_details(
    comparisons: Dict[str, Tuple[Any, Any, bool]],
    output_dir: str = "data/reports",
    filename_prefix: str = "full_log_"
) -> str:
    """
    Logs all comparisons (match + mismatch) to a file with match status.
    Returns the JSON log file path.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, f"{filename_prefix}{timestamp}.json")

    full_data = {}

    for metric, (val_legit, val_phish, match) in comparisons.items():
        full_data[metric] = {
            "legit": make_serializable(val_legit),
            "phish": make_serializable(val_phish),
            "match": match,
            "weight": metric_weight(metric)
        }

    try:
        with open(log_path, "w") as f:
            json.dump(full_data, f, indent=2)
    except Exception as e:
        print(f"[!] Error writing full comparison log: {e}")
        return ""

    return log_path

# 🔧 Developer test
if __name__ == "__main__":
    sample = {
        "html_sha256":  ("aaa", "bbb", False),
        "favicon_hash": ("111", "111", True),
        "dns_ips":      ("1.2.3.4", "5.6.7.8", False),
        "XFO":          ("DENY", "-", False),
        "title_font":   ("Arial", "Helvetica", False),
        "load_time":    (datetime.timedelta(seconds=1.5), datetime.timedelta(seconds=2.2), False),
        "whois_created_on": (
            datetime.date(2020, 1, 1),
            datetime.date(2024, 1, 1),
            False
        )
    }

    total, max_score = compute_risk_score(sample)
    print(f"Risk score: {total}/{max_score} → {human_readable_score(total, max_score)}")

    mismatch_log = log_score_details(sample)
    print(f"[+] Mismatches logged to: {mismatch_log}")

    full_log = log_all_details(sample)
    print(f"[+] Full comparison log: {full_log}")

