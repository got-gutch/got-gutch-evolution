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
import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class EvoScanLog:
    """Represents a single EvoScan 2.9 data log file using pandas."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.df = pd.DataFrame()
        self._load()

    def _load(self) -> None:
        """Load CSV and drop columns that are entirely empty or contain no data."""
        # EvoScan often uses 'utf-8-sig' for the BOM
        self.df = pd.read_csv(self.path, encoding="utf-8-sig")

        # Remove columns that are entirely NaN or empty strings
        # First convert empty strings/whitespace to NaN for consistent dropping
        self.df.replace(r'^\s*$', pd.NA, regex=True, inplace=True)
        self.df.dropna(axis=1, how='all', inplace=True)

    def channel_names(self) -> list[str]:
        """Return the list of logged channel names."""
        return self.df.columns.tolist()

    def summary(self) -> dict:
        """
        Return a summary dict: channel → stats.
        Uses pandas describe() logic but mimics the previous output format.
        """
        return self._get_summary_for_df(self.df)

    def _get_summary_for_df(self, df: pd.DataFrame) -> dict:
        """Internal helper to generate summary stats for a given dataframe."""
        out = {}
        for ch in df.columns:
            series = df[ch]
            # Try to force numeric for stats if possible
            numeric_series = pd.to_numeric(series, errors='coerce').dropna()

            if not numeric_series.empty:
                out[ch] = {
                    "count": len(numeric_series),
                    "min": float(numeric_series.min()),
                    "max": float(numeric_series.max()),
                    "mean": float(numeric_series.mean()),
                }
            else:
                # Non-numeric or empty after coercion
                values = series.dropna()
                out[ch] = {
                    "count": len(series),
                    "sample": str(values.iloc[0]) if not values.empty else "",
                }
        return out

    def get_wot_segments(self, tps_threshold: float = 95.0, min_rows: int = 5) -> list[pd.DataFrame]:
        """
        Identify segments of Wide Open Throttle (WOT) activity.
        Returns a list of DataFrames, each representing a contiguous WOT pull.
        """
        if "TPS" not in self.df.columns:
            return []

        # Convert TPS to numeric for comparison
        tps = pd.to_numeric(self.df["TPS"], errors='coerce').fillna(0)
        is_wot = tps >= tps_threshold

        # Identify contiguous groups of True values
        # (is_wot != is_wot.shift()).cumsum() creates a unique ID for each block of identical values
        group_ids = (is_wot != is_wot.shift()).cumsum()

        segments = []
        for _, group in self.df[is_wot].groupby(group_ids):
            if len(group) >= min_rows:
                segments.append(group)

        return segments

    def export_csv(self, dest: str) -> None:
        """Write the cleaned dataframe to *dest* as a CSV."""
        self.df.to_csv(dest, index=False, encoding="utf-8")
        print(f"Exported {len(self.df)} rows → {dest}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

CRITICAL_WOT_CHANNELS = ["RPM", "TPS", "Speed", "TimingAdv", "KnockSum", "MAP", "AirFlow", "ECULoad"]


def _print_summary(log: EvoScanLog, show_wot: bool = False) -> None:
    print(f"\n{'=' * 60}")
    print(f"File   : {log.path}")
    print(f"Rows   : {len(log.df)}")
    print(f"{'=' * 60}")

    if show_wot:
        wot_segments = log.get_wot_segments()
        if wot_segments:
            print(f"FOUND {len(wot_segments)} WOT SEGMENT(S)")
            for i, seg in enumerate(wot_segments, 1):
                print(f"\n--- WOT Segment {i} ({len(seg)} rows) ---")
                stats = log._get_summary_for_df(seg)
                # Use global list for critical channels
                for ch in CRITICAL_WOT_CHANNELS:
                    if ch in stats and "mean" in stats[ch]:
                        s = stats[ch]
                        print(f"  {ch:<15} min={s['min']:>8.1f} max={s['max']:>8.1f} mean={s['mean']:>8.1f}")
        else:
            print("NO WOT SEGMENTS DETECTED (TPS >= 95%)")
        print(f"\n{'=' * 60}")
    else:
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


def _expand_paths(paths: list[str]) -> list[Path]:
    """
    Expand input paths: if a path is a directory, find all .csv files in it.
    Otherwise, treat it as a file path.
    """
    expanded = []
    for path_str in paths:
        path = Path(path_str)
        if path.is_dir():
            # Find all CSV files in the directory (non-recursive)
            csv_files = sorted(path.glob("*.csv"))
            if not csv_files:
                print(f"WARNING: no .csv files found in {path}", file=sys.stderr)
            expanded.extend(csv_files)
        else:
            expanded.append(path)
    return expanded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse and summarise EvoScan 2.9 data log CSV files."
    )
    parser.add_argument("logs", nargs="+", help="Path(s) to EvoScan CSV log file(s) or directory")
    parser.add_argument(
        "--export",
        metavar="DEST",
        help="Export cleaned CSV to DEST (only used with a single input file)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=None,
        help="Print a full channel summary",
    )
    parser.add_argument(
        "--wot",
        action="store_true",
        help="Filter for Wide Open Throttle segments and show critical stats",
    )
    args = parser.parse_args(argv)

    # Default to summary if nothing else specified
    if args.summary is None and not args.wot and not args.export:
        args.summary = True

    # Expand directories to CSV files
    log_paths = _expand_paths(args.logs)

    if not log_paths:
        print("ERROR: no input files found", file=sys.stderr)
        return 1

    for log_path in log_paths:
        try:
            log = EvoScanLog(str(log_path))
        except FileNotFoundError:
            print(f"ERROR: file not found: {log_path}", file=sys.stderr)
            return 1
        except PermissionError:
            print(f"ERROR: permission denied: {log_path}", file=sys.stderr)
            return 1

        if args.summary:
            _print_summary(log)

        if args.wot:
            _print_summary(log, show_wot=True)

        if args.export:
            if len(log_paths) > 1:
                print(
                    "WARNING: --export is ignored when multiple input files are given.",
                    file=sys.stderr,
                )
            else:
                log.export_csv(args.export)

    return 0


if __name__ == "__main__":
    sys.exit(main())
