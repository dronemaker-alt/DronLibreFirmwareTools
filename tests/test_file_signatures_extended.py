from src.file_signatures import detect_file_signature, parse_elf_header


def test_detect_intel_hex() -> None:
    intel = b":10010000214601360121470136007EFE09D2190140\n:00000001FF\n"
    assert detect_file_signature(intel) == "Intel HEX"


def test_detect_dji_heuristic() -> None:
    data = b"\x00\x01DJI\x00\x02"
    # strings passed to helper
    strings = ["DJI", "firmware"]
    assert "DJI" in detect_file_signature(data, strings=strings)


def test_detect_betaflight_heuristic() -> None:
    data = b"random"
    strings = ["Betaflight v4.4.0"]
    assert "Betaflight" in detect_file_signature(data, strings=strings)


def test_parse_elf_header_minimal() -> None:
    # craft minimal ELF header for little-endian 64-bit x86-64
    elf = b"\x7fELF" + bytes([2, 1, 1]) + b"\x00" * 9  # e_ident (16 bytes)
    # pad to 20 bytes so we can set e_machine at offset 18-19
    elf = elf.ljust(18, b"\x00") + b"\x3E\x00" + b"rest"
    parsed = parse_elf_header(elf)
    assert parsed is not None
    assert parsed.get("class") == "ELF64"
    assert "x86-64" in parsed.get("machine")
