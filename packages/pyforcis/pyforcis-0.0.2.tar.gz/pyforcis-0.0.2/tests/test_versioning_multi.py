import pyforcis.versioning as vz

def test_version_index_structure(monkeypatch):
    fake_response = {
        "hits": {
            "hits": [
                {
                    "id": "123",
                    "metadata": {
                        "version": "10",
                        "doi": "10.5281/zenodo.123",
                        "publication_date": "2025-01-01",
                        "title": "FORCIS v10",
                        "access_right": "open",
                        "license": {"id": "cc-by-4.0"},
                    },
                    "files": [
                        {
                            "key": "FORCIS_net_01012025.csv",
                            "size": 100,
                            "checksum": "md5:abc",
                            "links": {"self": "https://example.org/net.csv"},
                        }
                    ],
                },
                {
                    "id": "122",
                    "metadata": {
                        "version": "09",
                        "doi": "10.5281/zenodo.122",
                        "publication_date": "2024-12-01",
                        "title": "FORCIS v09",
                        "access_right": "open",
                        "license": {"id": "cc-by-4.0"},
                    },
                    "files": [],
                },
                {
                    "id": "121",
                    "metadata": {
                        "version": "08",
                        "doi": "10.5281/zenodo.121",
                        "publication_date": "2024-11-01",
                        "title": "FORCIS v08",
                        "access_right": "open",
                        "license": {"id": "cc-by-4.0"},
                    },
                    "files": [],
                },
            ]
        }
    }
    monkeypatch.setattr(vz, "_fetch_json", lambda url: fake_response)
    idx = vz.get_version_index(force=True)
    assert len(idx) == 3
    assert idx[0]["version"] == "10"
    assert "files" in idx[0]
    versions = vz.list_versions(force=False)
    assert versions[:2] == ["10", "09"]