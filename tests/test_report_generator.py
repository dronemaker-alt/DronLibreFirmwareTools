from pathlib import Path

from src.report_generator import generate_markdown_report


def test_generate_markdown_report(tmp_path: Path) -> None:
    report = [
        {
            "path": "firmware.bin",
            "size": 64,
            "hashes": {"sha256": "deadbeef"},
            "mime_type": "application/octet-stream",
            "signature": "ZIP archive",
            "entropy": 4.321,
            "strings_count": 1,
            "strings": ["FirmwareSample"],
        }
    ]

    generate_markdown_report(report, tmp_path)

    index_path = tmp_path / "index.md"
    file_path = tmp_path / "firmware.bin.md"

    assert index_path.exists()
    assert file_path.exists()
    index_text = index_path.read_text(encoding="utf-8")
    file_text = file_path.read_text(encoding="utf-8")

    assert "Firmware Analysis Report" in index_text
    assert "firmware.bin" in file_text
    assert "ZIP archive" in file_text
