"""ESP32 firmware parser plugin."""

from pathlib import Path
from typing import List, Dict, Any

NAME = "esp32"
VERSION = "0.1.0"
SUPPORTED_FILE_TYPES = [".bin", ".elf"]
STATUS = "active"
DESCRIPTION = "ESP32 firmware detector for Xtensa and ESP-IDF images."


def parse(data: bytes, strings: List[str], path: Path) -> Dict[str, Any]:
    joined = " ".join(strings).lower()
    detected = "esp32" in joined or b"esp32" in data.lower()
    if not detected:
        return {"detected": False}

    version = None
    m = re.search(r"esp-idf[\s_-]*v?([0-9]+\.[0-9]+(?:\.[0-9]+)*)", joined)
    if m:
        version = m.group(1)

    return {
        "name": NAME,
        "detected": True,
        "firmware_type": "ESP32",
        "flight_stack": "ESP32",
        "board_type": "ESP32",
        "processor_family": "Xtensa",
        "version": version,
        "confidence": 0.75,
        "notes": "ESP32 firmware detected",
    }
