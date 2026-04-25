#!/usr/bin/env python3
"""
quick_mut_check.py — Quick validation of MUT table offset

This is a simple script that tells you if a given offset looks like a valid MUT table.
It's faster than running the full finder and gives you a yes/no answer.

Examples:
    python scripts/quick_mut_check.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex 0xFE5E
    python scripts/quick_mut_check.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex 0xFE5A 0xFE5E 0xFE60
"""

from __future__ import annotations

import sys
from pathlib import Path


TABLE_WIDTH = 8
TABLE_HEIGHT = 15
TABLE_WORDS = TABLE_WIDTH * TABLE_HEIGHT


def load_words(path: Path) -> list[int]:
    data = path.read_bytes()
    if len(data) % 2 != 0:
        data = data[:-1]
    return [int.from_bytes(data[i:i + 2], "big") for i in range(0, len(data), 2)]


def looks_like_pointer(value: int) -> bool:
    if value in {0x0000, 0xFFFF}:
        return False
    return 0x0700 <= value <= 0x9FFF


def check_mut_table(words: list[int], offset: int) -> dict:
    """Quick check if offset contains a valid MUT table."""
    word_offset = offset // 2
    table = words[word_offset:word_offset + TABLE_WORDS]

    if len(table) < TABLE_WORDS:
        return {
            "valid": False,
            "reason": "Offset too close to end of file",
        }

    pointers = sum(1 for w in table if looks_like_pointer(w))
    zeros = table.count(0x0000)
    ffffs = table.count(0xFFFF)

    # Quick validation rules
    has_enough_pointers = 12 <= pointers <= 80
    has_sentinels = ffffs > 0 or zeros > 0
    not_too_repetitive = len(set(table)) >= 8

    valid = has_enough_pointers and has_sentinels and not_too_repetitive

    result = {
        "valid": valid,
        "offset": offset,
        "pointers": pointers,
        "zeros": zeros,
        "ffffs": ffffs,
        "unique": len(set(table)),
        "confidence": "unknown",
    }

    # Confidence assessment
    if valid:
        if pointers >= 40 and (zeros + ffffs) >= 20:
            result["confidence"] = "HIGH ✓✓✓"
        elif pointers >= 25 and (zeros + ffffs) >= 10:
            result["confidence"] = "MEDIUM ✓✓"
        else:
            result["confidence"] = "LOW ✓"
    else:
        result["confidence"] = "INVALID ✗"
        if not has_enough_pointers:
            result["reason"] = f"Only {pointers} pointers (need 12-80)"
        elif not has_sentinels:
            result["reason"] = "No sentinel values (0x0000 or 0xFFFF)"
        elif not not_too_repetitive:
            result["reason"] = f"Too repetitive (only {len(set(table))} unique values)"

    return result


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/quick_mut_check.py ROM_FILE OFFSET [OFFSET2 ...]")
        print()
        print("Example:")
        print("  python scripts/quick_mut_check.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex 0xFE5E")
        print("  python scripts/quick_mut_check.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex 0xFE5A 0xFE5E 0xFE60")
        return 1

    rom_path = Path(sys.argv[1])
    offsets = sys.argv[2:]

    if not rom_path.is_file():
        print(f"ERROR: File not found: {rom_path}")
        return 1

    print(f"ROM: {rom_path.name}")
    print(f"Checking {len(offsets)} offset(s)...\n")

    words = load_words(rom_path)

    results = []
    for offset_str in offsets:
        offset = int(offset_str.replace("0x", "").replace("0X", ""), 16)
        result = check_mut_table(words, offset)
        results.append(result)

    # Sort by validity and confidence
    results.sort(key=lambda r: (r["valid"], r["pointers"]), reverse=True)

    print("Results:")
    print("-" * 80)

    for result in results:
        offset = result["offset"]
        confidence = result["confidence"]
        pointers = result["pointers"]
        zeros = result["zeros"]
        ffffs = result["ffffs"]
        unique = result["unique"]

        print(f"Offset 0x{offset:06X}: {confidence}")
        print(f"  Pointers: {pointers:3d}  |  Zeros: {zeros:3d}  |  FFFs: {ffffs:3d}  |  Unique: {unique:3d}")

        if not result["valid"] and "reason" in result:
            print(f"  Reason: {result['reason']}")

        print()

    # Print recommendation
    print("-" * 80)
    valid_results = [r for r in results if r["valid"]]

    if valid_results:
        best = valid_results[0]
        print(f"✓ RECOMMENDATION: Try offset 0x{best['offset']:06X} first ({best['confidence']})")

        if len(valid_results) > 1:
            print(f"  Alternative offsets: ", end="")
            alts = [f"0x{r['offset']:06X}" for r in valid_results[1:4]]
            print(", ".join(alts))
    else:
        print("✗ No valid MUT table candidates found at the specified offsets")
        print("  Run rom_mut_finder.py to scan the entire ROM")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

