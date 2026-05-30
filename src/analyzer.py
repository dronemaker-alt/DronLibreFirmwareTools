"""Firmware analysis logic for DronLibreFirmwareTools."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import datetime
import json
import logging

from .file_signatures import detect_file_signature, parse_elf_header
from .parsers import get_parser_metadata, load_parsers
from .firmware_db import (
    init_db,
    upsert_firmware,
    export_to_dronemaker,
    export_inventory_json,
    export_inventory_csv,
)
from .report_generator import generate_markdown_report, generate_html_dashboard
from .utils import (
    estimate_entropy,
    get_file_hash,
    get_file_type,
    read_file_bytes,
    safe_read_strings,
)


class FirmwareAnalyzer:
    def __init__(
        self,
        input_dir: Optional[Path] = None,
        output_dir: Path = Path("reports"),
        allowed_suffixes: tuple[str, ...] | None = None,
    ) -> None:
        self.input_dir = input_dir or Path("samples/input")
        self.output_dir = output_dir
        self.allowed_suffixes = allowed_suffixes
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parsers = load_parsers()
        self.parser_inventory = [get_parser_metadata(parser) for parser in self.parsers]

    def run(self) -> None:
        files = self._iterate_files()
        report = [self.analyze_file(path) for path in files]
        self._mark_duplicates(report)
        self._save_report(report)
        generate_markdown_report(report, self.output_dir)
        generate_html_dashboard(report, self.output_dir, self.parser_inventory)
        self._save_parser_inventory_json()
        self._save_firmware_db_json(report)
        # maintain firmware DB and inventory exports
        db_path = self.output_dir / "firmware.db"
        conn = init_db(db_path)
        for item in report:
            meta = {
                "sha256": item["hashes"].get("sha256"),
                "file_name": item["path"],
                "processor_family": item.get("processor_family"),
                "firmware_type": item.get("firmware_type"),
                "flight_stack": item.get("flight_stack"),
                "version": item.get("version"),
                "confidence": item.get("confidence"),
                "board_type": item.get("board_type"),
                "date_analyzed": item.get("date_analyzed"),
                "notes": item.get("notes"),
                "duplicate_of": ",".join(item.get("duplicate_of", [])) if item.get("duplicate_of") else None,
            }
            upsert_firmware(conn, meta)
        export_to_dronemaker(conn, self.output_dir / "dronemaker.json")
        export_inventory_json(conn, self.output_dir / "inventory.json")
        export_inventory_csv(conn, self.output_dir / "inventory.csv")
        conn.close()
        logging.info("Firmware analysis complete. Reports written to %s", self.output_dir)
        return report

    def _save_firmware_db_json(self, report: List[dict]) -> None:
        db_json_path = self.output_dir / "firmware_db.json"
        with db_json_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)

    def _save_parser_inventory_json(self) -> None:
        out_path = self.output_dir / "parser_inventory.json"
        with out_path.open("w", encoding="utf-8") as handle:
            json.dump(self.parser_inventory, handle, indent=2)

    def _iterate_files(self) -> List[Path]:
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input folder not found: {self.input_dir}")

        files = [path for path in self.input_dir.rglob("*") if path.is_file()]
        if self.allowed_suffixes is None:
            return files

        allowed = {suffix.lower() for suffix in self.allowed_suffixes}
        return [path for path in files if path.suffix.lower() in allowed]

    def analyze_file(self, path: Path) -> dict:
        data = read_file_bytes(path)
        strings = safe_read_strings(data, max_strings=200)

        signature = detect_file_signature(data, strings=strings)
        firmware_type = self._classify_firmware_type(path, data, signature, strings)
        board_type = None
        processor_family = None
        notes_parts = [signature]

        if "ELF" in signature or data.startswith(b"\x7fELF"):
            elf_info = parse_elf_header(data)
            if elf_info:
                file_info_elf = {
                    "elf": elf_info,
                    "processor_family": elf_info.get("machine"),
                    "board_type": elf_info.get("class"),
                }
                processor_family = elf_info.get("machine")
                board_type = elf_info.get("class")
            else:
                file_info_elf = {}
        else:
            file_info_elf = {}

        parser_meta = self._apply_parser_plugins(data, strings, path)
        firmware_type = parser_meta.get("firmware_type") or firmware_type
        board_type = parser_meta.get("board_type") or board_type
        processor_family = parser_meta.get("processor_family") or processor_family
        flight_stack = parser_meta.get("flight_stack")
        version = parser_meta.get("version")
        confidence = parser_meta.get("confidence", 0.0)

        if parser_meta.get("notes"):
            notes_parts.append(parser_meta["notes"])
        if parser_meta.get("detected_parsers"):
            notes_parts.append(f"parsers={','.join(parser_meta['detected_parsers'])}")

        if signature == "Intel HEX":
            processor_family = processor_family or "Unknown"
            board_type = board_type or "Unknown"

        notes = "; ".join(notes_parts)

        file_info = {
            "path": str(path.relative_to(self.input_dir)),
            "size": len(data),
            "hashes": get_file_hash(path),
            "mime_type": get_file_type(path),
            "signature": signature,
            "firmware_type": firmware_type,
            "processor_family": processor_family,
            "flight_stack": flight_stack,
            "version": version,
            "confidence": round(confidence, 3),
            "board_type": board_type,
            "entropy": round(estimate_entropy(data), 4),
            "strings_count": len(strings),
            "strings": strings,
            "date_analyzed": datetime.datetime.utcnow().isoformat() + "Z",
            "notes": notes,
            "detected_parsers": parser_meta.get("detected_parsers", []),
            "parser_details": parser_meta.get("parser_details", []),
        }

        # ELF specific details
        if file_info_elf.get("elf"):
            file_info["elf"] = file_info_elf["elf"]

        # Intel HEX: provide a short text preview if applicable
        if signature == "Intel HEX":
            try:
                text = data.decode("ascii", errors="ignore")
                lines = [l for l in text.splitlines() if l.strip()]
                file_info["intel_hex_lines"] = len(lines)
                file_info["intel_hex_sample"] = lines[:5]
            except Exception:
                pass

        if firmware_type == "BIN" and not board_type:
            notes = file_info["notes"] + "; raw binary"
            file_info["notes"] = notes

        return file_info

    def _apply_parser_plugins(self, data: bytes, strings: List[str], path: Path) -> dict:
        metadata = {
            "firmware_type": None,
            "board_type": None,
            "processor_family": None,
            "flight_stack": None,
            "version": None,
            "confidence": 0.0,
            "notes": None,
            "detected_parsers": [],
            "parser_details": [],
        }
        for parser in self.parsers:
            try:
                result = parser.parse(data, strings, path)
            except Exception:
                continue

            if not result.get("detected"):
                continue

            normalized = {
                "firmware_type": result.get("firmware_type"),
                "board_type": result.get("board_type"),
                "processor_family": result.get("processor_family"),
                "flight_stack": result.get("flight_stack"),
                "version": result.get("version"),
                "confidence": float(result.get("confidence", 0.0) or 0.0),
                "notes": result.get("notes"),
                "name": getattr(parser, "NAME", parser.__name__),
            }

            if normalized["firmware_type"] and not metadata["firmware_type"]:
                metadata["firmware_type"] = normalized["firmware_type"]
            if normalized["board_type"] and not metadata["board_type"]:
                metadata["board_type"] = normalized["board_type"]
            if normalized["processor_family"] and not metadata["processor_family"]:
                metadata["processor_family"] = normalized["processor_family"]
            if normalized["flight_stack"] and not metadata["flight_stack"]:
                metadata["flight_stack"] = normalized["flight_stack"]
            if normalized["version"] and not metadata["version"]:
                metadata["version"] = normalized["version"]
            if normalized["confidence"] > metadata["confidence"]:
                metadata["confidence"] = normalized["confidence"]
            if normalized["notes"]:
                metadata["notes"] = "; ".join(filter(None, [metadata.get("notes"), normalized["notes"]]))

            metadata["detected_parsers"].append(normalized["name"])
            metadata["parser_details"].append(normalized)

        return metadata

    def _classify_firmware_type(self, path: Path, data: bytes, signature: str, strings: List[str]) -> str:
        lower_name = path.suffix.lower()
        if signature == "Intel HEX":
            return "Intel HEX"
        if "DJI" in signature:
            return "DJI"
        if "Betaflight" in signature:
            return "Betaflight"
        if "ELF" in signature or data.startswith(b"\x7fELF"):
            return "ELF"
        if lower_name == ".hex":
            return "Intel HEX"
        if lower_name == ".elf":
            return "ELF"
        if lower_name == ".bin":
            return "BIN"
        return "binary"

    def _mark_duplicates(self, report: List[dict]) -> None:
        duplicates = {}
        for item in report:
            sha = item["hashes"].get("sha256")
            if sha:
                duplicates.setdefault(sha, []).append(item["path"])

        for item in report:
            sha = item["hashes"].get("sha256")
            if sha and len(duplicates.get(sha, [])) > 1:
                other_files = [path for path in duplicates[sha] if path != item["path"]]
                item["duplicate_of"] = other_files
                item["duplicate_count"] = len(duplicates[sha])
                item["notes"] = f"{item.get('notes', '')}; duplicate of {', '.join(other_files)}"

    def _save_report(self, report: List[dict]) -> None:
        report_path = self.output_dir / "analysis_report.json"
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
