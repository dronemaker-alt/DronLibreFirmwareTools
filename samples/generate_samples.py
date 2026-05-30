"""Generate sample firmware test files for DronLibreFirmwareTools.

Each supported parser gets one representative sample file in both the parser-specific
sample folder and the shared `samples/input` folder, so the analysis engine can be
exercised directly against the input set.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "input"
PARSER_DIRS = {
    "DJI": ROOT / "DJI",
    "Betaflight": ROOT / "Betaflight",
    "INAV": ROOT / "INAV",
    "ArduPilot": ROOT / "Ardupilot",
    "ESP32": ROOT / "ESP32",
    "STM32": ROOT / "STM32",
}


def write_sample(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"Written sample: {path}")


def dji_sample() -> bytes:
    return b"DJI\nFW_v1.2.3\nOSDK firmware package for flight controller\n"


def betaflight_sample() -> bytes:
    return b"Betaflight\nSTM32F4\nv4.4.0\nblackbox logging enabled\n"


def inav_sample() -> bytes:
    return b"INAV\nv4.5.0\nflight controller firmware\nSTM32F7\n"


def ardupilot_sample() -> bytes:
    return b"ArduPilot\nAPM\nmission planner\nfirmware version 4.3.5\n"


def esp32_sample() -> bytes:
    return b"ESP32\nESP-IDF v5.0\nWi-Fi + Bluetooth firmware image\n"


def stm32_sample() -> bytes:
    # Create a minimal STM32-like vector table with valid SRAM SP and Flash reset address.
    sp = (0x20001000).to_bytes(4, "little")
    reset = (0x08090000).to_bytes(4, "little")
    return sp + reset + b"STM32F7\nfirmware\nflash image\n"


def generate_samples() -> None:
    samples = {
        "dji_firmware_example.bin": dji_sample(),
        "betaflight_firmware_example.bin": betaflight_sample(),
        "inav_firmware_example.bin": inav_sample(),
        "ardupilot_firmware_example.bin": ardupilot_sample(),
        "esp32_firmware_example.bin": esp32_sample(),
        "stm32_firmware_example.bin": stm32_sample(),
    }

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, data in samples.items():
        sample_path = INPUT_DIR / filename
        write_sample(sample_path, data)

    for vendor, directory in PARSER_DIRS.items():
        sample_filename = f"{vendor.lower()}_firmware_example.bin"
        sample_path = directory / sample_filename
        write_sample(sample_path, samples[sample_filename])

    print("Sample firmware generation complete.")


if __name__ == "__main__":
    generate_samples()
