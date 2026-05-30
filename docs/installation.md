# Installation

These instructions cover a minimal setup to run the prototype analyzer locally.

Prerequisites

- Python 3.10 or later
- `pip` available
- Optional system libraries (for `python-magic`):
  - Linux: `libmagic` (package name `libmagic` or `file` in some distros)
  - Windows: `python-magic-bin` may be used as an alternative

Create virtual environment and install dependencies

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix/macOS
source .venv/bin/activate

python -m pip install -r requirements.txt
```

Troubleshooting

- If `python-magic` fails to detect types on Windows, consider installing `python-magic-bin` or omit MIME detection.
- Ensure your system has `libmagic` available when running on Linux.
