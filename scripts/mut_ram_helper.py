#!/usr/bin/env python3
"""
mut_ram_helper.py - Helper for creating direct RAM pointer tables in EcuFlash XML

Instead of modifying the MUT table, this approach creates simple 1D table entries
that point directly to RAM addresses where the ECU stores runtime values.

Usage:
    python scripts/mut_ram_helper.py --base-offset 0x38062 --ram-addresses 0x896C 0x896D
    python scripts/mut_ram_helper.py --generate-xml --start-rom 0x38062 --ram-start 0x896C --count 10
"""

from __future__ import annotations

import argparse
from pathlib import Path


def ram_to_hex16(ram_address: int) -> str:
    """Convert RAM address to hex16 format for XML."""
    return f"{ram_address:04X}"


def generate_xml_entry(name: str, rom_address: str, description: str = "") -> str:
    """Generate a single XML table entry for a RAM pointer."""
    desc = f' <!-- {description} -->' if description else ''
    return f'  <table name="{name}" address="{rom_address}" type="1D" level="1" scaling="uint16" />{desc}'


def generate_sequential_entries(
    base_rom_offset: int,
    start_ram: int,
    count: int,
    prefix: str = "2byte_",
) -> list[str]:
    """Generate sequential XML entries for RAM pointers."""
    entries = []

    for i in range(count):
        rom_offset = base_rom_offset + (i * 4)  # Each entry is 4 bytes apart (2 for pointer)
        ram_address = start_ram + i

        name = f"{prefix}{i:02d}"
        rom_addr_hex = f"0x{rom_offset:X}"
        desc = f"Points to RAM 0x{ram_address:04X} (decimal {ram_address})"

        entry = generate_xml_entry(name, rom_addr_hex, desc)
        entries.append(entry)

    return entries


