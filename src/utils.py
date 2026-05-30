"""Utility helpers for DronLibreFirmwareTools."""

from pathlib import Path
import hashlib
import math
import re

try:
    import magic
except ImportError:  # pragma: no cover
    magic = None


def configure_logging() -> None:
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def get_file_type(path: Path) -> str:
    if magic is None:
        return "unknown"

    try:
        return magic.from_file(str(path), mime=True)
    except Exception:
        return "unknown"


def get_file_hash(path: Path) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return {"sha256": digest.hexdigest()}


def read_file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def estimate_entropy(data: bytes) -> float:
    if not data:
        return 0.0

    counts: dict[int, int] = {}
    for byte in data:
        counts[byte] = counts.get(byte, 0) + 1

    entropy = 0.0
    length = len(data)
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy


def safe_read_strings(data: bytes, max_strings: int = 100) -> list[str]:
    pattern = re.compile(rb"[ -~]{4,}")
    strings: list[str] = []
    for match in pattern.finditer(data):
        strings.append(match.group(0).decode("ascii", errors="ignore"))
        if len(strings) >= max_strings:
            break
    return strings
