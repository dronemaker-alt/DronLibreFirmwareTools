from src.file_signatures import detect_file_signature


def test_detect_zip_signature() -> None:
    assert detect_file_signature(b"PK\x03\x04Hello") == "ZIP archive"


def test_detect_png_signature() -> None:
    assert detect_file_signature(b"\x89PNG\r\n\x1a\nRest of data") == "PNG image"


def test_detect_unknown_signature() -> None:
    assert detect_file_signature(b"no signature here") == "unknown"
