import pytest
from pathlib import Path
from pyforcis.dataset import Dataset, Schema
from pyforcis.parquetio import jsonl_to_parquet, parquet_to_jsonl

@pytest.mark.skipif("pyarrow" not in __import__('sys').modules, reason="Requires pyarrow already imported")
def test_parquet_roundtrip(tmp_path: Path):
    path = tmp_path / "data.jsonl"
    ds = Dataset(
        [{"year": 2000, "species": "A", "count": 10}],
        Schema(["year","species","count"])
    )
    ds.to_jsonl(path)
    pq_path = tmp_path / "data.parquet"
    jsonl_to_parquet(path, pq_path)
    out_path = tmp_path / "out.jsonl"
    parquet_to_jsonl(pq_path, out_path)
    assert out_path.read_text().strip() != ""