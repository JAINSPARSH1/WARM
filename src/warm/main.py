#!/usr/bin/env python3
# WARM/main.py — Entry point for WARM CLI tool

import os
from urllib.parse import urlparse
from rich.console import Console
from rich.rule import Rule
import argparse
from warm.core.analyzer import full_analysis, compare_and_score
from warm.core.comparator import render_comparison

console = Console(force_terminal=True)

def normalize_url(url: str) -> str:
    """
    Ensure URL includes a scheme. If missing, prepend https://
    """
    url = url.strip()
    if not url:
        return ""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
    return url

def get_url(prompt: str) -> str:
    """
    Prompt user until a valid HTTP/HTTPS URL is entered.
    """
    while True:
        raw = input(prompt)
        url = normalize_url(raw)
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return url
        console.print("  › Invalid URL. Try again", style="red")

def get_urlscan_choice() -> bool:
    """
    Prompt to ask if URLScan enrichment should be enabled.
    """
    choice = input("Run URLScan enrichment? [Y/N]: ").strip().lower()
    return choice == "y"

def cli():
    """Console entry‑point: parse args and run non‑interactive analysis."""
    parser = argparse.ArgumentParser(
        prog="warm",
        description="CLI toolkit for fingerprinting websites & computing explainable risk scores"
    )

    parser.add_argument(
        "--baseline", "-b",
        required=True,
        help="URL of the legitimate (baseline) site"
    )
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="URL of the phishing (target) site"
    )
    parser.add_argument(
        "--urlscan", "-u",
        action="store_true",
        help="Enable URLScan enrichment"
    )
    parser.add_argument(
        "--browser", "-B",
        action="store_true",
        help="Enable Selenium/browser‑based analysis"
    )

    args = parser.parse_args()

    console.print("\n=== WARM: Web Artefact‑based Risk Mapper ===\n", style="bold cyan")

    baseline_url = normalize_url(args.baseline)
    target_url = normalize_url(args.target)

    console.print(f"→ Analyzing [green]LEGITIMATE[/green] site: {baseline_url}")
    data_legit = full_analysis(
        baseline_url,
        use_browser=args.browser,
        do_urlscan=args.urlscan
    )

    console.print(f"→ Analyzing [red]PHISHING[/red] site:    {target_url}")
    data_phish = full_analysis(
        target_url,
        use_browser=args.browser,
        do_urlscan=args.urlscan
    )

    console.print()
    console.print(Rule("Comparison Results", style="magenta"))
    console.print()
    render_comparison(
        title_a="LEGITIMATE",
        data_a=data_legit,
        title_b="PHISHING",
        data_b=data_phish,
        ignore_keys=[]
    )

    console.print(Rule("Risk Score", style="red"))
    result = compare_and_score(data_legit, data_phish)
    console.print(f"[bold]Overall risk of phishing:[/bold] {result['risk_score']}")
    console.print(f"[blue]Score breakdown logged to:[/blue] {result['log_file']}\n")


def main():
    console.print("\n=== WARM: Web Artefact-based Risk Mapper ===\n", style="bold cyan")

    legit_url = get_url("Enter legitimate site URL: ")
    phish_url = get_url("Enter phishing site URL: ")
    console.print()

    use_urlscan = get_urlscan_choice()
    console.print()

    console.print(f"→ Analyzing [green]LEGITIMATE[/green] site: {legit_url}")
    data_legit = full_analysis(legit_url, use_browser=False, do_urlscan=use_urlscan)

    console.print(f"→ Analyzing [red]PHISHING[/red] site:    {phish_url}")
    data_phish = full_analysis(phish_url, use_browser=False, do_urlscan=use_urlscan)

    console.print()
    console.print(Rule("Comparison Results", style="magenta"))
    console.print()

    render_comparison(
        title_a="LEGITIMATE",
        data_a=data_legit,
        title_b="PHISHING",
        data_b=data_phish,
        ignore_keys=[]
    )

    console.print(Rule("Risk Score", style="red"))
    result = compare_and_score(data_legit, data_phish)

    console.print(f"[bold]Overall risk of phishing:[/bold] {result['risk_score']}")
    console.print(f"[blue]Score breakdown logged to:[/blue] {result['log_file']}\n")

if __name__ == "__main__":
    cli()

