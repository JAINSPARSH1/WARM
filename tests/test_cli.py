import subprocess
import json

def test_cli_help():
    proc = subprocess.run(["warm","--help"], capture_output=True)
    assert proc.returncode == 0
    assert b"Web Artefact-based Risk Mapper" in proc.stdout

def test_cli_end_to_end(tmp_path):
    # Create a dummy baseline file
    baseline = tmp_path / "b.html"
    baseline.write_text("<html></html>")
    # Similarly target. Then call: warm -b file://... -t file://...
    proc = subprocess.run([
        "warm","-b", f"file://{baseline}", "-t", f"file://{baseline}"
    ], capture_output=True)
    assert b"Risk Score" in proc.stdout

