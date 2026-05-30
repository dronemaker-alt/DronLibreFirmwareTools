"""STM32 firmware parser plugin."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import struct

NAME = "stm32"
VERSION = "0.1.0"
SUPPORTED_FILE_TYPES = [".bin", ".hex", ".elf"]
STATUS = "active"
DESCRIPTION = "STM32 binary detector with family heuristics."

_FAMILY_PATTERNS = [
    (re.compile(r"stm32f1", re.IGNORECASE), "STM32F1"),
    (re.compile(r"stm32f3", re.IGNORECASE), "STM32F3"),
    (re.compile(r"stm32f4", re.IGNORECASE), "STM32F4"),
    (re.compile(r"stm32f7", re.IGNORECASE), "STM32F7"),
    (re.compile(r"stm32h7", re.IGNORECASE), "STM32H7"),
]


def detect_stm32_vector(data: bytes) -> Optional[Dict[str, str]]:
    if len(data) < 8:
        return None

    try:
        sp, reset = struct.unpack_from("<II", data, 0)
    except struct.error:
        return None

    is_sp_valid = 0x20000000 <= sp <= 0x2005FFFF
    is_reset_valid = 0x08000000 <= (reset & 0xFFFFFFFF) <= 0x082FFFFF
    if is_sp_valid or is_reset_valid:
        return {
            "initial_sp": hex(sp),
            "reset_address": hex(reset),
            "sp_valid": str(is_sp_valid),
            "reset_valid": str(is_reset_valid),
        }
    return None


def detect_stm32_family(data: bytes, strings: List[str]) -> Optional[str]:
    joined = " ".join(strings)
    for pattern, family in _FAMILY_PATTERNS:
        if pattern.search(joined):
            return family

    try:
        text = data.decode("ascii", errors="ignore")
    except Exception:
        text = ""

    for pattern, family in _FAMILY_PATTERNS:
        if pattern.search(text):
            return family

    vector = detect_stm32_vector(data)
    if not vector:
        return None

    reset_addr = int(vector["reset_address"], 16)
    size = len(data)

    if 0x08000000 <= reset_addr <= 0x0807FFFF:
        if size <= 0x40000:
            return "STM32F1"
        if size <= 0x80000:
            return "STM32F3"
        return "STM32F4"
    if 0x08080000 <= reset_addr <= 0x080FFFFF:
        return "STM32F7"
    if 0x08100000 <= reset_addr <= 0x082FFFFF:
        return "STM32H7"
    return None


def parse(data: bytes, strings: List[str], path: Path) -> Dict[str, Any]:
    family = detect_stm32_family(data, strings)
    vector = detect_stm32_vector(data)
    if not family and not vector:
        return {"detected": False}

    notes = "STM32 firmware detected"
    if family:
        notes += f"; family={family}"

    return {
        "name": NAME,
        "detected": True,
        "firmware_type": family or "STM32",
        "flight_stack": "STM32",
        "board_type": "STM32",
        "processor_family": family or "ARM Cortex-M",
        "version": None,
        "confidence": 0.9 if family else 0.7,
        "notes": notes,
    }
