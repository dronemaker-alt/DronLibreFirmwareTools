# Supported Formats

This file documents the formats the analyzer recognises by signature and how to extend support.

Recognised signatures (examples)

- ZIP (PK\x03\x04, PK\x05\x06)
- GZIP (\x1f\x8b\x08)
- TAR / ustar (offset 257: "ustar\x0000")
- 7z, RAR, XZ, LZMA, BZIP2
- ELF (\x7fELF) and PE (MZ)
- Image formats: PNG, JPEG, BMP
- PDF documents
- Heuristic vendor markers (e.g., DJI-specific headers)

Extending signatures

Signatures are defined in `src/file_signatures.py` as a list of tuples `(label, offset, signature_bytes)`.
To add a new signature:

1. Open `src/file_signatures.py`.
2. Add an entry to the `FILE_SIGNATURES` list with a descriptive `label`, the `offset` to check, and the signature bytes.
3. Add unit tests in `tests/` demonstrating detection for the new signature.

Limitations

- Detection is based on fixed signatures and heuristics only. Full format parsing or extraction requires dedicated parsers.
- Some vendor formats are proprietary and may require reverse-engineering; only add formats when you have a legal right to the sample data.

If you want help adding support for a specific format, open an issue and attach a legally shareable sample or format notes.
