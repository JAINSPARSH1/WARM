# WARM: Web Artefact-based Risk Mapper
[![CI](https://github.com/<your-org>/warm-risk-mapper/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/warm-risk-mapper/actions)
[![PyPI](https://img.shields.io/pypi/v/warm-risk-mapper.svg)](https://pypi.org/project/warm-risk-mapper/)
[![Coverage](https://img.shields.io/codecov/c/github/<your-org>/warm-risk-mapper)](https://codecov.io/gh/<your-org>/warm-risk-mapper)

Threat Intelligence tool to compare and analyze phishing vs legit sites.

pip install warm-risk-mapper
warm -b https://example.com -t https://phish.com -k $URLSCAN_KEY
