import pytest
from warm.core.analyzer import Analyzer

@pytest.fixture
def minimal_urls(tmp_path, monkeypatch):
    # Monkeypatch submodules to return fixed artifact dicts
    monkeypatch.setattr("warm.core.fetcher.Fetcher.fetch", lambda self: type("R", (), {"html": "", "status_code":200}))
    fake_art = {"f1":{"value":1}, "f2":{"value":2}}
    monkeypatch.setattr("warm.core.extractor.Extractor.extract", lambda self: fake_art)
    monkeypatch.setattr("warm.core.comparator.Comparator.diff", lambda a,b: {"f1":{"match":True},"f2":{"match":False}})
    monkeypatch.setattr("warm.core.scorer.Scorer.compute", lambda self, d: (50,"SUSPICIOUS"))
    return Analyzer("a","b")

def test_analyzer_run(minimal_urls):
    res = minimal_urls.run()
    assert res.risk == 50
    assert res.label == "SUSPICIOUS"

