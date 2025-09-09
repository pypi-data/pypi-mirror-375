from __future__ import annotations
import json
import re
import urllib.error
import hashlib
import time
from urllib.request import urlopen, Request
from pathlib import Path
from typing import List, Dict, Optional, Iterable, Callable
from .config import CACHE_DIR, USER_AGENT
from .cache import record_download
from urllib.parse import urlparse

ZENODO_CONCEPT_REC_ID = "7390791"

SEARCH_URL_TEMPLATE = (
    "https://zenodo.org/api/records?"
    "q=conceptrecid:{concept}&all_versions=true&sort=mostrecent&size=200"
)

VERSIONS_INDEX_PATH = CACHE_DIR / "versions_index.json"
METADATA_DIR = CACHE_DIR / "metadata"
DOWNLOAD_DIR = CACHE_DIR / "downloads"

METADATA_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _fetch_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _parse_version_str(v: str | None) -> Optional[int]:
    if v is None:
        return None
    m = re.match(r"^(\d+)", v.strip())
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None

def _record_summary(hit: dict) -> dict:
    md = hit.get("metadata", {}) or {}
    version_str = md.get("version")
    version_num = _parse_version_str(version_str)
    recid = hit.get("id") or hit.get("recid")
    doi = md.get("doi") or hit.get("doi")
    publication_date = md.get("publication_date")
    access_right = md.get("access_right")
    license_id = (md.get("license") or {}).get("id")
    title = md.get("title")
    files = hit.get("files") or []
    file_list = [
        {
            "key": f.get("key"),
            "size": f.get("size"),
            "checksum": f.get("checksum"),
            "url": f.get("links", {}).get("self"),
        }
        for f in files
    ]
    return {
        "version": version_str,
        "version_int": version_num,
        "recid": recid,
        "doi": doi,
        "publication_date": publication_date,
        "access_right": access_right,
        "license": license_id,
        "title": title,
        "files": file_list,
    }

def _save_versions_index(index: List[dict]):
    # Embed a saved_at timestamp for potential future diagnostics (not used in logic yet)
    meta_wrapper = {"__saved_at": int(time.time()), "entries": index}
    VERSIONS_INDEX_PATH.write_text(json.dumps(meta_wrapper, indent=2), encoding="utf-8")

def _load_versions_index() -> Optional[List[dict]]:
    if not VERSIONS_INDEX_PATH.exists():
        return None
    try:
        raw = json.loads(VERSIONS_INDEX_PATH.read_text(encoding="utf-8"))
        # Backwards compatibility: older format is just a list
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict) and "entries" in raw:
            return raw.get("entries") or []
        return None
    except Exception:
        return None

def _metadata_cache_path(recid: str) -> Path:
    return METADATA_DIR / f"metadata_{recid}.json"

def _load_cached_metadata(recid: str) -> Optional[dict]:
    p = _metadata_cache_path(recid)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _cache_metadata(recid: str, data: dict):
    _metadata_cache_path(recid).write_text(json.dumps(data, indent=2), encoding="utf-8")

def _resolve_version_entry(version: Optional[str], recid: Optional[str], doi: Optional[str], index: List[dict]) -> dict:
    if recid:
        for entry in index:
            if entry["recid"] == recid:
                return entry
        raise ValueError(f"recid '{recid}' not found.")
    if doi:
        norm = doi.lower()
        for entry in index:
            if entry.get("doi", "").lower() == norm:
                return entry
        m = re.match(r".*zenodo\.(\d+)$", norm)
        if m:
            rid = m.group(1)
            for entry in index:
                if entry["recid"] == rid:
                    return entry
        raise ValueError(f"DOI '{doi}' not found.")
    if version:
        v_int = _parse_version_str(version)
        for entry in index:
            if entry["version"] == version or (v_int is not None and entry["version_int"] == v_int):
                return entry
    if not index:
        raise RuntimeError("No versions found.")
    return index[0]

MAX_INDEX_AGE_SECS = 7 * 24 * 3600  # 7 days

def _index_looks_suspicious(index: List[dict]) -> bool:
    # Basic structural heuristic
    if len(index) < 3:
        return True
    # Host sanity
    for entry in index:
        for f in entry.get("files", []):
            url = f.get("url")
            if not url:
                continue
            try:
                host = urlparse(url).netloc.lower()
            except Exception:
                continue
            if host == "example.org":
                return True
    # Age heuristic: if file older than threshold, refresh
    try:
        mtime = VERSIONS_INDEX_PATH.stat().st_mtime
        if (time.time() - mtime) > MAX_INDEX_AGE_SECS:
            return True
    except Exception:
        pass
    return False

