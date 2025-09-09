import pyforcis.versioning as vz

def test_resolve_version_entry_internal():
    fake_index = [
        {"version": "10", "version_int": 10, "recid": "555", "doi": "10.5281/zenodo.555", "files":[]},
        {"version": "09", "version_int": 9, "recid": "444", "doi": "10.5281/zenodo.444", "files":[]},
    ]
    e1 = vz._resolve_version_entry(version="09", recid=None, doi=None, index=fake_index)
    assert e1["recid"] == "444"
    e2 = vz._resolve_version_entry(version=None, recid=None, doi="10.5281/zenodo.555", index=fake_index)
    assert e2["version"] == "10"
    e3 = vz._resolve_version_entry(version=None, recid=None, doi=None, index=fake_index)
    assert e3["version"] == "10"