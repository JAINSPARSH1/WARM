import pytest
from warm.core.tls_whois import TLSWhois

def test_tls_whois_offline(monkeypatch):
    # Monkeypatch socket and whois lookups to return canned values
    class DummyCert:
        issuer = "Test CA"
        not_before = "20200101000000Z"
        not_after = "20230101000000Z"
    monkeypatch.setattr(TLSWhois, "fetch_cert", lambda self, _: DummyCert())
    tls = TLSWhois("example.com")
    data = tls.run()
    assert data["issuer"] == "Test CA"
    assert "tls_jarm" in data

