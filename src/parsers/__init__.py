"""Parser plugin loader for DronLibreFirmwareTools."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, TypedDict


class ParserResult(TypedDict, total=False):
    detected: bool
    name: str
    firmware_type: str
    processor_family: str
    flight_stack: str
    version: str
    confidence: float
    board_type: str
    notes: str


class ParserMetadata(TypedDict, total=False):
    name: str
    version: str
    supported_file_types: List[str]
    status: str
    description: str


def _load_parser_module(path: Path) -> ModuleType:
    name = f"{__name__}.{path.name}"
    spec = importlib.util.spec_from_file_location(name, path / "__init__.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load parser module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def get_parser_metadata(module: ModuleType) -> ParserMetadata:
    return {
        "name": getattr(module, "NAME", module.__name__),
        "version": getattr(module, "VERSION", "0.1.0"),
        "supported_file_types": getattr(module, "SUPPORTED_FILE_TYPES", [".bin", ".hex", ".elf"]),
        "status": getattr(module, "STATUS", "active"),
        "description": getattr(module, "DESCRIPTION", ""),
    }


def load_parsers() -> List[ModuleType]:
    plugins: List[ModuleType] = []
    parser_dir = Path(__file__).parent
    for path in sorted(parser_dir.iterdir(), key=lambda p: p.name):
        if not path.is_dir() or path.name.startswith("__"):
            continue
        init_file = path / "__init__.py"
        if not init_file.exists():
            continue

        try:
            module = _load_parser_module(path)
            if hasattr(module, "parse"):
                plugins.append(module)
        except Exception:
            continue

    return plugins


PARSERS = load_parsers()
