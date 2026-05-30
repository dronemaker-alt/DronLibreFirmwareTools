"""Command-line entry point for DronLibreFirmwareTools."""

from collections import Counter
from pathlib import Path
import argparse
from typing import List, Dict, Any

from .analyzer import FirmwareAnalyzer
from .utils import configure_logging


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DronLibreFirmwareTools command-line interface."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser(
        "analyze-all",
        help="Scan input/ recursively, auto-detect firmware, run parsers, and generate reports.",
    )
    analyze.add_argument(
        "--input",
        type=Path,
        default=Path("input"),
        help="Root input folder to scan recursively (default: input)",
    )
    analyze.add_argument(
        "--output",
        type=Path,
        default=Path("reports"),
        help="Output directory for generated reports (default: reports)",
    )
    return parser


def _print_summary(report: List[Dict[str, Any]]) -> None:
    total = len(report)
    duplicates = sum(1 for entry in report if entry.get("duplicate_count", 0) > 0)
    firmware_counts = Counter(entry.get("firmware_type") or "Unknown" for entry in report)
    processor_counts = Counter(entry.get("processor_family") or "Unknown" for entry in report)
    board_counts = Counter(entry.get("board_type") or "Unknown" for entry in report)
    average_confidence = (
        round(sum(entry.get("confidence", 0.0) for entry in report) / total, 3)
        if total
        else 0.0
    )

    print("\nFirmware Import Wizard Summary")
    print("--------------------------------")
    print(f"Total firmware analyzed: {total}")
    print(f"Duplicate files detected: {duplicates}")
    print(f"Average confidence score: {average_confidence:.3f}\n")

    print("Firmware types:")
    for firmware_type, count in firmware_counts.most_common():
        print(f"  - {firmware_type}: {count}")

    print("\nProcessor families:")
    for processor_family, count in processor_counts.most_common():
        print(f"  - {processor_family}: {count}")

    print("\nBoard types:")
    for board_type, count in board_counts.most_common():
        print(f"  - {board_type}: {count}")
    print()


def main() -> int:
    configure_logging()
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "analyze-all":
        analyzer = FirmwareAnalyzer(
            input_dir=args.input,
            output_dir=args.output,
            allowed_suffixes=(".bin", ".hex", ".elf"),
        )
        report = analyzer.run()
        _print_summary(report)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
