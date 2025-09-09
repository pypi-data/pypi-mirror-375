"""Minimal pyforcis core: versioning, download, formats, cache integrity, devices.

Version resolution behavior
---------------------------
Public APIs that accept (version / recid / doi) selectors (e.g. download_forcis_db,
download_forcis_file, get_version_metadata) will automatically use the latest
available FORCIS release when all selectors are omitted. Precedence when multiple
are supplied: recid > doi > version.
Use get_version_index(force=True) before calling if you need a freshly refreshed index.
"""
from .versioning import (
    list_versions,
    get_version_index,
    get_version_metadata,
    download_forcis_db,
    download_forcis_file,
    get_available_versions,
)
from .parquetio import jsonl_to_parquet, parquet_to_jsonl
from .cache import get_cache_info, clear_cache, record_download
from .devices import get_devices, find_device_for_file

# NOTE: Single source of truth for the package version is pyproject.toml.
# __version__ is resolved dynamically at runtime so only pyproject.toml needs updating.
try:  # Python 3.8+ importlib.metadata
    from importlib.metadata import version as _pkg_version  # type: ignore
except Exception:  # pragma: no cover
    _pkg_version = lambda _name: "0.0.0"  # fallback

__all__ = [
    "list_versions", "get_version_index", "get_version_metadata",
    "download_forcis_db", "download_forcis_file", "get_available_versions",
    "jsonl_to_parquet", "parquet_to_jsonl",
    "get_cache_info", "clear_cache", "record_download",
    "get_devices", "find_device_for_file"
]
try:
    __version__ = _pkg_version("pyforcis")
except Exception:  # pragma: no cover
    __version__ = "0.0.0"