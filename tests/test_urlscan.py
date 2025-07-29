import pytest
from warm.core.urlscan import URLScan

def test_urlscan_no_key_raises():
    with pytest.raises(ValueError):
        URLScan(api_key=None)

