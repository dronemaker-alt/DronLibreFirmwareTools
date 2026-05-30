"""Lightweight Betaflight target detection parser."""
from typing import List, Dict
import re


def parse_betaflight(data: bytes, strings: List[str]) -> Dict[str, str]:
    """Return Betaflight detection info if present (heuristic)."""
    joined = " ".join(strings)
    info = {"detected": False}

    if "betaflight" in joined.lower():
        info["detected"] = True
        # attempt to extract a target or MCU family token
        m = re.search(r"(stm32[fF][0-9]+|stm32)", joined, re.IGNORECASE)
        if m:
            info["board_type"] = m.group(1)
    return info
