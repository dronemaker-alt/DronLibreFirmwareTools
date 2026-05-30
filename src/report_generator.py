"""Markdown report generation for DronLibreFirmwareTools."""

from pathlib import Path
import re
from typing import Any, Dict, List


def generate_markdown_report(report: List[Dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.md"

    with index_path.open("w", encoding="utf-8") as handle:
        handle.write("# Firmware Analysis Report\n\n")
        handle.write("This report summarizes discovered firmware files and analysis metadata.\n\n")
        handle.write("## Files\n\n")
        for item in report:
            file_name = item["path"]
            report_file_name = _safe_filename(file_name) + ".md"
            handle.write(f"- [{file_name}]({report_file_name})\n")

    for item in report:
        file_report_path = output_dir / (_safe_filename(item["path"]) + ".md")
        _write_file_report(item, file_report_path)


def generate_html_dashboard(report: List[Dict[str, Any]], output_dir: Path, parser_inventory: List[Dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    dashboard_path = output_dir / "index.html"

    total = len(report)
    firmware_counts = _count_values(report, "firmware_type")
    processor_counts = _count_values(report, "processor_family")
    board_counts = _count_values(report, "board_type")
    duplicates = [item for item in report if item.get("duplicate_count", 0) > 0]
    duplicate_files = len(duplicates)
    duplicate_groups = len({item["hashes"].get("sha256") for item in duplicates if item["hashes"].get("sha256")})
    average_confidence = round(sum(item.get("confidence", 0.0) for item in report) / total, 3) if total else 0.0

    rows_html = "\n".join(_html_row(item) for item in report)
    parser_rows_html = "\n".join(_html_parser_row(parser) for parser in parser_inventory)

    with dashboard_path.open("w", encoding="utf-8") as handle:
        handle.write("<!DOCTYPE html>\n")
        handle.write("<html lang=\"en\">\n")
        handle.write("<head>\n")
        handle.write("  <meta charset=\"utf-8\">\n")
        handle.write("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n")
        handle.write("  <title>Firmware Analysis Dashboard</title>\n")
        handle.write("  <style>body{font-family:Arial,sans-serif;margin:24px;background:#f8f9fb;color:#1d2129;}h1,h2{color:#0f172a;}table{border-collapse:collapse;width:100%;margin-bottom:24px;}th,td{border:1px solid #d1d5db;padding:8px;text-align:left;}th{background:#e2e8f0;}tr:nth-child(even){background:#f8fafc;}code{background:#eef2ff;padding:2px 4px;border-radius:4px;}</style>\n")
        handle.write("</head>\n")
        handle.write("<body>\n")
        handle.write("<h1>Firmware Analysis Dashboard</h1>\n")
        handle.write(f"<p>Total firmware analyzed: <strong>{total}</strong></p>\n")
        handle.write(f"<p>Average confidence score: <strong>{average_confidence}</strong></p>\n")
        handle.write(f"<p>Duplicate files: <strong>{duplicate_files}</strong> in <strong>{duplicate_groups}</strong> groups</p>\n")

        handle.write("<h2>Counts by Firmware Type</h2>\n")
        handle.write(_html_summary_table(firmware_counts))

        handle.write("<h2>Counts by Processor Family</h2>\n")
        handle.write(_html_summary_table(processor_counts))

        handle.write("<h2>Counts by Board Type</h2>\n")
        handle.write(_html_summary_table(board_counts))

        handle.write("<h2>Firmware Inventory</h2>\n")
        handle.write("<table>\n")
        handle.write("<thead><tr><th>Path</th><th>Firmware Type</th><th>Processor</th><th>Board</th><th>Confidence</th><th>Duplicate</th></tr></thead>\n")
        handle.write("<tbody>\n")
        handle.write(rows_html)
        handle.write("</tbody>\n")
        handle.write("</table>\n")

        handle.write("<h2>Parser Manager</h2>\n")
        handle.write("<p>The parser manager dashboard displays all detected parser plugins, versions, supported file types, and current status.</p>\n")
        handle.write("<table>\n")
        handle.write("<thead><tr><th>Name</th><th>Version</th><th>Supported File Types</th><th>Status</th><th>Description</th></tr></thead>\n")
        handle.write("<tbody>\n")
        handle.write(parser_rows_html)
        handle.write("</tbody>\n")
        handle.write("</table>\n")
        handle.write("</body>\n")
        handle.write("</html>\n")


def _html_summary_table(counts: Dict[str, int]) -> str:
    if not counts:
        return "<p><em>None detected.</em></p>\n"
    rows = "".join(f"<tr><td>{key}</td><td>{value}</td></tr>\n" for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    return f"<table>\n<thead><tr><th>Value</th><th>Count</th></tr></thead>\n<tbody>\n{rows}</tbody>\n</table>\n"


def _html_row(item: Dict[str, Any]) -> str:
    duplicate = ", ".join(item.get("duplicate_of", [])) if item.get("duplicate_of") else ""
    return (
        "<tr>"
        f"<td><code>{item['path']}</code></td>"
        f"<td>{item.get('firmware_type', 'unknown')}</td>"
        f"<td>{item.get('processor_family', 'unknown')}</td>"
        f"<td>{item.get('board_type', 'unknown')}</td>"
        f"<td>{item.get('confidence', 0.0):.3f}</td>"
        f"<td>{duplicate}</td>"
        "</tr>\n"
    )


def _count_values(report: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in report:
        value = item.get(key) or "Unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _html_parser_row(parser: Dict[str, Any]) -> str:
    supported = ", ".join(parser.get("supported_file_types", []))
    return (
        "<tr>"
        f"<td>{parser.get('name', 'unknown')}</td>"
        f"<td>{parser.get('version', 'unknown')}</td>"
        f"<td>{supported}</td>"
        f"<td>{parser.get('status', 'unknown')}</td>"
        f"<td>{parser.get('description', '')}</td>"
        "</tr>\n"
    )


def _write_file_report(file_info: Dict[str, Any], report_path: Path) -> None:
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# File Report: {file_info['path']}\n\n")
        handle.write("## Summary\n\n")
        handle.write(f"- **Size:** {file_info['size']} bytes\n")
        handle.write(f"- **SHA256:** {file_info['hashes'].get('sha256', 'unknown')}\n")
        handle.write(f"- **Firmware type:** {file_info.get('firmware_type', 'unknown')}\n")
        handle.write(f"- **Flight stack:** {file_info.get('flight_stack', 'unknown')}\n")
        handle.write(f"- **Version:** {file_info.get('version', 'unknown')}\n")
        handle.write(f"- **Confidence:** {file_info.get('confidence', 0.0)}\n")
        handle.write(f"- **Processor family:** {file_info.get('processor_family', 'unknown')}\n")
        handle.write(f"- **Board type:** {file_info.get('board_type', 'unknown')}\n")
        handle.write(f"- **Detected parsers:** {', '.join(file_info.get('detected_parsers', [])) or 'none'}\n")
        handle.write(f"- **Date analyzed:** {file_info.get('date_analyzed', 'unknown')}\n")
        handle.write(f"- **Mime type:** {file_info.get('mime_type', 'unknown')}\n")
        handle.write(f"- **Detected signature:** {file_info.get('signature', 'unknown')}\n")
        handle.write(f"- **Estimated entropy:** {file_info.get('entropy', 0.0)}\n")
        handle.write(f"- **Extracted strings:** {file_info.get('strings_count', 0)}\n")
        if file_info.get('duplicate_count'):
            handle.write(f"- **Duplicate count:** {file_info.get('duplicate_count')}\n")
            handle.write(f"- **Duplicate of:** {', '.join(file_info.get('duplicate_of', []))}\n")
        handle.write("\n")

        # ELF details
        if file_info.get("elf"):
            handle.write("## ELF Details\n\n")
            elf = file_info["elf"]
            handle.write(f"- **Class:** {elf.get('class')}\n")
            handle.write(f"- **Machine:** {elf.get('machine')}\n\n")

        # Intel HEX details
        if file_info.get("intel_hex_lines"):
            handle.write("## Intel HEX Summary\n\n")
            handle.write(f"- **Lines:** {file_info.get('intel_hex_lines')}\n\n")
            sample = file_info.get("intel_hex_sample", [])
            if sample:
                handle.write("### Sample Intel HEX lines\n\n")
                for line in sample:
                    handle.write(f"- `{line}`\n")

        if file_info.get("parser_details"):
            handle.write("## Parser Metadata\n\n")
            handle.write("The parser plugins that matched this firmware and their inferred metadata are shown below.\n\n")
            for parser in file_info["parser_details"]:
                handle.write(f"### {parser.get('name', 'unknown')}\n")
                handle.write(f"- **Detected:** {parser.get('detected')}\n")
                handle.write(f"- **Firmware type:** {parser.get('firmware_type', 'unknown')}\n")
                handle.write(f"- **Flight stack:** {parser.get('flight_stack', 'unknown')}\n")
                handle.write(f"- **Version:** {parser.get('version', 'unknown')}\n")
                handle.write(f"- **Confidence:** {parser.get('confidence', 0.0)}\n")
                handle.write(f"- **Processor family:** {parser.get('processor_family', 'unknown')}\n")
                handle.write(f"- **Board type:** {parser.get('board_type', 'unknown')}\n")
                handle.write(f"- **Notes:** {parser.get('notes', 'none')}\n\n")

        if file_info.get("strings"):
            handle.write("## Sample Strings\n\n")
            handle.write("The first extracted printable strings are shown below.\n\n")
            for string in file_info["strings"][:40]:
                safe = string.replace("`", "'")
                handle.write(f"- `{safe}`\n")


def _safe_filename(name: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    if not safe_name:
        return "file-report"
    return safe_name
