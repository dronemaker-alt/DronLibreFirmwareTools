"""INAV firmware parser plugin."""

from pathlib import Path
from typing import List, Dict, Any

NAME = "inav"
VERSION = "0.1.0"
SUPPORTED_FILE_TYPES = [".bin", ".hex", ".elf"]
STATUS = "active"
DESCRIPTION = "INAV firmware detector for navigation and flight controllers."


def parse(data: bytes, strings: List[str], path: Path) -> Dict[str, Any]:
    joined = " ".join(strings).lower()
    detected = "inav" in joined or b"inav" in data.lower()
    if not detected:
        return {"detected": False}

    version = None
    m = re.search(r"v?([0-9]+\.[0-9]+(?:\.[0-9]+)*)", joined, re.IGNORECASE)
    if m:
        version = m.group(1)

    return {
        "name": NAME,
        "detected": True,
        "firmware_type": "INAV",
        "flight_stack": "INAV",
        "board_type": "INAV",
        "processor_family": "ARM",
        "version": version,
        "confidence": 0.85,
        "notes": "INAV firmware detected",
    }
