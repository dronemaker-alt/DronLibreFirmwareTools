from pathlib import Path
import sqlite3

from src.parsers import get_parser_metadata, load_parsers
from src.parsers.stm32 import detect_stm32_vector, detect_stm32_family
from src.firmware_db import init_db, upsert_firmware, export_to_dronemaker, export_inventory_json, export_inventory_csv


def test_detect_stm32_vector_valid() -> None:
    # construct vector table with SP in SRAM and reset in flash
    sp = (0x20001000).to_bytes(4, "little")
    reset = (0x08000100).to_bytes(4, "little")
    data = sp + reset + b"rest"
    info = detect_stm32_vector(data)
    assert info is not None
    assert info["sp_valid"] == "True"
    assert info["reset_valid"] == "True"


def test_detect_stm32_family_from_strings() -> None:
    data = b"\x00" * 64
    strings = ["STM32F4", "STM32 MCU"]
    family = detect_stm32_family(data, strings)
    assert family == "STM32F4"


def test_detect_stm32_family_from_vector() -> None:
    sp = (0x20001000).to_bytes(4, "little")
    reset = (0x08090000).to_bytes(4, "little")
    data = sp + reset + b"rest"
    family = detect_stm32_family(data, [])
    assert family == "STM32F7"


def test_firmware_db_export(tmp_path: Path) -> None:
    db_path = tmp_path / "reports" / "firmware.db"
    conn = init_db(db_path)
    upsert_firmware(conn, {
        "sha256": "deadbeef",
        "file_name": "test.bin",
        "board_type": "TestBoard",
        "processor_family": "ARM",
        "firmware_type": "TestFirmware",
        "flight_stack": "TestStack",
        "version": "1.0.0",
        "confidence": 0.77,
        "date_analyzed": "2026-05-30T00:00:00Z",
        "notes": "Unit test",
    })
    out = tmp_path / "reports" / "dronemaker.json"
    export_to_dronemaker(conn, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "deadbeef" in content

    json_out = tmp_path / "reports" / "inventory.json"
    export_inventory_json(conn, json_out)
    assert json_out.exists()
    json_content = json_out.read_text(encoding="utf-8")
    assert "inventory" in json_content

    csv_out = tmp_path / "reports" / "inventory.csv"
    export_inventory_csv(conn, csv_out)
    assert csv_out.exists()
    csv_content = csv_out.read_text(encoding="utf-8")
    assert "deadbeef" in csv_content
    assert "TestStack" in csv_content
    conn.close()


def test_parser_discovery_loads_all_plugins() -> None:
    parsers = load_parsers()
    assert len(parsers) >= 1
    for parser in parsers:
        assert hasattr(parser, "parse")
        assert getattr(parser, "NAME", None) is not None


def test_parser_metadata_populated() -> None:
    parsers = load_parsers()
    metadata = [get_parser_metadata(parser) for parser in parsers]
    assert all(parser_meta["version"] for parser_meta in metadata)
    assert all(isinstance(parser_meta["supported_file_types"], list) for parser_meta in metadata)
    assert all(parser_meta["status"] for parser_meta in metadata)


def test_dji_parser_interface() -> None:
    parsers = load_parsers()
    dji_parser = next((p for p in parsers if getattr(p, "NAME", "") == "dji"), None)
    assert dji_parser is not None

    data = b"DJI firmware binary with FW_v1.2.3"
    strings = ["DJI", "FW_v1.2.3"]
    result = dji_parser.parse(data, strings, Path("dummy.bin"))

    assert result["detected"] is True
    assert result["firmware_type"] == "DJI"
    assert result["flight_stack"] == "DJI"
    assert result["confidence"] > 0.0
    assert result["version"] == "1.2.3"
    assert "notes" in result
