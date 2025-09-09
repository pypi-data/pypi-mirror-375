from __future__ import annotations
import time, json, hashlib
from pathlib import Path
from typing import Dict, Any
from .config import CACHE_DIR

INDEX_PATH = CACHE_DIR / "download_index.json"

def _load_index() -> Dict[str, Any]:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {}

def _save_index(idx: Dict[str, Any]):
    INDEX_PATH.write_text(json.dumps(idx, indent=2), encoding="utf-8")

def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def record_download(key: str, path: Path, etag: str | None = None):
    idx = _load_index()
    entry = {
        "path": str(path),
        "size": path.stat().st_size,
        "sha256": sha256sum(path),
        "etag": etag,
        "timestamp": time.time()
    }
    idx[key] = entry
    _save_index(idx)
    return entry

def get_cache_info() -> Dict[str, Any]:
    return _load_index()

def clear_cache():
    idx = _load_index()
    for meta in idx.values():
        p = Path(meta["path"])
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass
    if INDEX_PATH.exists():
        INDEX_PATH.unlink()