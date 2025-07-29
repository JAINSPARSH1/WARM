import pytest
from warm.core.extractor import Extractor

@pytest.fixture
def simple_html(tmp_path):
    f = tmp_path / "test.html"
    f.write_text("<html><body><p>hey</p></body></html>")
    return str(f)

def test_extractor_basic(simple_html):
    ext = Extractor(simple_html, from_file=True)
    artifacts = ext.extract()
    assert "html_sha256" in artifacts
    assert artifacts["dom_form_count"] == 0

