# WARM: Web Artefact-based Risk Mapper  
[![CI](https://github.com/JAINSPARSH1/WARM/actions/workflows/ci.yml/badge.svg)](https://github.com/JAINSPARSH1/WARM/actions) [![Coverage](https://img.shields.io/codecov/c/github/JAINSPARSH1/WARM)](https://codecov.io/gh/JAINSPARSH1/WARM)  

> **Status:** 🚧 Ongoing Masters-level research project — under active development  

**WARM** is a Python CLI toolkit that “actively fingerprints” any webpage across multiple layers, enriches those artefacts with threat-intelligence feeds, and distills everything into a **single composite hash** (“site signature”). That signature powers both ultra-fast signature lookup and supervised ML classification, yielding a transparent, explainable risk score (0–100%) to catch zero-day phishing and malicious sites before traditional blocklists update.

---

## 📖 Table of Contents  
1. [Motivation](#motivation)  
2. [Project Vision & Objectives](#project-vision--objectives)  
3. [Key Features](#key-features)  
4. [System Architecture](#system-architecture)  
5. [Composite Hashing & ML](#composite-hashing--ml)  
6. [Getting Started](#getting-started)  
7. [Usage Examples](#usage-examples)  
8. [Configuration](#configuration)  
9. [Project Structure](#project-structure)  
10. [Development & Testing](#development--testing)  
11. [Roadmap & Future Work](#roadmap--future-work)  
12. [Acknowledgements](#acknowledgements)  
13. [License](#license)  

---

## 🎯 Motivation  
- **Phishing is rising:** Over one-third of breaches in 2024 began with phishing campaigns spinning up disposable domains and reusing “kits.”  
- **Blocklists lag:** Static URL reputation services can’t keep up with rapid domain churn.  
- **Opaque ML:** High-accuracy black-box models provide little insight, hindering SOC response.  

**WARM** addresses these gaps by combining live, multi-modal artefact extraction with threat-intel enrichment and an explainable scoring engine.

---

## 🚀 Project Vision & Objectives  
1. **Interactive Fetching:** Fetch via HTTP(S), fallback to headless browser (Playwright) for dynamic content.  
2. **Artefact Extraction:** Capture content, structure, resource, transport, and infra signals.  
3. **Threat-Intel Enrichment:** Augment artefacts with VirusTotal, URLScan.io, Shodan, OTX, IPInfo.  
4. **Composite Hashing:** Normalize & concatenate all artefacts + TI flags → SHA-256 “site signature.”  
5. **Dual Detection Modes:**  
   - **Lookup:** O(1) SQLite lookup of known benign/phish signatures  
   - **ML Prediction:** Random Forest/XGBoost model on composite signatures  
6. **Explainable Scoring:** Weighted mismatches + model confidence → final risk score with per-feature breakdown.

---

## ✨ Key Features  
- **Content & Structure:** HTML SHA-256 & ssdeep, DOM metrics, form counts  
- **Resources & Visuals:** CSS/JS count, favicon mmh3 + URL, optional screenshot hash  
- **Transport & Infra:** TLS Cert details & JARM, DNS TTL, WHOIS age, ASN  
- **Threat-Intel Flags:** VirusTotal verdicts, URLScan tech stack, Shodan banners, OTX pulses  
- **Composite Hashing:** Single canonical fingerprint for fast lookup & ML  
- **Explainability:** Per-feature weight breakdown in CLI output & JSON logs  
- **Extensible Outputs:** Rich CLI table, JSON report, single-row CSV for dataset building  

---

## 🏗 System Architecture  

```mermaid
flowchart LR
  subgraph Offline_Training["Offline Training"]
    A[Labelled URLs] --> B[Extract & Combine]
    B --> C[SQLite Signature Store]
    C --> D[Train ML Model]
    D --> E[Persist Model]
  end

  subgraph Online_Detection["Online Detection"]
    F[User Input: URL] --> G[Fetcher]
    G --> H[Extractor]
    H --> I[TI Enrichment]
    I --> J[Composite Hashing]
    J --> K{Signature in Store?}
    K -->|Yes| L[Lookup Verdict]
    K -->|No| M[ML Prediction]
    L --> N[Explainable Scoring]
    M --> N
    N --> O[CLI / JSON / CSV Output]
  end

  E -.-> M
🔐 Composite Hashing & ML Integration
Normalization: Convert each artefact & TI flag to key=value strings in fixed order.

Concatenation: Join with | delimiter to form canonical fingerprint.

Hashing: Compute SHA-256 → 64-hex “site signature.”

Lookup Mode: Instant SQLite lookup if signature known.

ML Mode: Feed signature vector into pre-trained Random Forest/XGBoost for classification.

Explainability: Map model confidence & weighted mismatches back to original features.

⚙️ Getting Started
Prerequisites
Python ≥3.9

(Optional) Environment variables:

bash
Copy
Edit
export URLSCAN_API_KEY="<your_key>"
export VIRUSTOTAL_API_KEY="<your_key>"
Installation
bash
Copy
Edit
git clone https://github.com/JAINSPARSH1/WARM.git
cd WARM
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
🖥 Usage Examples
Basic Signature Lookup
bash
Copy
Edit
warm -b https://example.com -t https://suspicious.com
With Threat-Intel Enrichment & JSON Output
bash
Copy
Edit
warm \
  --baseline https://bank.com \
  --target  https://phishingsite.com \
  --urlscan-key $URLSCAN_API_KEY \
  --output report.json
🛠 Configuration
All tunables in src/warm/config.py:

python
Copy
Edit
METRIC_WEIGHTS = {
  "favicon_hash": 0.20,
  "tls_jarm":     0.15,
  "html_ssdeep":  0.10,
  # ...
}
THRESHOLDS = {
  "benign_max":     25,
  "suspicious_max": 60,
  "malicious_min":  61,
}
Override via edits or future CLI flags.

📂 Project Structure
bash
Copy
Edit
WARM/
├── .github/            # CI workflows
├── data/               # cache & example logs
├── src/warm/
│   ├── main.py         # CLI entrypoint
│   ├── config.py       # global settings & weights
│   └── core/
│       ├── fetcher.py
│       ├── extractor.py
│       ├── tls_whois.py
│       ├── urlscan.py
│       ├── comparator.py
│       └── scorer.py
├── tests/              # pytest modules
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── setup.cfg
├── pyproject.toml
└── CHANGELOG.md
✅ Development & Testing
pytest for unit tests: fetcher, extractor, TLS/WHOIS, comparator, scorer, analyzer, CLI

Black, isort, flake8 for code style

GitHub Actions CI across Python 3.9–3.11

🛣 Roadmap & Future Work
 Full VirusTotal API integration & incremental updates

 Bulk dataset builder (.csv export) for advanced ML training

 Online incremental learning pipeline for automatic model refresh

 Browser-extension proof-of-concept for in-page warnings

 Vision-based screenshot OCR & UI similarity detection

 Web dashboard & PDF export for SOC reporting

🙏 Acknowledgements
Verizon DBIR 2024 for phishing statistics

Open-source threat-intel APIs: VirusTotal, URLScan.io, Shodan, OTX, IPInfo

📜 License
MIT © 2025 Sparsh M. Jain
