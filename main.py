#!/usr/bin/env python3
"""make.fun entry: Sum up 22 November 2026's world news in one image.

The entry image lives beside this program as entry.png. Running the
program copies it to /output/entry.png, byte for byte, so repeated runs
always produce identical output. No network, no randomness, no arguments.
"""
import hashlib
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
TARGET = Path("/output/entry.png")
MAX_BYTES = 1_048_576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing {SOURCE}", file=sys.stderr)
        return 1
    data = SOURCE.read_bytes()
    if not data.startswith(PNG_MAGIC):
        print("entry.png is not a PNG", file=sys.stderr)
        return 1
    # PNG IHDR: width and height are the first 8 bytes after the 8-byte
    # signature + 8-byte chunk header (length 4 + type 4).
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width > 1024 or height > 1024:
        print(f"entry.png is {width}x{height}, over the 1024x1024 cap",
              file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print(f"entry.png is {len(data)} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(data)
    print(f"wrote {TARGET} ({len(data)} bytes, sha256 {digest(TARGET)[:16]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
