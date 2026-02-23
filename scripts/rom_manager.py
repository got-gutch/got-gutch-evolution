#!/usr/bin/env python3
"""
rom_manager.py — Manage and compare Evo 8 ROM files.

ROM files follow the naming convention:
  {owner}_{car_year}_{car_model}_{MM}_{DD}_{YYYY}[_tune_{NNN}_{description}].{ext}

Examples:
  bgutch_2003_evo8_11_11_2025.bin
  bgutch_2003_evo8_11_11_2025_tune_010_wastegateclear.bin
  bgutch_2003_evo8_02_18_2026_tune_001_rpm_limit.hex

Commands:
  list    — list all ROMs under a directory with parsed metadata
  tunes   — show all tunes derived from a given base ROM
  diff    — byte-level diff between two ROM files

Usage:
  python scripts/rom_manager.py list cars/2003-evo-viii/roms
  python scripts/rom_manager.py tunes bgutch_2003_evo8_11_11_2025.bin \\
                                       --dir cars/2003-evo-viii/roms/tunes
  python scripts/rom_manager.py diff <rom_a> <rom_b>
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Filename parsing
# ---------------------------------------------------------------------------

_BASE_PATTERN = re.compile(
    r"^(?P<owner>[^_]+)"
    r"_(?P<car_year>\d{4})"
    r"_(?P<car_model>[^_]+)"
    r"_(?P<month>\d{2})_(?P<day>\d{2})_(?P<year>\d{4})"
    r"(?:_tune_(?P<tune_num>\d+)_(?P<description>.+))?"
    r"\.(?P<ext>bin|hex)$"
)


@dataclass
class RomMeta:
    path: Path
    owner: str
    car_year: str
    car_model: str
    date: str          # YYYY-MM-DD
    is_tune: bool
    tune_num: str      # e.g. "010", empty string for base ROMs
    description: str   # e.g. "wastegateclear", empty string for base ROMs
    ext: str           # "bin" or "hex"

    @property
    def base_stem(self) -> str:
        """The stem shared by a base ROM and all tunes derived from it."""
        return f"{self.owner}_{self.car_year}_{self.car_model}_{self._date_tag}"

    @property
    def _date_tag(self) -> str:
        """MM_DD_YYYY extracted from the parsed date."""
        y, m, d = self.date.split("-")
        return f"{m}_{d}_{y}"


def parse_rom_filename(path: Path) -> RomMeta | None:
    """Return RomMeta for *path*, or None if the name doesn't match."""
    m = _BASE_PATTERN.match(path.name)
    if not m:
        return None
    month, day, year = m["month"], m["day"], m["year"]
    return RomMeta(
        path=path,
        owner=m["owner"],
        car_year=m["car_year"],
        car_model=m["car_model"],
        date=f"{year}-{month}-{day}",
        is_tune=m["tune_num"] is not None,
        tune_num=m["tune_num"] or "",
        description=m["description"] or "",
        ext=m["ext"],
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_list(directory: str) -> int:
    """List all recognised ROM files under *directory*."""
    root = Path(directory)
    if not root.is_dir():
        print(f"ERROR: directory not found: {directory}", file=sys.stderr)
        return 1

    roms = sorted(
        (parse_rom_filename(p) for p in root.rglob("*.bin") if parse_rom_filename(p) is not None),
        key=lambda r: (r.date, r.is_tune, r.tune_num),
    )
    hex_roms = sorted(
        (parse_rom_filename(p) for p in root.rglob("*.hex") if parse_rom_filename(p) is not None),
        key=lambda r: (r.date, r.is_tune, r.tune_num),
    )
    roms = roms + hex_roms

    if not roms:
        print("No ROM files found.")
        return 0

    print(f"\n{'File':<60} {'Date':<12} {'Type':<8} {'Tune#':<6} {'Description'}")
    print("-" * 110)
    for r in roms:
        kind = "tune" if r.is_tune else "base"
        print(
            f"{r.path.name:<60} {r.date:<12} {kind:<8} {r.tune_num:<6} {r.description}"
        )
    return 0


def cmd_tunes(base_rom: str, directory: str) -> int:
    """Show all tunes derived from *base_rom* found in *directory*."""
    base_path = Path(base_rom)
    base_meta = parse_rom_filename(base_path)
    if base_meta is None:
        print(f"ERROR: cannot parse base ROM filename: {base_rom}", file=sys.stderr)
        return 1

    root = Path(directory)
    if not root.is_dir():
        print(f"ERROR: directory not found: {directory}", file=sys.stderr)
        return 1

    tunes = []
    for ext in ("*.bin", "*.hex"):
        for p in root.rglob(ext):
            meta = parse_rom_filename(p)
            if meta and meta.is_tune and meta.base_stem == base_meta.base_stem:
                tunes.append(meta)

    tunes.sort(key=lambda r: (r.tune_num, r.ext))

    if not tunes:
        print(f"No tunes found for base ROM: {base_path.name}")
        return 0

    print(f"\nTunes derived from: {base_path.name}")
    print(f"{'File':<60} {'Tune#':<6} {'Ext':<5} {'Description'}")
    print("-" * 90)
    for t in tunes:
        print(f"{t.path.name:<60} {t.tune_num:<6} {t.ext:<5} {t.description}")
    return 0


def cmd_diff(rom_a: str, rom_b: str) -> int:
    """Print a byte-level diff between *rom_a* and *rom_b*."""
    path_a, path_b = Path(rom_a), Path(rom_b)
    for p in (path_a, path_b):
        if not p.is_file():
            print(f"ERROR: file not found: {p}", file=sys.stderr)
            return 1

    data_a = path_a.read_bytes()
    data_b = path_b.read_bytes()

    print(f"A: {path_a}  ({len(data_a):,} bytes)")
    print(f"B: {path_b}  ({len(data_b):,} bytes)")

    if data_a == data_b:
        print("Files are identical.")
        return 0

    diffs = []
    max_len = max(len(data_a), len(data_b))
    for i in range(max_len):
        byte_a = data_a[i] if i < len(data_a) else None
        byte_b = data_b[i] if i < len(data_b) else None
        if byte_a != byte_b:
            diffs.append((i, byte_a, byte_b))

    print(f"\n{len(diffs):,} byte(s) differ:\n")
    print(f"{'Offset (hex)':<14} {'A (hex)':<10} {'B (hex)'}")
    print("-" * 36)
    for offset, ba, bb in diffs[:200]:
        a_str = f"{ba:02X}" if ba is not None else "--"
        b_str = f"{bb:02X}" if bb is not None else "--"
        print(f"0x{offset:08X}     {a_str:<10} {b_str}")

    if len(diffs) > 200:
        print(f"  … and {len(diffs) - 200:,} more differences (truncated).")

    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage and compare Evo 8 ROM files."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List all ROM files in a directory")
    p_list.add_argument("directory", help="Root directory to search")

    p_tunes = sub.add_parser("tunes", help="Show tunes derived from a base ROM")
    p_tunes.add_argument("base_rom", help="Base ROM filename or path")
    p_tunes.add_argument(
        "--dir",
        default="cars/2003-evo-viii/roms/tunes",
        help="Directory to search for tune files",
    )

    p_diff = sub.add_parser("diff", help="Byte-level diff two ROM files")
    p_diff.add_argument("rom_a", help="First ROM file")
    p_diff.add_argument("rom_b", help="Second ROM file")

    args = parser.parse_args(argv)

    if args.command == "list":
        return cmd_list(args.directory)
    if args.command == "tunes":
        return cmd_tunes(args.base_rom, args.dir)
    if args.command == "diff":
        return cmd_diff(args.rom_a, args.rom_b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
