#!/usr/bin/env python3
"""
boost_tuner.py \u2014 Analyze EvoScan logs to suggest WGDC (Wastegate Duty Cycle) updates.

This script helps tune a 3-port boost solenoid (Port 1: Vent, Port 2: WG, Port 3: Turbo).
- 0% DC = Spring Pressure (~11-12 psi)
- 100% DC = Max Boost

Target: ~21 psi.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

class BoostAnalyzer:
    def __init__(self, log_path: str, target_boost: float = 21.0, spring_pressure: float = 12.0, hack01: bool = False):
        self.path = Path(log_path)
        self.target_boost = target_boost
        self.spring_pressure = spring_pressure
        self.hack01 = hack01
        self.df = pd.DataFrame()
        self._load()

    def _load(self):
        """Load CSV and drop empty columns, similar to evoscan_parser."""
        self.df = pd.read_csv(self.path, encoding="utf-8-sig")
        self.df.replace(r"^\s*$", pd.NA, regex=True, inplace=True)
        self.df.dropna(axis=1, how="all", inplace=True)

        # Map Boost Column (Prefer ZTXBoost, then MAP)
        if "ZTXBoost" in self.df.columns:
            self.df["Boost"] = pd.to_numeric(self.df["ZTXBoost"], errors="coerce")
        elif "MAP" in self.df.columns:
            self.df["Boost"] = pd.to_numeric(self.df["MAP"], errors="coerce")
            if self.hack01:
                # Convert PSIA to PSIG by subtracting atmospheric pressure
                self.df["Boost"] = self.df["Boost"] - 14.7
        else:
            print(f"[!] Warning: No boost column (ZTXBoost or MAP) found in {self.path.name}")
            self.df["Boost"] = 0.0

        if "TPS" in self.df.columns:
            self.df["TPS"] = pd.to_numeric(self.df["TPS"], errors="coerce")
        else:
            print(f"[!] Warning: No TPS column found in {self.path.name}")

        if "WGDC" in self.df.columns:
            self.df["WGDC"] = pd.to_numeric(self.df["WGDC"], errors="coerce")

    def find_wot_pulls(self, tps_thresh=90.0):
        if "TPS" not in self.df.columns or "Boost" not in self.df.columns:
            return []

        is_wot = self.df["TPS"] >= tps_thresh
        if not is_wot.any():
            return []

        group_ids = (is_wot != is_wot.shift()).cumsum()

        pulls = []
        for _, group in self.df[is_wot].groupby(group_ids):
            if len(group) >= 5: # Min rows for a valid pull
                pulls.append(group)
        return pulls

    def analyze(self):
        pulls = self.find_wot_pulls()
        if not pulls:
            print(f"No WOT pulls found in {self.path.name}")
            return

        print(f"\nAnalysis for {self.path.name}:")

        for i, pull in enumerate(pulls, 1):
            max_boost = pull["Boost"].max()
            avg_wgdc = pull["WGDC"].mean() if "WGDC" in pull.columns else 0.0

            print(f"\nPull {i}:")
            print(f"  Max Boost: {max_boost:.2f} psi")
            print(f"  Avg WGDC:  {avg_wgdc:.1f}%")

            if max_boost < self.spring_pressure - 2:
                print("  [!] WARNING: Boost is significantly lower than spring pressure. Check for leaks.")
            elif abs(max_boost - self.spring_pressure) < 1.5 and avg_wgdc < 1.0:
                print(f"  [+] Spring Pressure Confirmed (~{max_boost:.1f} psi). Plumbing looks correct.")
                print("  [>] Suggestion: Increase WGDC by 5-10% in the ROM to begin walking up to target.")
            elif max_boost < self.target_boost:
                shortfall = self.target_boost - max_boost
                suggested_increase = min(10, max(2, int(shortfall * 1.5)))
                print(f"  [-] Below Target ({self.target_boost} psi).")
                print(f"  [>] Suggestion: Increase WGDC by {suggested_increase}% in your next tune.")
            elif max_boost > self.target_boost + 1:
                print(f"  [!] OVERBOOST: {max_boost:.2f} psi exceeds target of {self.target_boost} psi.")
                print("  [>] Suggestion: Decrease WGDC immediately by 10% or more.")
            else:
                print(f"  [*] Target achieved! Boost is stable at {max_boost:.2f} psi.")

def main():
    parser = argparse.ArgumentParser(description="Suggest WGDC updates based on EvoScan logs.")
    parser.add_argument("logs", nargs="+", help="Path to EvoScan CSV log file(s)")
    parser.add_argument("--target", type=float, default=21.0, help="Target boost in psi (default: 21.0)")
    parser.add_argument("--spring", type=float, default=12.0, help="Estimated spring pressure in psi (default: 12.0)")
    parser.add_argument("--hack01", action="store_true", help="Subtract 14.7 from MAP (PSIA -> PSIG conversion)")
    args = parser.parse_args()

    for log_path in args.logs:
        try:
            analyzer = BoostAnalyzer(log_path, target_boost=args.target, spring_pressure=args.spring, hack01=args.hack01)
            analyzer.analyze()
        except Exception as e:
            print(f"Error processing {log_path}: {e}")

if __name__ == "__main__":
    main()