def analyze_mut_table_at_offset(rom_path: Path, mut_offset: int) -> list[tuple[int, int]]:
    """
    Read MUT table from ROM and extract request ID -> RAM address mappings.
    Returns list of (request_id, ram_address) tuples.
    """
    data = rom_path.read_bytes()

    # MUT table is 15 rows x 8 columns = 120 words
    TABLE_WIDTH = 8
    TABLE_HEIGHT = 15

    entries = []

    for row in range(TABLE_HEIGHT):
        for col in range(TABLE_WIDTH):
            # Sparse layout: only even columns (0, 2, 4, 6) contain data
            if col % 2 == 0:
                offset = mut_offset + (row * TABLE_WIDTH * 2) + (col * 2)

                if offset + 1 < len(data):
                    # Read 16-bit big-endian value
                    ram_addr = int.from_bytes(data[offset:offset+2], "big")

                    # Calculate request ID for sparse layout
                    request_id = (row * 4) + (col // 2)

                    # Only include valid RAM addresses
                    if 0x0700 <= ram_addr <= 0x9FFF:
                        entries.append((request_id, ram_addr))

    return entries


def find_rom_space_for_pointers(rom_path: Path, count: int) -> list[int]:
    """
    Suggest ROM addresses that could be used for custom RAM pointers.
    Looks for regions with 0xFFFF (unused space).
    """
    data = rom_path.read_bytes()
    candidates = []

    # Look in common areas for custom data (typically near end of ROM)
    search_start = 0x30000  # Start searching from 192KB
    search_end = min(len(data) - (count * 4), 0x3F000)

    # Need (count * 4) bytes of 0xFFFF
    needed_bytes = count * 4

    for offset in range(search_start, search_end, 2):
        # Check if we have enough 0xFFFF bytes
        is_empty = all(
            data[offset + i:offset + i + 2] == b'\xFF\xFF'
            for i in range(0, needed_bytes, 2)
        )

        if is_empty:
            candidates.append(offset)

            # Return first 5 candidates
            if len(candidates) >= 5:
                break

    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Helper for creating direct RAM pointer tables in EcuFlash XML"
    )

    # Mode selection
    parser.add_argument(
        "--generate-xml",
        action="store_true",
        help="Generate XML entries for sequential RAM addresses",
    )
    parser.add_argument(
        "--analyze-mut",
        action="store_true",
        help="Analyze existing MUT table in ROM",
    )
    parser.add_argument(
        "--find-space",
        action="store_true",
        help="Find available ROM space for custom pointers",
    )

    # Parameters
    parser.add_argument(
        "--rom",
        type=str,
        help="Path to ROM file",
    )
    parser.add_argument(
        "--mut-offset",
        type=str,
        help="MUT table offset in ROM (e.g., 0x96C8)",
    )
    parser.add_argument(
        "--start-rom",
        type=str,
        help="Starting ROM offset for pointer entries (e.g., 0x38062)",
    )
    parser.add_argument(
        "--ram-start",
        type=str,
        help="Starting RAM address (e.g., 0x896C or 35164)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of entries to generate (default: 10)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="2byte_",
        help="Prefix for table names (default: 2byte_)",
    )

    args = parser.parse_args()

    # Generate XML mode
    if args.generate_xml:
        if not args.start_rom or not args.ram_start:
            print("ERROR: --start-rom and --ram-start are required for --generate-xml")
            return 1

        start_rom = int(args.start_rom.replace("0x", ""), 16)

        # Parse RAM address (could be hex or decimal)
        ram_str = args.ram_start.replace("0x", "")
        try:
            ram_start = int(ram_str, 16)
        except ValueError:
            ram_start = int(args.ram_start)

        print(f"<!-- Custom 2-byte RAM pointer tables -->")
        print(f"<!-- ROM offset: 0x{start_rom:X}, RAM start: 0x{ram_start:04X} (decimal {ram_start}) -->\n")

        entries = generate_sequential_entries(start_rom, ram_start, args.count, args.prefix)

        for entry in entries:
            print(entry)

        print()
        print(f"<!-- Total: {args.count} entries -->")
        print(f"<!-- ROM space used: 0x{start_rom:X} to 0x{start_rom + (args.count * 4):X} ({args.count * 4} bytes) -->")

        return 0

    # Analyze MUT table mode
    if args.analyze_mut:
        if not args.rom or not args.mut_offset:
            print("ERROR: --rom and --mut-offset are required for --analyze-mut")
            return 1

        rom_path = Path(args.rom)
        if not rom_path.is_file():
            print(f"ERROR: ROM file not found: {rom_path}")
            return 1

        mut_offset = int(args.mut_offset.replace("0x", ""), 16)

        print(f"Analyzing MUT table at offset 0x{mut_offset:X} in {rom_path.name}\n")

        entries = analyze_mut_table_at_offset(rom_path, mut_offset)

        print(f"Found {len(entries)} valid RAM pointers:\n")
        print("Request ID | RAM Address | Decimal")
        print("-" * 40)

        for req_id, ram_addr in entries:
            print(f"  0x{req_id:02X}      | 0x{ram_addr:04X}      | {ram_addr}")

        return 0

    # Find available ROM space mode
    if args.find_space:
        if not args.rom:
            print("ERROR: --rom is required for --find-space")
            return 1

        rom_path = Path(args.rom)
        if not rom_path.is_file():
            print(f"ERROR: ROM file not found: {rom_path}")
            return 1

        print(f"Finding available ROM space for {args.count} pointer entries in {rom_path.name}\n")
        print(f"Need {args.count * 4} bytes ({args.count} entries × 4 bytes each)\n")

        candidates = find_rom_space_for_pointers(rom_path, args.count)

        if candidates:
            print(f"Found {len(candidates)} suitable locations:\n")
            for i, offset in enumerate(candidates, 1):
                end_offset = offset + (args.count * 4)
                print(f"{i}. 0x{offset:06X} to 0x{end_offset:06X} ({args.count * 4} bytes)")
        else:
            print("No suitable empty space found.")
            print("Try reducing --count or searching manually.")

        return 0

    # No mode selected
    print("ERROR: Must specify --generate-xml, --analyze-mut, or --find-space")
    print("Use --help for usage information")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

