"""STM32 vector table detection utilities."""

from typing import Dict, Optional, List
import re
import struct

_FAMILY_PATTERNS = [
    (re.compile(r"stm32f1", re.IGNORECASE), "STM32F1"),
    (re.compile(r"stm32f3", re.IGNORECASE), "STM32F3"),
    (re.compile(r"stm32f4", re.IGNORECASE), "STM32F4"),
    (re.compile(r"stm32f7", re.IGNORECASE), "STM32F7"),
    (re.compile(r"stm32h7", re.IGNORECASE), "STM32H7"),
]


def detect_stm32_vector(data: bytes) -> Optional[Dict[str, str]]:
    """Detect a plausible STM32 vector table at the start of `data`.

    Returns a dict with initial SP and reset address if plausible, otherwise None.
    """
    if len(data) < 8:
        return None

    # Little-endian by ARM convention; read first two words
    try:
        sp, reset = struct.unpack_from("<II", data, 0)
    except struct.error:
        return None

    # Basic heuristics: initial SP in SRAM region and reset vector in Flash
    is_sp_valid = 0x20000000 <= sp <= 0x2005FFFF
    is_reset_valid = 0x08000000 <= (reset & 0xFFFFFFFF) <= 0x080FFFFF

    if is_sp_valid or is_reset_valid:
        return {
            "initial_sp": hex(sp),
            "reset_address": hex(reset),
            "sp_valid": str(is_sp_valid),
            "reset_valid": str(is_reset_valid),
        }
    return None


def detect_stm32_family(data: bytes, strings: Optional[List[str]] = None) -> Optional[str]:
    """Attempt to identify the STM32 family from firmware data or printable strings."""
    if strings:
        joined = " ".join(strings)
        for pattern, family in _FAMILY_PATTERNS:
            if pattern.search(joined):
                return family

    # Look for family-specific signatures in binary image
    for pattern, family in _FAMILY_PATTERNS:
        try:
            if pattern.search(data.decode("ascii", errors="ignore")):
                return family
        except Exception:
            continue

    # Use reset vector address heuristics to infer some common families
    vector = detect_stm32_vector(data)
    if not vector:
        return None

    reset_addr = int(vector["reset_address"], 16)
    size = len(data)

    # Heuristic family selection based on flash address ranges and image size.
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
