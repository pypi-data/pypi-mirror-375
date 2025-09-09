from pyforcis.devices import get_devices, find_device_for_file

def test_devices_lookup():
    devices = get_devices()
    assert any(d["id"] == "net" for d in devices)
    assert find_device_for_file("FORCIS_net_20240101.csv") == "net"
    assert find_device_for_file("unrelated_file.csv") is None