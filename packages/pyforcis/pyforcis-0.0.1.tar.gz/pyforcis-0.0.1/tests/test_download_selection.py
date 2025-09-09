import pyforcis.versioning as vz

def test_select_files_for_sources():
    entry = {
        "version": "10",
        "files": [
            {"key": "FORCIS_net_01012025.csv"},
            {"key": "FORCIS_cpr_north_01012025.csv"},
            {"key": "FORCIS_trap_01012025.csv"},
            {"key": "FORCIS_taxonomy_levels.xlsx"},
        ],
    }
    subset = vz.select_files_for_sources(entry, sources=["net","trap"])
    keys = {f["key"] for f in subset}
    assert "FORCIS_net_01012025.csv" in keys
    assert "FORCIS_trap_01012025.csv" in keys
    assert "FORCIS_cpr_north_01012025.csv" not in keys