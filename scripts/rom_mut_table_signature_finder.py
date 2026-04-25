#!/usr/bin/env python3
"""rom_mut_table_signature_finder.py — Find MUT table base by signature bytes.

This script searches one or more ROM files for an exact 16-byte signature that
commonly appears at/near the beginning of a MUT table region:

    FFFF 0000 0000 0000 0000 0000 0000 0000

Interpreted as big-endian 16-bit words, this is the byte sequence:

    FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00

It prints every match offset (byte offset) and, optionally, a small hex context
around the match so you can sanity-check the surrounding data.

Examples:
    python scripts/rom_mut_table_signature_finder.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex

    # Show 64 bytes of context before/after each hit
    python scripts/rom_mut_table_signature_finder.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex --context 64

Notes:
- This is intentionally "dumb" compared to `rom_mut_finder.py`: it doesn't try
  to score/guess. It just finds the signature.
- ROMs are treated as raw bytes; offsets printed are file byte offsets.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SIGNATURE_WORDS_BE = [0xFFFF] + [0x0000] * 7  # 8 words == 16 bytes
SIGNATURE_BYTES_BE = b"".join(w.to_bytes(2, "big") for w in SIGNATURE_WORDS_BE)
SIGNATURE_BYTES_LE = b"".join(w.to_bytes(2, "little") for w in SIGNATURE_WORDS_BE)


@dataclass(frozen=True)
class Hit:
    offset: int


def iter_signature_hits(data: bytes, signature: bytes) -> Iterable[Hit]:
    """Yield all non-overlapping hits of signature in data."""
    start = 0
    while True:
        idx = data.find(signature, start)
        if idx == -1:
            return
        yield Hit(offset=idx)
        # Step forward by 1 to allow overlapping matches (safe; signature is 16 bytes)
        start = idx + 1


def hex_bytes(chunk: bytes) -> str:
    return " ".join(f"{b:02X}" for b in chunk)


def dump_context(data: bytes, hit_offset: int, context: int) -> str:
    if context <= 0:
        return ""

    start = max(0, hit_offset - context)
    end = min(len(data), hit_offset + len(SIGNATURE_BYTES_BE) + context)

    before = data[start:hit_offset]
    sig = data[hit_offset : hit_offset + len(SIGNATURE_BYTES_BE)]
    after = data[hit_offset + len(SIGNATURE_BYTES_BE) : end]

    return (
        f"      context [0x{start:06X}..0x{end:06X})\n"
        f"        before: {hex_bytes(before)}\n"
        f"        match : {hex_bytes(sig)}\n"
        f"        after : {hex_bytes(after)}\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find MUT table base by searching for the byte signature: FFFF 0000 0000 0000 0000 0000 0000 0000"
    )
    parser.add_argument("roms", nargs="+", help="One or more ROM files to scan")
    parser.add_argument(
        "--endianness",
        choices=["big", "little"],
        default="big",
        help="Word endianness used to interpret the signature (default: big).",
    )
    parser.add_argument(
        "--align",
        type=int,
        default=1,
        help="Only report hits whose offset is a multiple of this value (default: 1). Use 2 for 16-bit alignment.",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=0,
        help="If >0, dump this many bytes of context before/after each hit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    signature = SIGNATURE_BYTES_BE if args.endianness == "big" else SIGNATURE_BYTES_LE

    roms = [Path(p) for p in args.roms]
    missing = [str(p) for p in roms if not p.is_file()]
    if missing:
        for p in missing:
            print(f"ERROR: file not found: {p}")
        return 1

    any_hits = False

    for rom in roms:
        data = rom.read_bytes()
        hits = [h for h in iter_signature_hits(data, signature) if (h.offset % args.align) == 0]

        print(f"ROM: {rom}")
        print(f"  size: {len(data)} bytes")
        print(f"  signature: {hex_bytes(signature)} ({args.endianness}-endian words)")
        print(f"  hits: {len(hits)}")

        if hits:
            any_hits = True

        for i, hit in enumerate(hits, start=1):
            print(f"  {i:>2}. offset=0x{hit.offset:06X} ({hit.offset} bytes)")
            context_dump = dump_context(data, hit.offset, args.context)
            if context_dump:
                print(context_dump, end="")

        print()

    return 0 if any_hits else 2


if __name__ == "__main__":
    raise SystemExit(main())