def refresh_index() -> List[dict]:
    url = SEARCH_URL_TEMPLATE.format(concept=ZENODO_CONCEPT_REC_ID)
    data = _fetch_json(url)
    hits = (data.get("hits") or {}).get("hits") or []
    summaries = []
    for h in hits:
        try:
            summaries.append(_record_summary(h))
        except Exception:
            continue
    summaries = [s for s in summaries if s.get("version_int") is not None]
    summaries.sort(key=lambda x: x["version_int"], reverse=True)
    _save_versions_index(summaries)
    return summaries

def get_version_index(force: bool = False) -> List[dict]:
    if not force:
        cached = _load_versions_index()
        if cached and not _index_looks_suspicious(cached):
            return cached
    return refresh_index()

def list_versions(force: bool = False) -> List[str]:
    return [entry["version"] for entry in get_version_index(force=force)]

def get_available_versions(force: bool = False) -> List[str]:
    return list_versions(force=force)

def get_version_metadata(version: Optional[str] = None, recid: Optional[str] = None,
                         doi: Optional[str] = None, force: bool = False) -> dict:
    index = get_version_index(force=force)
    entry = _resolve_version_entry(version, recid, doi, index)
    rid = entry["recid"]
    if not force:
        cached = _load_cached_metadata(rid)
        if cached:
            return cached
    record_url = f"https://zenodo.org/api/records/{rid}"
    full = _fetch_json(record_url)
    _cache_metadata(rid, full)
    return full

def select_files_for_sources(entry: dict, sources: Optional[Iterable[str]] = None) -> List[dict]:
    files = entry.get("files") or []
    if not sources:
        return files
    # Use boundary-aware matching so short substrings do not produce accidental matches.
    import re
    regexes = [re.compile(rf"(?:^|[_/]){re.escape(s.lower())}(?:[_/]|$)") for s in sources]
    selected: List[dict] = []
    for f in files:
        key = f.get("key", "").lower()
        if any(rx.search(key) for rx in regexes):
            selected.append(f)
    return selected

def _parse_checksum_decl(decl: str) -> Optional[tuple[str, str]]:
    if not decl:
        return None
    if ":" in decl:
        algo, value = decl.split(":", 1)
        algo = algo.lower().strip()
        value = value.strip().lower()
        return algo, value
    # Fallback guess by length
    d = decl.lower().strip()
    if len(d) == 32:
        return ("md5", d)
    if len(d) == 40:
        return ("sha1", d)
    if len(d) == 64:
        return ("sha256", d)
    return None

def _hash_file(path: Path, algo: str) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _verify_checksum(path: Path, checksum_decl: Optional[str]) -> bool:
    parsed = _parse_checksum_decl(checksum_decl) if checksum_decl else None
    if not parsed:
        return True  # Nothing to verify
    algo, expected = parsed
    try:
        actual = _hash_file(path, algo)
    except ValueError:
        return True  # Unsupported algo: skip
    return actual.lower() == expected.lower()

def _stream_download(url: str, target: Path, file_key: str,
                     force: bool,
                     progress_cb: Optional[Callable[[int, Optional[int], str, bool], None]] = None,
                     chunk_size: int = 64 * 1024,
                     expected_checksum: Optional[str] = None,
                     retries: int = 3) -> bool:
    if target.exists() and not force:
        if progress_cb:
            sz = target.stat().st_size
            progress_cb(sz, sz, file_key, True)
        return False
    last_err = None
    for attempt in range(1, retries + 1):
        req = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urlopen(req, timeout=1800) as resp, target.open("wb") as out:
                total = resp.headers.get("Content-Length")
                total_int = int(total) if total and total.isdigit() else None
                downloaded = 0
                if progress_cb:
                    progress_cb(0, total_int, file_key, False)
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)
                    if progress_cb:
                        progress_cb(downloaded, total_int, file_key, False)
                etag = resp.headers.get("ETag")
            # Verify checksum if provided
            if not _verify_checksum(target, expected_checksum):
                target.unlink(missing_ok=True)
                raise RuntimeError(f"Checksum mismatch for {file_key}")
            record_download(file_key, target, etag=etag)
            return True
        except urllib.error.HTTPError as e:
            # Don't retry 4xx except maybe 408
            if e.code >= 500 or e.code in (408,):
                last_err = e
            else:
                raise
        except (urllib.error.URLError, RuntimeError) as e:
            last_err = e
        # Backoff before next attempt
        if attempt < retries:
            time.sleep(2 ** (attempt - 1))
    # Exhausted attempts
    if last_err:
        raise last_err
    return False

