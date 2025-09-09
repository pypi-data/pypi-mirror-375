from pathlib import Path
import os

_OVERRIDE = os.environ.get("PYFORCIS_CACHE_DIR")
if _OVERRIDE:
    CACHE_DIR = Path(_OVERRIDE).expanduser().resolve()
else:
    CACHE_DIR = Path.home() / ".cache" / "pyforcis"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

ZENODO_RECORD_ID = "7390791"
USER_AGENT = "pyforcis/0.3.4 (+https://github.com/)"