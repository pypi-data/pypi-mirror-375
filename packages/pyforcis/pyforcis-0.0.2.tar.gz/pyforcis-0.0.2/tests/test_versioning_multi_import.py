import pyforcis as pf

def test_list_versions_function_exists():
    assert callable(pf.list_versions)