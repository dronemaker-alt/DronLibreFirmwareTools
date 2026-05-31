# DronLibreFirmwareTools

DronLibreFirmwareTools is an analysis-only firmware archaeology and reporting toolkit for legally obtained drone firmware and related binary packages.

The project is meant to help with safe inspection, documentation, board identification, metadata extraction, and repeatable reporting. It does not modify, patch, sign, flash, unlock, or bypass firmware protections.

## Quick facts

- Project owner: `dronemaker-alt`
- Default branch: `master`
- Focus: read-only firmware analysis and drone recovery documentation
- Prototype implementation: Python modules under `src/`
- Related repository: `DronLibre-Rescue-Logs`

## Goals

- Identify file types and firmware package structure.
- Compute secure hashes for traceability.
- Extract printable strings for safe inspection.
- Estimate entropy to locate compressed or encrypted regions.
- Detect known archive, container, image, and executable signatures.
- Generate human-readable and machine-readable reports.
- Keep a clean paper trail before working with unknown boards or firmware files.

## Project layout

- `src/` - core Python modules
  - `analyzer.py` - coordinates scanning and analysis
  - `file_signatures.py` - known magic bytes and signature detection
  - `report_generator.py` - Markdown and JSON report generation
  - `utils.py` - hashing, entropy, string extraction, and helpers
- `docs/` - project documentation and design notes
- `samples/input/` - local firmware input folder
- `reports/` - generated analysis reports
- `tests/` - unit tests and lightweight checks

## Supported and recognized formats

The analyzer is intended to detect common container and binary signatures. Current or planned examples include:

- ZIP
- TAR / ustar
- GZIP / BZIP2 / XZ / LZMA
- 7z and RAR
- ELF and PE executable formats
- PNG, JPEG, BMP, and PDF
- Heuristic vendor markers, including DJI-style markers when safely detectable
- Embedded filesystem candidates such as SquashFS and YAFFS as future work

## Basic usage

Create and activate a Python virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activation usually looks like this:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Place legally obtained firmware files in `samples/input/`, then run the analyzer:

```bash
python -m src.cli samples/input --output reports
```

Expected output:

- `reports/analysis_report.json` - machine-readable summary
- `reports/index.md` - report index
- `reports/<file>.md` - per-file report with size, hashes, detected signatures, entropy estimate, and sample strings

## Manual repository health check

Before testing unknown boards or firmware packages:

1. Confirm the board identity, chip family, USB port, and visible markings.
2. Capture initial serial output before flashing or changing anything.
3. Save screenshots, terminal output, or copied serial logs.
4. Put session notes under `docs/` or the related rescue-log repository.
5. Keep firmware samples out of public commits unless they are legally shareable.
6. Treat all firmware handling as read-only unless you are working on your own hardware and have a clear recovery path.

## Roadmap

### Firmware analysis

- Aircraft and board family identification
- Firmware version extraction
- Processor and architecture hints
- Firmware package comparison
- Signature library expansion
- Read-only container extraction where legally and technically appropriate

### Reporting and database work

- Known firmware signature library
- Version compatibility notes
- Supported hardware database
- Markdown, JSON, and CSV reports
- Integration with DronLibre rescue case notes

### Live diagnostics documentation

Future documentation may cover safe observation and logging of:

- Battery voltage
- GPS health and lock status
- IMU health indicators
- Compass status
- Radio link quality
- Temperature readings
- System health reports

### Initial platform targets

- DJI Mini, Mavic, Phantom, and Inspire families
- ArduPilot
- Betaflight
- INAV
- STM32 flight controllers
- ESP32 companion systems
- NXP K66 / Aesir flight-system experiments

## Safety and legal boundary

This repository is for analysis, research, repair documentation, and forensic-style inspection of firmware you are authorized to handle.

Do not use this project to bypass access controls, defeat firmware protections, unlock restricted features, modify vendor firmware, or flash unknown binaries onto aircraft that could create a safety hazard.

## License

This project is provided under the MIT license. See `LICENSE` for details.
