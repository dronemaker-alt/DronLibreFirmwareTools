# Roadmap

## Phase 1 - Prototype

- Establish Python project scaffold
- Support input folder scanning for firmware files
- Identify common file formats and collect metadata
- Detect archive/container formats and extract safely when possible
- Generate analysis reports with discovered files, sizes, hashes, strings, and architecture clues
- Create docs, tests, samples, and report templates

## Phase 2 - Analysis Enhancements

- Add file-type heuristics for DJI, PX4, ArduPilot, and generic firmware blobs
- Support additional container formats such as ZIP, TAR, LZMA, SquashFS, and proprietary DJI archives
- Add processor fingerprinting heuristics for ARM, MIPS, x86, and RISC-V
- Improve report layout and machine-readable export formats (JSON, CSV)

## Phase 3 - Forensics and Documentation

- Add detailed firmware structure reporting
- Add extraction of readable strings and binary sections
- Add documentation for safe usage and legal boundaries
- Provide workflows for research, reverse engineering, and validation

## Constraints

- Analysis-only: no modification, no signing, no flashing
- Always assume firmware was obtained legally and ethically
- Preserve original files and report on copies only
