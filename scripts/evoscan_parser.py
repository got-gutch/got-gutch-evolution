#!/usr/bin/env python3
"""
evoscan_parser.py — Parse EvoScan 2.9 data log CSV files.

EvoScan 2.9 produces comma-separated log files with a header row followed by
timestamped sensor readings.  This script loads one or more log files, prints
a summary of every channel found, and can export a cleaned CSV.

Usage:
    python scripts/evoscan_parser.py <logfile.csv> [logfile2.csv ...]
    python scripts/evoscan_parser.py <logfile.csv> --export cleaned.csv
    python scripts/evoscan_parser.py <logfile.csv> --summary
"""

import argparse
import csv
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class EvoScanLog:
    """Represents a single EvoScan 2.9 data log file."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.headers: list[str] = []
        self.rows: list[dict] = []
        self._load()

    def _load(self) -> None:
        with self.path.open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            self.headers = reader.fieldnames or []
            self.rows = list(reader)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def channel_names(self) -> list[str]:
        """Return the list of logged channel names (header columns)."""
        return list(self.headers)

    def channel_values(self, channel: str) -> list[str]:
        """Return all recorded values for a given channel."""
        return [row[channel] for row in self.rows if channel in row]

    def numeric_values(self, channel: str) -> list[float]:
        """Return numeric values for a channel, skipping non-numeric entries."""
        result = []
        for raw in self.channel_values(channel):
            try:
                result.append(float(raw))
            except (ValueError, TypeError):
                pass
        return result

    def summary(self) -> dict:
        """
        Return a summary dict: channel → {count, min, max, mean} for numeric
        channels, or {count, sample} for non-numeric ones.
        """
        out = {}
        for ch in self.headers:
            nums = self.numeric_values(ch)
            if nums:
                out[ch] = {
                    "count": len(nums),
                    "min": min(nums),
                    "max": max(nums),
                    "mean": sum(nums) / len(nums),
                }
            else:
                values = self.channel_values(ch)
                out[ch] = {
                    "count": len(values),
                    "sample": values[0] if values else "",
                }
        return out

    def export_csv(self, dest: str) -> None:
        """Write the loaded log rows to *dest* as a clean CSV."""
        with open(dest, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.rows)
        print(f"Exported {len(self.rows)} rows → {dest}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_summary(log: EvoScanLog) -> None:
    print(f"\n{'=' * 60}")
    print(f"File   : {log.path}")
    print(f"Rows   : {len(log.rows)}")
    print(f"{'=' * 60}")
    summary = log.summary()
    for ch, stats in summary.items():
        if "mean" in stats:
            print(
                f"  {ch:<35} count={stats['count']:>6}  "
                f"min={stats['min']:>10.3f}  "
                f"max={stats['max']:>10.3f}  "
                f"mean={stats['mean']:>10.3f}"
            )
        else:
            print(
                f"  {ch:<35} count={stats['count']:>6}  "
                f"sample={stats['sample']}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse and summarise EvoScan 2.9 data log CSV files."
    )
    parser.add_argument("logs", nargs="+", help="Path(s) to EvoScan CSV log file(s)")
    parser.add_argument(
        "--export",
        metavar="DEST",
        help="Export cleaned CSV to DEST (only used with a single input file)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=True,
        help="Print a channel summary (default: on)",
    )
    args = parser.parse_args(argv)

    for log_path in args.logs:
        try:
            log = EvoScanLog(log_path)
        except FileNotFoundError:
            print(f"ERROR: file not found: {log_path}", file=sys.stderr)
            return 1

        if args.summary:
            _print_summary(log)

        if args.export:
            if len(args.logs) > 1:
                print(
                    "WARNING: --export is ignored when multiple input files are given.",
                    file=sys.stderr,
                )
            else:
                log.export_csv(args.export)

    return 0


if __name__ == "__main__":
    sys.exit(main())
