"""Lightweight DJI firmware heuristics parser."""
from typing import List, Dict
import re


def parse_dji(data: bytes, strings: List[str]) -> Dict[str, str]:
    """Return basic DJI package info if detected (heuristic)."""
    joined = " ".join(strings).lower()
    info = {"vendor": "DJI", "detected": False}

    if "dji" in joined or b"osdk" in data.lower():
        info["detected"] = True
        # attempt to extract a version-like token
        m = re.search(r"fw[ _-]?v?([0-9]+(?:\.[0-9A-Za-z_\-]+)*)", joined)
        if m:
            info["version"] = m.group(1)
        else:
            # try generic version token
            m2 = re.search(r"version[:= ]+([0-9A-Za-z._-]+)", joined)
            if m2:
                info["version"] = m2.group(1)
    return info
