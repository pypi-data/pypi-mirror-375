from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Iterable, Optional, Sequence
import json, csv, time, math
from copy import deepcopy

Row = Dict[str, Any]

@dataclass(frozen=True)
class Schema:
    fields: List[str]

@dataclass
class Provenance:
    version: Optional[str] = None
    source: Optional[str] = None
    checksum: Optional[str] = None
    created_ts: float = field(default_factory=time.time)
    history: List[str] = field(default_factory=list)
    def add(self, entry: str):
        self.history.append(entry)

@dataclass
class Dataset:
    rows: List[Row]
    schema: Schema
    provenance: Provenance = field(default_factory=Provenance)
    def select(self, columns: Iterable[str]) -> "Dataset":
        cols = list(columns)
        data = [{k: r.get(k) for k in cols} for r in self.rows]
        ds = Dataset(data, Schema(cols), deepcopy(self.provenance))
        ds.provenance.add(f"select({cols})")
        return ds
    def filter(self, predicate: Callable[[Row], bool], label: str = "filter") -> "Dataset":
        data = [r for r in self.rows if predicate(r)]
        ds = Dataset(data, self.schema, deepcopy(self.provenance))
        ds.provenance.add(label)
        return ds
    def mutate(self, **computations: Callable[[Row], Any]) -> "Dataset":
        new_rows: List[Row] = []
        # Preserve original field order; append any new computed fields on first appearance.
        new_fields_list = list(self.schema.fields)
        existing = set(new_fields_list)
        for row in self.rows:
            nr = dict(row)
            for k, func in computations.items():
                nr[k] = func(row)
                if k not in existing:
                    new_fields_list.append(k)
                    existing.add(k)
            new_rows.append(nr)
        ds = Dataset(new_rows, Schema(new_fields_list), deepcopy(self.provenance))
        ds.provenance.add(f"mutate({list(computations.keys())})")
        return ds
    def melt(self, id_vars: List[str], value_vars: List[str],
             var_name: str = "variable", value_name: str = "value") -> "Dataset":
        out: List[Row] = []
        for r in self.rows:
            base = {k: r.get(k) for k in id_vars}
            for vv in value_vars:
                row = dict(base); row[var_name] = vv; row[value_name] = r.get(vv)
                out.append(row)
        fields = list(dict.fromkeys(id_vars + [var_name, value_name]))
        ds = Dataset(out, Schema(fields), deepcopy(self.provenance))
        ds.provenance.add(f"melt({len(value_vars)})")
        return ds
    def to_jsonl(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for r in self.rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    def head(self, n: int = 5) -> "Dataset":
        return Dataset(self.rows[:n], self.schema, deepcopy(self.provenance))
    def __len__(self):
        return len(self.rows)
    # --- New helpers -----------------------------------------------------
    def _col_values(self, name: str) -> List[Any]:
        return [r.get(name) for r in self.rows]
    @staticmethod
    def _infer_type(values: Sequence[Any]) -> str:
        non_null = [v for v in values if v is not None]
        if not non_null:
            return "null"
        # Distinguish bool before int
        if all(isinstance(v, bool) for v in non_null):
            return "bool"
        # If any non-bool int
        if all(isinstance(v, (int, bool)) and not isinstance(v, bool) or isinstance(v, bool) for v in non_null):
            # mixture of int/bool counts as int if at least one pure int
            if any(isinstance(v, int) and not isinstance(v, bool) for v in non_null):
                return "int"
        # Numeric (float)
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in non_null):
            if any(isinstance(v, float) and (not math.isnan(v)) for v in non_null):
                return "float"
            return "int"
        if all(isinstance(v, (str,)) for v in non_null):
            return "str"
        if all(isinstance(v, (dict, list)) for v in non_null):
            return "json"
        return "mixed"
    def describe(self, max_unique: int = 50, sample: int = 3) -> List[Dict[str, Any]]:
        """Return lightweight per-column summary.

        Each entry: field, non_null, nulls, distinct (capped), type, sample_values.
        No heavy statistics (keeps dependency-light). Designed for quick schema peeks.
        """
        out: List[Dict[str, Any]] = []
        total = len(self.rows)
        for name in self.schema.fields:
            vals = self._col_values(name)
            non_null_vals = [v for v in vals if v is not None]
            nn = len(non_null_vals)
            distinct_vals = []
            seen = set()
            overflow = False
            for v in non_null_vals:
                key = json.dumps(v, sort_keys=True, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                if key not in seen:
                    seen.add(key)
                    distinct_vals.append(v)
                if len(distinct_vals) > max_unique:
                    overflow = True
                    break
            distinct_count = f">{max_unique}" if overflow else len(distinct_vals)
            inferred = self._infer_type(non_null_vals)
            out.append({
                "field": name,
                "non_null": nn,
                "nulls": total - nn,
                "distinct": distinct_count,
                "type": inferred,
                "sample_values": distinct_vals[:sample]
            })
        return out
    def to_parquet(self, path):
        """Write dataset to Parquet (requires pyarrow)."""
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError as e:
            raise ImportError("pyarrow required for to_parquet()") from e
        cols = {k: [r.get(k) for r in self.rows] for k in self.schema.fields}
        table = pa.table(cols)
        path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, path)
    def to_feather(self, path):
        """Write dataset to Feather (requires pyarrow)."""
        try:
            import pyarrow as pa
            import pyarrow.feather as feather
        except ImportError as e:
            raise ImportError("pyarrow required for to_feather()") from e
        cols = {k: [r.get(k) for r in self.rows] for k in self.schema.fields}
        table = pa.table(cols)
        path.parent.mkdir(parents=True, exist_ok=True)
        feather.write_feather(table, path)

def load_jsonl(path, limit: Optional[int] = None) -> Dataset:
    rows: List[Row] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.strip():
                rows.append(json.loads(line))
            if limit and i + 1 >= limit:
                break
    fields = sorted({k for r in rows for k in r.keys()})
    return Dataset(rows, Schema(fields))

def load_csv(path, limit: Optional[int] = None) -> Dataset:
    rows: List[Row] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            rows.append(row)
            if limit and i + 1 >= limit:
                break
    fields = reader.fieldnames or []
    return Dataset(rows, Schema(list(fields)))