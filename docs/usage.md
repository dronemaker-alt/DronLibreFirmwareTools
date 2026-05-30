# Usage

Basic CLI usage

Place firmware files in `samples/input/` and run the analyzer. By default the CLI reads `samples/input` if no input directory is provided.

```bash
# Analyze samples/input and write reports to reports/
python -m src.cli samples/input --output reports

# Explicitly specify input and output
python -m src.cli path/to/firmware_folder --output path/to/reports
```

Outputs

- `reports/analysis_report.json` — JSON array with per-file metadata
- `reports/index.md` — Markdown index linking to per-file reports
- `reports/<file>.md` — per-file detailed Markdown report

Notes

- The tool is read-only and will not modify the original firmware files.
- For best results, run the analyzer on copies of original images kept in a safe location.
- Use the `tests/` folder as examples for expected outputs.
