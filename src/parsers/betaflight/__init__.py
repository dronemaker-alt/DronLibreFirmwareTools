"""Betaflight firmware parser plugin."""

from pathlib import Path
from typing import List, Dict, Any
import re

NAME = "betaflight"
VERSION = "0.1.0"
SUPPORTED_FILE_TYPES = [".bin", ".hex", ".elf"]
STATUS = "active"
DESCRIPTION = "Betaflight firmware detector for STM32 and flight controller images."


def parse(data: bytes, strings: List[str], path: Path) -> Dict[str, Any]:
    joined = " ".join(strings)
    detected = "betaflight" in joined.lower() or b"betaflight" in data.lower()
    if not detected:
        return {"detected": False}

    board_type = None
    version = None
    confidence = 0.8
    m = re.search(r"(stm32[fF][0-9]+|stm32)", joined, re.IGNORECASE)
    if m:
        board_type = m.group(1)
        confidence = 0.9

    vm = re.search(r"v?([0-9]+\.[0-9]+(?:\.[0-9]+)*)", joined, re.IGNORECASE)
    if vm:
        version = vm.group(1)

    return {
        "name": NAME,
        "detected": True,
        "firmware_type": "Betaflight",
        "flight_stack": "Betaflight",
        "board_type": board_type,
        "processor_family": "ARM",
        "version": version,
        "confidence": confidence,
        "notes": "Betaflight firmware detected",
    }
