"""ArduPilot firmware parser plugin."""

from pathlib import Path
from typing import List, Dict, Any

NAME = "ardupilot"
VERSION = "0.1.0"
SUPPORTED_FILE_TYPES = [".bin", ".hex", ".elf"]
STATUS = "active"
DESCRIPTION = "ArduPilot firmware detector for ARM-based autopilot images."


def parse(data: bytes, strings: List[str], path: Path) -> Dict[str, Any]:
    joined = " ".join(strings).lower()
    detected = "ardupilot" in joined or b"ardupilot" in data.lower() or b"apm" in data.lower()
    if not detected:
        return {"detected": False}

    return {
        "name": NAME,
        "detected": True,
        "firmware_type": "ArduPilot",
        "flight_stack": "ArduPilot",
        "processor_family": "ARM",
        "version": None,
        "confidence": 0.95,
        "board_type": "ArduPilot",
        "notes": "ArduPilot firmware detected",
    }
