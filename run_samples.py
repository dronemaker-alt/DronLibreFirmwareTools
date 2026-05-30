"""Run a sample firmware scan and generate reports for all supported parser targets."""

from pathlib import Path

from src.analyzer import FirmwareAnalyzer
from src.utils import configure_logging


def main() -> int:
    configure_logging()
    analyzer = FirmwareAnalyzer(
        input_dir=Path("samples"),
        output_dir=Path("reports"),
        allowed_suffixes=(".bin", ".hex", ".elf"),
    )
    analyzer.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
