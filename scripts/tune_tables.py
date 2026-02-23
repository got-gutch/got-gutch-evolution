#!/usr/bin/env python3
"""
tune_tables.py — Extract and display octane and ignition tables from Evo 8 ROM files.

The Mitsubishi 4G63 ECU stores fuel/ignition tables as a grid of byte values
at fixed offsets within the ROM image.  Provide offsets via command-line
arguments or a JSON config file.

Commands:
  show    — print a table (octane or ignition) from a ROM file as an ASCII grid
  compare — diff a table between two ROM files side by side
  export  — write a table to CSV for further analysis

Usage:
  python scripts/tune_tables.py show <rom.bin> --table octane
  python scripts/tune_tables.py show <rom.bin> --table ignition
  python scripts/tune_tables.py show <rom.bin> --table octane --config tables.json
  python scripts/tune_tables.py compare <rom_a.bin> <rom_b.bin> --table ignition
  python scripts/tune_tables.py export <rom.bin> --table octane --out octane.csv

Table config JSON format (tables.json):
  {
    "octane": {
      "offset": 12288,
      "rows": 16,
      "cols": 16,
      "row_label": "RPM",
      "col_label": "Load"
    },
    "ignition": {
      "offset": 16384,
      "rows": 16,
      "cols": 16,
      "row_label": "RPM",
      "col_label": "Load"
    }
  }
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Default table layouts (offsets are illustrative — update from your ROMs)
# ---------------------------------------------------------------------------

DEFAULT_TABLES: dict = {
    "octane": {
        "offset": 0x3000,   # update with actual ROM offset
        "rows": 16,
        "cols": 16,
        "row_label": "RPM",
        "col_label": "Load",
    },
    "ignition": {
        "offset": 0x4000,   # update with actual ROM offset
        "rows": 16,
        "cols": 16,
        "row_label": "RPM",
        "col_label": "Load",
    },
}


# ---------------------------------------------------------------------------
# Table reading
# ---------------------------------------------------------------------------

def read_table(rom_data: bytes, config: dict) -> list[list[int]]:
    """Read a 2-D table from *rom_data* using the given config dict."""
    offset = config["offset"]
    rows = config["rows"]
    cols = config["cols"]
    size = rows * cols

    if offset + size > len(rom_data):
        raise ValueError(
            f"Table extends beyond ROM end "
            f"(offset=0x{offset:X}, size={size}, rom_size={len(rom_data)})"
        )

    flat = rom_data[offset: offset + size]
    return [list(flat[r * cols: (r + 1) * cols]) for r in range(rows)]


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_table(table: list[list[int]], config: dict, title: str = "") -> None:
    cols = len(table[0]) if table else 0
    if title:
        print(f"\n{title}")

    header = f"{'':>4} | " + " ".join(f"{c:>4}" for c in range(cols))
    print(header)
    print("-" * len(header))
    for r_idx, row in enumerate(table):
        cells = " ".join(f"{v:>4}" for v in row)
        print(f"{r_idx:>4} | {cells}")


def _print_diff(
    table_a: list[list[int]],
    table_b: list[list[int]],
    label_a: str,
    label_b: str,
    config: dict,
) -> int:
    """Print side-by-side diff, return count of changed cells."""
    rows = len(table_a)
    cols = len(table_a[0]) if table_a else 0
    changed = 0

    print(f"\n{'Col':>4}", end="")
    for c in range(cols):
        print(f"  {c:>9}", end="")
    print()
    print("-" * (4 + cols * 11))

    for r in range(rows):
        print(f"{r:>4}", end="")
        for c in range(cols):
            va, vb = table_a[r][c], table_b[r][c]
            if va != vb:
                changed += 1
                print(f"  {va:>4}→{vb:<4}", end="")
            else:
                print(f"  {'':>9}", end="")
        print()

    print(f"\n{changed} cell(s) differ between {label_a} and {label_b}.")
    return changed


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _load_config(config_path: str | None, table_name: str) -> dict:
    if config_path:
        with open(config_path) as fh:
            all_configs = json.load(fh)
        if table_name not in all_configs:
            raise KeyError(
                f"Table '{table_name}' not found in config. "
                f"Available: {list(all_configs.keys())}"
            )
        return all_configs[table_name]
    if table_name not in DEFAULT_TABLES:
        raise KeyError(
            f"Unknown table '{table_name}'. "
            f"Available defaults: {list(DEFAULT_TABLES.keys())}"
        )
    return DEFAULT_TABLES[table_name]


def cmd_show(rom: str, table_name: str, config_path: str | None) -> int:
    data = Path(rom).read_bytes()
    config = _load_config(config_path, table_name)
    table = read_table(data, config)
    _print_table(table, config, title=f"{table_name.title()} Table — {Path(rom).name}")
    return 0


def cmd_compare(rom_a: str, rom_b: str, table_name: str, config_path: str | None) -> int:
    data_a = Path(rom_a).read_bytes()
    data_b = Path(rom_b).read_bytes()
    config = _load_config(config_path, table_name)
    table_a = read_table(data_a, config)
    table_b = read_table(data_b, config)
    _print_diff(
        table_a,
        table_b,
        Path(rom_a).name,
        Path(rom_b).name,
        config,
    )
    return 0


def cmd_export(rom: str, table_name: str, config_path: str | None, out: str) -> int:
    data = Path(rom).read_bytes()
    config = _load_config(config_path, table_name)
    table = read_table(data, config)
    with open(out, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([f"{config['row_label']} \\ {config['col_label']}"] + list(range(len(table[0]))))
        for r_idx, row in enumerate(table):
            writer.writerow([r_idx] + row)
    print(f"Exported {table_name} table ({len(table)}×{len(table[0])}) → {out}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract and compare octane/ignition tables from Evo 8 ROM files."
    )
    parser.add_argument(
        "--config",
        metavar="tables.json",
        help="Optional JSON file with table offset configs",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_show = sub.add_parser("show", help="Print a table from a ROM file")
    p_show.add_argument("rom", help="ROM .bin file")
    p_show.add_argument("--table", default="octane", help="Table name (octane|ignition)")

    p_cmp = sub.add_parser("compare", help="Diff a table between two ROM files")
    p_cmp.add_argument("rom_a")
    p_cmp.add_argument("rom_b")
    p_cmp.add_argument("--table", default="ignition", help="Table name (octane|ignition)")

    p_exp = sub.add_parser("export", help="Export a table to CSV")
    p_exp.add_argument("rom", help="ROM .bin file")
    p_exp.add_argument("--table", default="octane", help="Table name (octane|ignition)")
    p_exp.add_argument("--out", required=True, help="Output CSV file path")

    args = parser.parse_args(argv)

    try:
        if args.command == "show":
            return cmd_show(args.rom, args.table, args.config)
        if args.command == "compare":
            return cmd_compare(args.rom_a, args.rom_b, args.table, args.config)
        if args.command == "export":
            return cmd_export(args.rom, args.table, args.config, args.out)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
