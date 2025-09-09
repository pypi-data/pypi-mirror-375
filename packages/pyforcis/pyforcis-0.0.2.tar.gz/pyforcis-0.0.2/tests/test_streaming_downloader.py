import pyforcis.versioning as v

def test_stream_download_cached(monkeypatch):
    fake_entry = {
        "version":"10",
        "recid":"123",
        "files":[
            {"key":"foo.csv","size":3,"checksum":"md5:abc","url":"https://zenodo.org/foo.csv"}
        ]
    }
    monkeypatch.setattr(v, "get_version_index", lambda force=False: [fake_entry])
    monkeypatch.setattr(v, "_resolve_version_entry", lambda ver, recid, doi, index: fake_entry)
    calls = {"count":0}
    def fake_stream(url, target, file_key, force, progress_cb=None):
        calls["count"] += 1
        if force or not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("abc")
            if progress_cb:
                progress_cb(3, 3, file_key, False)
            return True
        else:
            if progress_cb:
                progress_cb(target.stat().st_size, target.stat().st_size, file_key, True)
            return False
    monkeypatch.setattr(v, "_stream_download", fake_stream)
    p1 = v.download_forcis_file("foo.csv", version="10")
    assert p1.exists()
    assert calls["count"] == 1
    p2 = v.download_forcis_file("foo.csv", version="10")
    assert calls["count"] == 2