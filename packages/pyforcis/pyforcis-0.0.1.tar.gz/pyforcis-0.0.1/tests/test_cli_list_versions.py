import json
import sys
import pyforcis.cli as cli_mod
import pyforcis.versioning as versioning

def test_cli_list_versions_plain_json(capsys, monkeypatch):
    fake_index = [
        {"version":"10","recid":"999","publication_date":"2025-01-01","files":[{"key":"a.csv","url":"https://zenodo.org/a"}],"doi":"10.5281/zenodo.999","access_right":"open"},
        {"version":"09","recid":"998","publication_date":"2024-12-01","files":[{"key":"b.csv","url":"https://zenodo.org/b"}],"doi":"10.5281/zenodo.998","access_right":"restricted"},
        {"version":"08","recid":"997","publication_date":"2024-11-01","files":[{"key":"c.csv","url":"https://zenodo.org/c"}],"doi":"10.5281/zenodo.997","access_right":"open"},
    ]
    monkeypatch.setattr(versioning, "get_version_index", lambda force=False: fake_index)
    argv_backup = sys.argv
    sys.argv = ["pyforcis", "--plain", "--json", "list-versions"]
    try:
        cli_mod.main()
    finally:
        sys.argv = argv_backup
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert len(data) == 3
    assert data[0]["version"] == "10"
    # Access field propagated
    assert data[0]["access_right"] == "open"