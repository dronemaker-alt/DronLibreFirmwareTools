import json
from pathlib import Path

from src.analyzer import FirmwareAnalyzer


def test_analyzer_on_various_formats(tmp_path: Path) -> None:
    sample_dir = tmp_path / "samples" / "input"
    sample_dir.mkdir(parents=True)

    # Intel HEX file
    intel = sample_dir / "firmware.hex"
    intel.write_bytes(b":10010000214601360121470136007EFE09D2190140\n:00000001FF\n")

    # ELF-like file
    elf_file = sample_dir / "boot.elf"
    elf_data = b"\x7fELF" + bytes([2, 1, 1]) + b"\x00" * 9
    elf_data = elf_data.ljust(18, b"\x00") + b"\x3E\x00" + b"payload"
    elf_file.write_bytes(elf_data)

    # DJI heuristic file (strings)
    dji_file = sample_dir / "dji_blob.bin"
    dji_file.write_bytes(b"\x00DJI_FIRMWARE\x00")

    output_dir = tmp_path / "reports"
    analyzer = FirmwareAnalyzer(input_dir=sample_dir, output_dir=output_dir)
    analyzer.run()

    # Check reports
    assert (output_dir / "analysis_report.json").exists()
    assert (output_dir / "index.md").exists()
    # per-file markdowns
    assert (output_dir / "firmware.hex.md").exists()
    assert (output_dir / "boot.elf.md").exists()
    assert (output_dir / "dji_blob.bin.md").exists()

    inventory_json = output_dir / "inventory.json"
    inventory_csv = output_dir / "inventory.csv"
    assert inventory_json.exists()
    assert inventory_csv.exists()

    # no duplicates expected in this test set
    data = (output_dir / "analysis_report.json").read_text(encoding="utf-8")
    assert "duplicate_count" not in data


def test_duplicate_detection(tmp_path: Path) -> None:
    sample_dir = tmp_path / "samples" / "input"
    sample_dir.mkdir(parents=True)

    payload = b"PK\x03\x04dummy"
    file1 = sample_dir / "dup1.bin"
    file2 = sample_dir / "dup2.bin"
    file1.write_bytes(payload)
    file2.write_bytes(payload)

    output_dir = tmp_path / "reports"
    analyzer = FirmwareAnalyzer(input_dir=sample_dir, output_dir=output_dir)
    analyzer.run()

    report = json.loads((output_dir / "analysis_report.json").read_text(encoding="utf-8"))
    duplicates = [item for item in report if item.get("duplicate_count") == 2]
    assert len(duplicates) == 2
    assert all(item.get("duplicate_of") for item in duplicates)

    inventory = json.loads((output_dir / "inventory.json").read_text(encoding="utf-8"))
    assert any(entry["sha256"] == duplicates[0]["hashes"]["sha256"] for entry in inventory["inventory"])
