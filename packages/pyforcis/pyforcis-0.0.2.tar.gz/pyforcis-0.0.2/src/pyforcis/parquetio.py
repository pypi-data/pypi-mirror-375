from __future__ import annotations
from pathlib import Path
import json

def jsonl_to_parquet(in_path: Path, out_path: Path):
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as e:
        raise ImportError("pyarrow required for parquet conversion") from e
    rows = []
    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        table = pa.table({})
    else:
        # Preserve first-seen column order for reproducibility.
        ordered_keys = []
        seen = set()
        for r in rows:
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    ordered_keys.append(k)
        cols = {k: [r.get(k) for r in rows] for k in ordered_keys}
        table = pa.table(cols)
    pq.write_table(table, out_path)

def parquet_to_jsonl(in_path: Path, out_path: Path):
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise ImportError("pyarrow required for parquet conversion") from e
    table = pq.read_table(in_path)
    cols = table.to_pydict()
    n = len(next(iter(cols.values()))) if cols else 0
    with out_path.open("w", encoding="utf-8") as f:
        for i in range(n):
            row = {k: v[i] for k, v in cols.items()}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")