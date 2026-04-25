#!/usr/bin/env python3
"""
mut_table_analyzer.py — Analyze and compare MUT table candidates from ROM files.

This tool helps verify MUT table candidates by:
- Displaying full table layouts
- Comparing tables across multiple ROM versions
- Identifying patterns in request IDs and memory addresses
- Generating EcuFlash XML snippets for testing

Examples:
    python scripts/mut_table_analyzer.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex --offset 0xFE5E
    python scripts/mut_table_analyzer.py cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
        cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex --offset 0xFE5E --compare
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TABLE_WIDTH = 8
TABLE_HEIGHT = 15
TABLE_WORDS = TABLE_WIDTH * TABLE_HEIGHT


@dataclass
class MUTEntry:
    """Represents a single MUT table entry."""
    request_id: int
    address: int
    is_pointer_like: bool
    is_zero: bool
    is_ffff: bool

    def __str__(self) -> str:
        if self.is_zero:
            return f"Req 0x{self.request_id:02X}: NULL (0x0000)"
        elif self.is_ffff:
            return f"Req 0x{self.request_id:02X}: SENTINEL (0xFFFF)"
        else:
            return f"Req 0x{self.request_id:02X}: -> 0x{self.address:04X}"


def load_words(path: Path) -> list[int]:
    """Load ROM file as big-endian 16-bit words."""
    data = path.read_bytes()
    if len(data) % 2 != 0:
        data = data[:-1]
    return [int.from_bytes(data[i:i + 2], "big") for i in range(0, len(data), 2)]


def looks_like_pointer(value: int) -> bool:
    """Check if value looks like a RAM address pointer."""
    if value in {0x0000, 0xFFFF}:
        return False
    return 0x0700 <= value <= 0x9FFF


def extract_table(words: list[int], offset: int) -> list[int]:
    """Extract MUT table from ROM at given byte offset."""
    word_offset = offset // 2
    return words[word_offset:word_offset + TABLE_WORDS]


def parse_table_entries(table: list[int], layout: str = "dense") -> list[MUTEntry]:
    """Parse MUT table entries based on layout type."""
    entries = []

    if layout == "dense":
        # Dense layout: each word is an entry, request ID = index
        for idx, value in enumerate(table):
            entries.append(MUTEntry(
                request_id=idx,
                address=value,
                is_pointer_like=looks_like_pointer(value),
                is_zero=(value == 0x0000),
                is_ffff=(value == 0xFFFF),
            ))
    elif layout == "sparse_even":
        # Sparse layout: only even columns (0, 2, 4, 6) contain addresses
        # Request ID = row * 4 + (col / 2)
        for row in range(TABLE_HEIGHT):
            for col in [0, 2, 4, 6]:
                idx = row * TABLE_WIDTH + col
                if idx < len(table):
                    request_id = row * 4 + (col // 2)
                    entries.append(MUTEntry(
                        request_id=request_id,
                        address=table[idx],
                        is_pointer_like=looks_like_pointer(table[idx]),
                        is_zero=(table[idx] == 0x0000),
                        is_ffff=(table[idx] == 0xFFFF),
                    ))

    return entries


def print_table_layout(table: list[int], offset: int) -> None:
    """Print formatted table layout."""
    print(f"\n{'='*80}")
    print(f"MUT Table at offset 0x{offset:06X}")
    print(f"{'='*80}\n")

    print(f"Full table layout ({TABLE_HEIGHT} rows × {TABLE_WIDTH} columns):\n")
    print("      Col:   0       1       2       3       4       5       6       7")
    print("      " + "-" * 68)

    for row in range(TABLE_HEIGHT):
        row_start = row * TABLE_WIDTH
        row_end = row_start + TABLE_WIDTH
        row_words = table[row_start:row_end]

        byte_addr = offset + (row * TABLE_WIDTH * 2)
        row_str = f"  Row {row:2d} (0x{byte_addr:06X}): "

        for word in row_words:
            if word == 0x0000:
                row_str += "  NULL  "
            elif word == 0xFFFF:
                row_str += "  FFFF  "
            elif looks_like_pointer(word):
                row_str += f" {word:04X}* "
            else:
                row_str += f" {word:04X}  "

        print(row_str)

    print("\n  * = looks like a RAM pointer (0x0700-0x9FFF)\n")


def analyze_table_stats(table: list[int]) -> dict[str, Any]:
    """Compute statistics about the table."""
    pointer_count = sum(1 for w in table if looks_like_pointer(w))
    zero_count = table.count(0x0000)
    ffff_count = table.count(0xFFFF)
    other_count = len(table) - pointer_count - zero_count - ffff_count

    unique_values = len(set(table))

    return {
        "total_entries": len(table),
        "pointers": pointer_count,
        "zeros": zero_count,
        "sentinels": ffff_count,
        "other": other_count,
        "unique_values": unique_values,
        "pointer_pct": (pointer_count / len(table)) * 100,
    }


def print_table_stats(stats: dict[str, Any]) -> None:
    """Print table statistics."""
    print("Table Statistics:")
    print(f"  Total entries:     {stats['total_entries']}")
    print(f"  RAM pointers:      {stats['pointers']} ({stats['pointer_pct']:.1f}%)")
    print(f"  NULL (0x0000):     {stats['zeros']}")
    print(f"  Sentinel (0xFFFF): {stats['sentinels']}")
    print(f"  Other values:      {stats['other']}")
    print(f"  Unique values:     {stats['unique_values']}")
    print()


def compare_tables(tables: dict[str, list[int]], offset: int) -> None:
    """Compare tables across multiple ROM files."""
    print(f"\n{'='*80}")
    print(f"Table Comparison at offset 0x{offset:06X}")
    print(f"{'='*80}\n")

    if len(tables) < 2:
        print("Need at least 2 ROM files to compare.")
        return

    # Find differences
    rom_names = list(tables.keys())
    base_table = tables[rom_names[0]]

    print(f"Comparing against base: {rom_names[0]}\n")

    for rom_name in rom_names[1:]:
        compare_table = tables[rom_name]
        differences = []

        for idx, (base_val, compare_val) in enumerate(zip(base_table, compare_table)):
            if base_val != compare_val:
                row = idx // TABLE_WIDTH
                col = idx % TABLE_WIDTH
                differences.append((idx, row, col, base_val, compare_val))

        print(f"vs {rom_name}:")
        if not differences:
            print("  ✓ Tables are identical\n")
        else:
            print(f"  ✗ Found {len(differences)} difference(s):\n")
            for idx, row, col, base_val, comp_val in differences[:20]:  # Limit to 20
                byte_addr = offset + (idx * 2)
                print(f"    Position [{row},{col}] (0x{byte_addr:06X}): "
                      f"0x{base_val:04X} -> 0x{comp_val:04X}")
            if len(differences) > 20:
                print(f"    ... and {len(differences) - 20} more")
            print()


def generate_ecuflash_xml(offset: int, table: list[int], layout: str = "dense") -> str:
    """Generate EcuFlash XML snippet for testing."""
    entries = parse_table_entries(table, layout)

    # Filter to interesting entries (pointers only)
    pointer_entries = [e for e in entries if e.is_pointer_like]

    xml = f'<!-- MUT Table Definition - Test at offset 0x{offset:06X} -->\n'
    xml += f'<muttable offset="0x{offset:X}" layout="{layout}">\n'

    # Sample a few entries for testing
    for entry in pointer_entries[:10]:
        xml += f'  <mutentry requestid="0x{entry.request_id:02X}" address="0x{entry.address:04X}" />\n'

    if len(pointer_entries) > 10:
        xml += f'  <!-- ... and {len(pointer_entries) - 10} more pointer entries -->\n'

    xml += '</muttable>\n'

    return xml


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze MUT table candidates from ROM files."
    )
    parser.add_argument(
        "roms",
        nargs="+",
        help="One or more ROM files to analyze.",
    )
    parser.add_argument(
        "--offset",
        required=True,
        help="Byte offset of MUT table (e.g., 0xFE5E).",
    )
    parser.add_argument(
        "--layout",
        choices=["dense", "sparse_even"],
        default="dense",
        help="MUT table layout type (default: dense).",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare tables across multiple ROM files.",
    )
    parser.add_argument(
        "--xml",
        action="store_true",
        help="Generate EcuFlash XML snippet.",
    )

    args = parser.parse_args()

    # Parse offset
    offset_str = args.offset.replace("0x", "").replace("0X", "")
    offset = int(offset_str, 16)

    # Load ROM files
    roms = [Path(rom) for rom in args.roms]
    missing = [str(rom) for rom in roms if not rom.is_file()]
    if missing:
        for rom in missing:
            print(f"ERROR: file not found: {rom}")
        return 1

    # Extract tables
    tables = {}
    for rom in roms:
        words = load_words(rom)
        table = extract_table(words, offset)
        tables[rom.name] = table

    # Display each table
    for rom_name, table in tables.items():
        print(f"\n{'#'*80}")
        print(f"# ROM: {rom_name}")
        print(f"{'#'*80}")

        print_table_layout(table, offset)

        stats = analyze_table_stats(table)
        print_table_stats(stats)

        if args.xml:
            print("EcuFlash XML snippet:")
            print(generate_ecuflash_xml(offset, table, args.layout))

    # Compare if requested
    if args.compare and len(tables) > 1:
        compare_tables(tables, offset)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

