"""File signature detection and lightweight parsing helpers.

Provides detection for common binary signatures and simple heuristics for
Intel HEX, DJI packages, and Betaflight targets. Also includes a minimal
ELF header parser to extract class and machine architecture without external
dependencies.
"""

from typing import List, Tuple, Optional, Dict
import re
import struct


FILE_SIGNATURES: List[Tuple[str, int, bytes]] = [
    ("ZIP archive", 0, b"PK\x03\x04"),
    ("ZIP archive (empty)", 0, b"PK\x05\x06"),
    ("ZIP archive (spanned)", 0, b"PK\x07\x08"),
    ("GZIP archive", 0, b"\x1f\x8b\x08"),
    ("PNG image", 0, b"\x89PNG\r\n\x1a\n"),
    ("JPEG image", 0, b"\xff\xd8\xff"),
    ("TIFF image (little-endian)", 0, b"II*\x00"),
    ("TIFF image (big-endian)", 0, b"MM\x00*"),
    ("BMP image", 0, b"BM"),
    ("ELF executable", 0, b"\x7fELF"),
    ("Windows PE executable", 0, b"MZ"),
    ("PDF document", 0, b"%PDF-"),
    ("RAR archive", 0, b"Rar!\x1a\x07\x00"),
    ("7z archive", 0, b"7z\xbc\xaf'\x1c"),
    ("XZ stream", 0, b"\xfd7zXZ\x00"),
    ("LZMA stream", 0, b"\x5d\x00\x00\x80\x00"),
    ("BZIP2 archive", 0, b"BZh"),
    ("Tar archive", 257, b"ustar\x0000"),
]


INTEL_HEX_LINE = re.compile(rb"^:[0-9A-Fa-f]+$")


def detect_file_signature(data: bytes, strings: Optional[List[str]] = None) -> str:
    """Return a human-readable file signature for the given binary data.

    The function performs fixed-signature matching and a few text-based
    heuristics (Intel HEX, DJI, Betaflight). The `strings` parameter can be
    provided to aid heuristic detection (pre-extracted printable strings).
    """
    # fixed signatures
    matches: List[str] = []
    for label, offset, signature in FILE_SIGNATURES:
        if len(data) >= offset + len(signature) and data[offset : offset + len(signature)] == signature:
            matches.append(label)

    if matches:
        return ", ".join(matches)

    # Intel HEX detection (text-based)
    try:
        text = data.decode("ascii", errors="ignore").strip()
        lines = text.splitlines()
        if lines and all(INTEL_HEX_LINE.match(line.encode("ascii", errors="ignore")) for line in lines if line.strip()):
            return "Intel HEX"
    except Exception:
        pass

    # Heuristic: DJI package detection via strings
    if strings:
        joined = " ".join(s.lower() for s in strings)
        if "dji" in joined or "osdk" in joined or "dji_fw" in joined:
            return "DJI firmware (heuristic)"
        if "betaflight" in joined:
            return "Betaflight target (heuristic)"

    # fallback: raw binary
    return "raw binary (.bin)"


def parse_elf_header(data: bytes) -> Optional[Dict[str, str]]:
    """Parse minimal ELF header information: class (32/64) and machine.

    Returns a dict with `class` and `machine` keys or None if not ELF.
    """
    if len(data) < 16 or data[0:4] != b"\x7fELF":
        return None

    ei_class = data[4]
    ei_data = data[5]

    endian = "<" if ei_data == 1 else ">"
    elf_class = "ELF32" if ei_class == 1 else "ELF64" if ei_class == 2 else f"unknown({ei_class})"

    # e_machine is at offset 18 (2 bytes) in the ELF header
    if len(data) >= 20:
        e_machine = struct.unpack(endian + "H", data[18:20])[0]
    else:
        e_machine = 0

    machine_map = {
        0x03: "x86",
        0x28: "ARM",
        0x3E: "x86-64",
        0x08: "MIPS",
        0xB7: "AArch64",
        0xF3: "RISC-V",
    }
    machine = machine_map.get(e_machine, f"unknown(0x{e_machine:04x})")

    return {"class": elf_class, "machine": machine}

