# WARM: Web Artefact-based Risk Mapper

**Status:** 🚧 Ongoing Master’s-level research project

WARM is a Python CLI toolkit designed to detect and explain malicious or phishing web pages by:

1. **Actively fingerprinting** a target URL’s multi-modal artefacts (content, structure, transport, infrastructure).  
2. **Enriching** those artefacts with open-source threat-intelligence (VirusTotal, URLScan.io, Shodan, OTX, IPInfo).  
3. **Compressing** everything into a **single composite SHA-256 hash** (“site signature”).  
4. **Detecting** via ultra-fast SQLite signature lookup or a supervised ML model (Random Forest / XGBoost).  
5. **Explaining** each decision with per-feature weight breakdown and detailed JSON logs.



## Background & Motivation

- Phishing campaigns spin up disposable domains daily; static blocklists lag behind new threats.  
- Black-box ML offers good accuracy but little insight—analysts need to know **why** a site is flagged.  
- WARM combines rule-based mismatches and ML predictions in an explainable pipeline that fits SOC workflows.



## Key Features

- **Fetcher**: HTTP(S) requests + headless-browser fallback for dynamic sites.  
- **Extractor**:  
  - HTML SHA-256 and ssdeep fuzzy-hash  
  - DOM metrics (forms, inputs)  
  - Resource counts (CSS/JS/images) and favicon mmh3 hash  
- **TLS/WHOIS Module**:  
  - Certificate issuer, age, JARM fingerprint  
  - DNS A-record + TTL, WHOIS domain age, ASN lookup  
- **Threat-Intel Enrichment (optional)**:  
  VirusTotal URL verdicts, URLScan.io scan data, Shodan banners, OTX pulses, IPInfo metadata  
- **Composite Hashing**: Normalize all artefact values + TI flags → join with `|` → SHA-256 signature  
- **Detection Modes**:  
  - **Lookup**: O(1) SQLite match against known benign/phish signatures  
  - **ML Prediction**: Supervised model on signature vectors for unknown sites  
- **Explainable Scoring**: Weighted sum of mismatches + model confidence → 0–100% risk score  
- **Outputs**: CLI table, JSON report, CSV row for dataset building



## System Architecture




           ┌──────────────────┐
Offline: │ Labelled URLs │
Training └───┬────────────┬──┘
│ ↓
Extract & Combine Train ML Model
↓ ↓
SQLite Signature Store ─┘
│
┌────────────────┴────────────────┐
│ Online Detection (per URL) │
└──────────────┬─────────────────┘
↓
Fetcher
↓
Extractor
↓
Threat-Intel Enrichment
↓
Composite Hashing
↓
┌───────────┴───────────┐
│ Lookup? │ ML Model │
│ (SQLite) │ Prediction │
└────┬──────┴────────────┘
↓
Explainable Scoring & Output







## Installation

```
git clone https://github.com/JAINSPARSH1/WARM.git
cd WARM
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
Optional (Threat-Intel APIs)



export URLSCAN_API_KEY="…"
export VIRUSTOTAL_API_KEY="…"
Usage



# Basic signature lookup + explainable risk score
warm \
  --baseline https://example.com \
  --target  https://suspicious-site.test \
  [--urlscan-key $URLSCAN_API_KEY] \
  [--output report.json]
--baseline (or -b): Known-good URL

--target (or -t): URL under analysis

--urlscan-key (or -k): (Optional) URLScan.io API key

--output (or -o): Path to write JSON summary (default: stdout)

Configuration
All tunable parameters live in src/warm/config.py:

METRIC_WEIGHTS: per-feature mismatch weights (e.g. {"favicon_hash":0.2, …})

THRESHOLDS: risk thresholds (benign_max, suspicious_max, malicious_min)

TIMEOUTS, HEADERS, API KEYS

Adjust these to calibrate scoring and model behavior.

Project Structure



WARM/
├── src/warm/
│   ├── main.py      # CLI entry point
│   ├── config.py    # global settings & weights
│   └── core/
│       ├── fetcher.py
│       ├── extractor.py
│       ├── tls_whois.py
│       ├── urlscan.py
│       ├── comparator.py
│       └── scorer.py
├── data/            # cache & example JSON logs
├── tests/           # pytest suites per component
├── requirements.txt
├── setup.cfg        # entry point & packaging metadata
├── pyproject.toml   # project metadata & build config
└── CHANGELOG.md
Development & Testing



# Run unit tests
pytest

# Format & lint (locally)
black src tests
flake8 src tests
Roadmap & Future Work
Full VirusTotal and OTX enrichment

Bulk dataset exporter for advanced ML training

Incremental online learning for model refresh

Browser-extension prototype for in-page warnings

Screenshot OCR hashing for UI-similarity detection

Web dashboard & PDF reporting

Acknowledgements
Verizon DBIR 2024 for phishing statistics

Open-source APIs: VirusTotal, URLScan.io, Shodan, OTX, IPInfo

License
MIT © 2025 Sparsh M. Jain



