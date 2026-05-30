from pathlib import Path

from src.analyzer import FirmwareAnalyzer


def test_analyze_empty_directory(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"

    analyzer = FirmwareAnalyzer(input_dir=input_dir, output_dir=output_dir)
    analyzer.run()

    assert (output_dir / "analysis_report.json").exists()
    assert (output_dir / "index.md").exists()


def test_analyzer_generates_markdown_reports(tmp_path: Path) -> None:
    sample_dir = tmp_path / "samples" / "input"
    sample_dir.mkdir(parents=True)
    test_file = sample_dir / "firmware.bin"
    test_file.write_bytes(b"PK\x03\x04\x00\x00\x00hello firmware sample")

    output_dir = tmp_path / "reports"
    analyzer = FirmwareAnalyzer(input_dir=sample_dir, output_dir=output_dir)
    analyzer.run()

    assert (output_dir / "analysis_report.json").exists()
    assert (output_dir / "index.md").exists()
    assert (output_dir / "firmware.bin.md").exists()
    index_text = (output_dir / "index.md").read_text(encoding="utf-8")
    assert "firmware.bin" in index_text
