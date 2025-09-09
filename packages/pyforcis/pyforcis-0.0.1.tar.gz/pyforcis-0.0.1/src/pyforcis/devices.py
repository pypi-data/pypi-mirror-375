from __future__ import annotations
from typing import List, Dict

_DEVICES: List[Dict[str, str]] = [
    {
        "id": "net",
        "label": "Plankton Nets",
        "description": "Net tows with full raw/validated/lumped species taxonomy blocks.",
        "file_substring": "net",
    "notes": "species blocks"
    },
    {
        "id": "pump",
        "label": "Plankton Pump",
        "description": "Pump sampling; similar taxonomy layering to nets.",
        "file_substring": "pump",
    "notes": "validated + lumped"
    },
    {
        "id": "trap",
        "label": "Sediment Trap",
        "description": "Sediment traps; may include flux-oriented metrics.",
        "file_substring": "trap",
    "notes": "flux units"
    },
    {
        "id": "cpr_south",
        "label": "CPR (Southern Hemisphere)",
        "description": "Southern CPR with species-resolved counts, taxonomy blocks.",
        "file_substring": "cpr_south",
    "notes": "_VT/_LT present"
    },
    {
        "id": "cpr_north",
        "label": "CPR (Northern Hemisphere)",
        "description": "Northern CPR often with binned totals (fewer or no species columns).",
        "file_substring": "cpr_north",
    "notes": "maybe no species"
    },
]

def get_devices() -> List[Dict[str, str]]:
    return list(_DEVICES)

def find_device_for_file(file_key: str) -> str | None:
    lk = file_key.lower()
    for d in _DEVICES:
        if d["file_substring"] in lk:
            return d["id"]
    return None