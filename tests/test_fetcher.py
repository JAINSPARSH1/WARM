import responses
import pytest
from warm.core.fetcher import Fetcher

@responses.activate
def test_fetcher_requests(monkeypatch):
    url = "https://example.com"
    html = "<html><body>OK</body></html>"
    responses.add(responses.GET, url, body=html, status=200)

    fetcher = Fetcher(url)
    result = fetcher.fetch()
    assert html in result.html
    assert result.status_code == 200

