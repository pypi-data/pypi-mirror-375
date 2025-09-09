import sys
import json
import pyforcis.cli as cli_mod

def test_cli_list_devices_json(capsys):
    argv_backup = sys.argv
    sys.argv = ["pyforcis", "--json", "--plain", "list-devices"]
    try:
        cli_mod.main()
    finally:
        sys.argv = argv_backup
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    ids = {d["id"] for d in data}
    assert {"net", "pump", "trap", "cpr_south", "cpr_north"}.issubset(ids)