def download_forcis_file(file_key: str, version: Optional[str] = None,
                          recid: Optional[str] = None, doi: Optional[str] = None,
                          force: bool = False,
                          progress_cb: Optional[Callable[[int, Optional[int], str, bool], None]] = None) -> Path:
    """Download a single FORCIS file for the given version / recid / doi.

    Parameters
    ----------
    file_key : str
        Exact key (filename) as listed in the version index.
    version, recid, doi : Optional identifiers
        Resolution precedence: recid > doi > version. If none provided the latest version is used.
    force : bool
        If True, re-downloads the file even if it already exists locally. NOTE: This does NOT
        refresh the versions index. Call get_version_index(force=True) separately (or use the
        CLI option --refresh-index) if a fresh index listing is required.
    progress_cb : optional callable
        Callback receiving (downloaded_bytes, total_bytes|None, file_key, is_cached_flag).

    Returns
    -------
    Path
        Local filesystem path of the downloaded (or cached) file.
    """
    index = get_version_index()
    entry = _resolve_version_entry(version, recid, doi, index)
    version_str = entry["version"]
    target_file = None
    for f in entry["files"]:
        if f["key"] == file_key:
            target_file = f
            break
    if target_file is None:
        raise ValueError(f"File '{file_key}' not found in version {version_str}. Try --refresh-index or clear cache.")
    version_dir = DOWNLOAD_DIR / version_str
    version_dir.mkdir(parents=True, exist_ok=True)
    local_path = version_dir / file_key
    url = target_file["url"]
    try:
        # Support legacy monkeypatched _stream_download signatures in tests (without new params)
        try:
            _stream_download(url, local_path, file_key, force, progress_cb=progress_cb,
                             expected_checksum=target_file.get("checksum"))
        except TypeError:
            _stream_download(url, local_path, file_key, force, progress_cb=progress_cb)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            refreshed = refresh_index()
            entry2 = _resolve_version_entry(version, recid, doi, refreshed)
            for f in entry2.get("files", []):
                if f["key"] == file_key:
                    url = f.get("url")
                    try:
                        try:
                            _stream_download(url, local_path, file_key, force, progress_cb=progress_cb,
                                             expected_checksum=f.get("checksum"))
                        except TypeError:
                            _stream_download(url, local_path, file_key, force, progress_cb=progress_cb)
                        return local_path
                    except Exception:
                        break
            raise RuntimeError(
                f"404 downloading '{file_key}'. The cached index may be stale.\n"
                "Try: pyforcis refresh-index  or pyforcis cache-clear."
            ) from e
        raise
    return local_path

def download_forcis_db(version: Optional[str] = None, recid: Optional[str] = None,
                       doi: Optional[str] = None, sources: Optional[Iterable[str]] = None,
                       force: bool = False) -> Dict[str, Path]:
    """Download multiple FORCIS files for a resolved release.

    Resolution precedence (if multiple selectors provided): recid > doi > version.
    If all of (version, recid, doi) are None the latest available version (index[0])
    is used. To force refresh the version index before resolving, call
    get_version_index(force=True) yourself or invoke the CLI with --refresh-index
    prior to fetch.

    Parameters
    ----------
    version, recid, doi : optional str
        Selectors for the desired FORCIS release. Latest is used when omitted.
    sources : optional iterable of str
        Substring identifiers (e.g. ["net","trap"]). If omitted all files
        in the release are downloaded.
    force : bool
        Re-download even if a local cached copy exists.

    Returns
    -------
    dict
        Mapping of file_key -> local Path for successfully downloaded (or cached) files.
    """
    index = get_version_index()
    entry = _resolve_version_entry(version, recid, doi, index)
    version_str = entry["version"]
    files = select_files_for_sources(entry, sources=sources)
    if not files:
        raise RuntimeError(f"No files matched for version {version_str} with sources={sources}.")
    results: Dict[str, Path] = {}
    for f in files:
        key = f["key"]
        try:
            results[key] = download_forcis_file(file_key=key, version=version_str, force=force)
        except Exception:
            continue
    return results