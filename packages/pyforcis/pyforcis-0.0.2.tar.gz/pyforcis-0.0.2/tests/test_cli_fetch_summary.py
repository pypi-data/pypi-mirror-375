import sys
from pathlib import Path
import pyforcis.cli as cli_mod
import pyforcis.versioning as versioning

def test_cli_fetch_summary_only(capsys, monkeypatch, tmp_path):
    fake_entry = {
        "version": "10",
        "recid": "123",
        "files": [
            {"key": "FORCIS_net_fake.csv", "size": 4, "url": "https://zenodo.org/net.csv"},
            {"key": "FORCIS_pump_fake.csv", "size": 6, "url": "https://zenodo.org/pump.csv"}
        ]
    }
    monkeypatch.setattr(versioning, "get_version_index", lambda force=False: [fake_entry])
    monkeypatch.setattr(versioning, "_resolve_version_entry", lambda v,r,d,i: fake_entry)

    def fake_download(file_key, version=None, recid=None, doi=None, force=False, progress_cb=None):
        version_dir = Path.home() / ".cache" / "pyforcis" / "downloads" / "10"
        version_dir.mkdir(parents=True, exist_ok=True)
        target = version_dir / file_key
        if not target.exists() or force:
            target.write_text("x"*10)
        if progress_cb:
            progress_cb(10, 10, file_key, False)
        return target
    monkeypatch.setattr(versioning, "download_forcis_file", fake_download)

    argv_backup = sys.argv
    sys.argv = ["pyforcis", "--plain", "--summary-only", "fetch", "--version", "10", "--sources", "net,pump"]
    try:
        cli_mod.main()
    finally:
        sys.argv = argv_backup
    out = capsys.readouterr().out
    assert "FORCIS_net_fake.csv" in out
    assert "FORCIS_pump_fake.csv" in out