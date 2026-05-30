"""DJI firmware parser plugin."""

import re
from pathlib import Path
from typing import List, Dict, Any

NAME = "dji"
VERSION = "0.1.0"
SUPPORTED_FILE_TYPES = [".bin", ".hex", ".elf"]
STATUS = "active"
DESCRIPTION = "DJI firmware detector for packages and flight images."


def parse(data: bytes, strings: List[str], path: Path) -> Dict[str, Any]:
    joined = " ".join(strings).lower()
    detected = "dji" in joined or "osdk" in joined or b"dji" in data.lower()
    if not detected:
        return {"detected": False}

    version = None
    m = re.search(r"fw[ _-]?v?([0-9]+(?:\.[0-9A-Za-z_\-]+)*)", joined)
    if m:
        version = m.group(1)

    info: Dict[str, Any] = {
        "name": NAME,
        "detected": True,
        "firmware_type": "DJI",
        "flight_stack": "DJI",
        "board_type": "DJI",
        "processor_family": None,
        "version": version,
        "confidence": 0.85,
        "notes": "DJI firmware detected",
    }

    if version:
        info["notes"] += f"; version={version}"

    return info
