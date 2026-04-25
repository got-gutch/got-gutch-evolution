#!/usr/bin/env python3
"""
rom_mut_finder.py — Find likely MUT table base addresses in Evo ROM files.

This tool scans one or more ROM files for candidate regions that look like an
EcuFlash MUT table definition: a compact block of 16-bit values that contains a
mix of RAM-like pointers, zeros, and sentinel values such as 0xFFFF.

It is intentionally heuristic. The goal is to narrow the search to a short list
of plausible table addresses that can then be tested in an EcuFlash XML table
definition.

Examples:
    python scripts/rom_mut_finder.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex
    python scripts/rom_mut_finder.py cars/2003-evo-viii/roms/tunes/e8-t030-disable_cat.hex \
        cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
        cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex
    python scripts/rom_mut_finder.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
        --known-request 21:921A --known-request 17:9134 --known-request 07:90C2
"""

from __future__ import annotations

import argparse
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TABLE_WIDTH = 8
TABLE_HEIGHT = 15
TABLE_WORDS = TABLE_WIDTH * TABLE_HEIGHT
DEFAULT_TOP = 12
MIN_POINTERS = 12
MAX_POINTERS = 80
MAX_SINGLE_VALUE_SHARE = 0.22


@dataclass
class Candidate:
    offset: int
    score: float
    pointer_like_count: int
    ffff_count: int
    zero_count: int
    changing_from_previous: int
    anchors_matched: int
    unique_word_count: int
    top_value_share: float
    anchor_layout: str
    first_words: list[int]
    all_words: list[int] | None = None  # Full table for verbose mode
    is_sparse: bool = False
    sparse_confidence: str = "UNKNOWN"


@dataclass
class KnownRequest:
    request_id: int
    expected_value: int


def load_words(path: Path) -> list[int]:
    data = path.read_bytes()
    if len(data) % 2 != 0:
        data = data[:-1]
    return [int.from_bytes(data[i:i + 2], "big") for i in range(0, len(data), 2)]


def parse_known_request(raw: str) -> KnownRequest:
    cleaned = raw.replace(" ", "")
    req_text, value_text = cleaned.split(":", 1)
    return KnownRequest(int(req_text, 16), int(value_text, 16))


def looks_like_pointer(value: int) -> bool:
    if value in {0x0000, 0xFFFF}:
        return False
    return 0x0700 <= value <= 0x9FFF


def analyze_distribution(values: list[int]) -> tuple[int, float]:
    counts = Counter(values)
    unique_word_count = len(counts)
    top_value_share = counts.most_common(1)[0][1] / len(values)
    return unique_word_count, top_value_share


def detect_sparse_pattern(table: list[int]) -> dict[str, any]:
    """Detect if table follows a sparse layout pattern."""
    # Check for alternating 0x0000 pattern in odd columns (1, 3, 5, 7)
    odd_col_zeros = 0
    total_odd_positions = 0

    for row in range(TABLE_HEIGHT):
        for col in [1, 3, 5, 7]:
            idx = row * TABLE_WIDTH + col
            if idx < len(table):
                total_odd_positions += 1
                if table[idx] == 0x0000:
                    odd_col_zeros += 1

    odd_zero_ratio = odd_col_zeros / total_odd_positions if total_odd_positions > 0 else 0

    # Check even columns for pointer-like values
    even_col_pointers = 0
    total_even_positions = 0

    for row in range(TABLE_HEIGHT):
        for col in [0, 2, 4, 6]:
            idx = row * TABLE_WIDTH + col
            if idx < len(table):
                total_even_positions += 1
                if looks_like_pointer(table[idx]) or table[idx] == 0xFFFF:
                    even_col_pointers += 1

    even_pointer_ratio = even_col_pointers / total_even_positions if total_even_positions > 0 else 0

    # Strong sparse pattern: >70% zeros in odd columns, >50% pointers in even columns
    is_sparse = odd_zero_ratio > 0.7 and even_pointer_ratio > 0.5

    return {
        "is_sparse": is_sparse,
        "odd_zero_ratio": odd_zero_ratio,
        "even_pointer_ratio": even_pointer_ratio,
        "confidence": "HIGH" if odd_zero_ratio > 0.8 else "MEDIUM" if odd_zero_ratio > 0.6 else "LOW"
    }


def estimate_table_boundary(table: list[int], is_sparse: bool) -> int:
    """Estimate which row the valid table data likely ends at."""
    # Look for rows that break the pattern (likely code/garbage)
    for row in range(TABLE_HEIGHT):
        row_start = row * TABLE_WIDTH
        row_end = row_start + TABLE_WIDTH
        row_words = table[row_start:row_end]

        if is_sparse:
            # Check if odd columns still have zeros
            odd_zeros = sum(1 for col in [1, 3, 5, 7] if row_words[col] == 0x0000)
            if odd_zeros < 2:  # Pattern breaks if < 50% zeros in odd columns
                return row
        else:
            # Check if values look like pointers/sentinels
            valid_values = sum(1 for v in row_words if looks_like_pointer(v) or v in {0x0000, 0xFFFF})
            if valid_values < 3:  # Less than ~40% valid values
                return row

    return TABLE_HEIGHT  # All rows look valid


def request_indices(request_id: int) -> dict[str, int]:
    return {
        "dense": request_id,
        "sparse_even_columns": (request_id // 2),
    }


def count_anchor_matches(current: list[int], known_requests: list[KnownRequest]) -> tuple[int, str]:
    layouts = {"dense": 0, "sparse_even_columns": 0}
    for anchor in known_requests:
        for layout, index in request_indices(anchor.request_id).items():
            if index < len(current) and current[index] == anchor.expected_value:
                layouts[layout] += 1

    best_layout = max(layouts, key=layouts.get)
    return layouts[best_layout], best_layout


def score_window(
    current: list[int],
    previous: list[int] | None,
    word_offset: int,
    known_requests: list[KnownRequest],
) -> Candidate:
    pointer_like = sum(1 for value in current if looks_like_pointer(value))
    ffff_count = current.count(0xFFFF)
    zero_count = current.count(0x0000)
    unique_word_count, top_value_share = analyze_distribution(current)

    # Detect sparse pattern
    sparse_info = detect_sparse_pattern(current)
    is_sparse = sparse_info["is_sparse"]

    changing_from_previous = 0
    if previous is not None:
        changing_from_previous = sum(1 for a, b in zip(previous, current) if a != b)

    anchors_matched, anchor_layout = count_anchor_matches(current, known_requests)

    score = 0.0
    score += anchors_matched * 40.0
    score += min(pointer_like, 48) * 2.0
    score += min(ffff_count, 48) * 0.9
    score += min(zero_count, 48) * 0.6
    score += min(unique_word_count, 48) * 0.5

    # Bonus for sparse pattern detection
    if is_sparse:
        score += 25.0  # Strong bonus for clear sparse pattern
        if sparse_info["odd_zero_ratio"] > 0.85:
            score += 10.0  # Extra bonus for very clean sparse pattern

    # Prefer sparse tables over dense all-pointer regions.
    if 18 <= pointer_like <= 56:
        score += 18.0
    else:
        score -= abs(pointer_like - 36) * 1.6

    # Strongly penalize windows dominated by a single repeated value like 0x8080.
    score -= top_value_share * 90.0

    # Multi-ROM searches are powerful when the same region changes in a small localized way.
    if previous is not None:
        if 0 < changing_from_previous <= 12:
            score += 18.0 - changing_from_previous
        elif changing_from_previous > 20:
            score -= 10.0

    first_words = current[: min(8, len(current))]
    return Candidate(
        offset=word_offset * 2,
        score=score,
        pointer_like_count=pointer_like,
        ffff_count=ffff_count,
        zero_count=zero_count,
        changing_from_previous=changing_from_previous,
        anchors_matched=anchors_matched,
        unique_word_count=unique_word_count,
        top_value_share=top_value_share,
        anchor_layout=anchor_layout,
        first_words=first_words,
        all_words=current.copy(),
        is_sparse=is_sparse,
        sparse_confidence=sparse_info["confidence"],
    )


def iter_windows(words: list[int]) -> Iterable[tuple[int, list[int]]]:
    for start in range(0, len(words) - TABLE_WORDS + 1):
        yield start, words[start : start + TABLE_WORDS]


def is_reasonable_candidate(candidate: Candidate) -> bool:
    if candidate.pointer_like_count < MIN_POINTERS or candidate.pointer_like_count > MAX_POINTERS:
        return False
    if candidate.top_value_share > MAX_SINGLE_VALUE_SHARE:
        return False
    if candidate.unique_word_count < 8:
        return False
    if candidate.ffff_count == 0 and candidate.zero_count == 0 and candidate.anchors_matched == 0:
        return False
    return True


def find_candidates(paths: list[Path], known_requests: list[KnownRequest]) -> list[Candidate]:
    word_sets = [load_words(path) for path in paths]
    base_words = word_sets[-1]
    previous_words = word_sets[-2] if len(word_sets) > 1 else None

    previous_map: dict[int, list[int]] = {}
    if previous_words is not None:
        for start, window in iter_windows(previous_words):
            previous_map[start] = window

    candidates: list[Candidate] = []
    for start, window in iter_windows(base_words):
        prev_window = previous_map.get(start)
        candidate = score_window(window, prev_window, start, known_requests)
        if is_reasonable_candidate(candidate):
            candidates.append(candidate)

    anchor_hits = [candidate for candidate in candidates if candidate.anchors_matched > 0]
    if anchor_hits:
        candidates = anchor_hits

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates


def format_words(words: list[int]) -> str:
    return " ".join(f"0x{value:04X}" for value in words)


def print_verbose_candidate_details(candidate: Candidate) -> None:
    """Print full table layout for a candidate."""
    if candidate.all_words is None:
        return

    # Estimate where valid table data ends
    table_boundary = estimate_table_boundary(candidate.all_words, candidate.is_sparse)

    print(f"    Full table layout ({TABLE_HEIGHT} rows × 8 columns):")

    if candidate.is_sparse:
        print(f"    Pattern: SPARSE (odd columns are padding) - Confidence: {candidate.sparse_confidence}")
        print(f"    Note: Only columns 0, 2, 4, 6 contain MUT data")
    else:
        print(f"    Pattern: Possibly DENSE (all columns may contain data)")

    if table_boundary < TABLE_HEIGHT:
        print(f"    ⚠️  Table data likely ends at row {table_boundary} (rows {table_boundary}-{TABLE_HEIGHT-1} may be code/garbage)")

    print()

    for row in range(TABLE_HEIGHT):
        row_start = row * TABLE_WIDTH
        row_end = row_start + TABLE_WIDTH
        row_words = candidate.all_words[row_start:row_end]

        # Mark rows beyond boundary
        row_marker = "  " if row < table_boundary else "⚠ "
        row_str = f"    {row_marker}Row {row:2d}: "

        for col, word in enumerate(row_words):
            # Format based on value type and position
            if candidate.is_sparse and col in [1, 3, 5, 7]:
                # Sparse padding columns
                if word == 0x0000:
                    row_str += " ----  "  # Expected padding
                else:
                    row_str += f"[{word:04X}]"  # Unexpected - highlight
            elif looks_like_pointer(word):
                row_str += f" {word:04X}* "  # Pointer
            elif word == 0xFFFF:
                row_str += " FFFF  "  # Sentinel
            elif word == 0x0000:
                row_str += " NULL  "  # Null
            else:
                # Check if this looks like garbage (likely not table data)
                if row >= table_boundary:
                    row_str += f"({word:04X})"  # Mark as suspicious
                else:
                    row_str += f" {word:04X}  "

        print(row_str)

    print()
    print(f"    Legend:")
    print(f"      * = RAM pointer (0x0700-0x9FFF)")
    if candidate.is_sparse:
        print(f"      - = Expected padding (sparse layout)")
        print(f"    [...] = Unexpected value in padding column")
    print(f"    (...) = Likely garbage/code (not table data)")
    print(f"      ⚠ = Row past estimated table boundary")
    print()


def dump_hex_at_offset(path: Path, offset: int, num_words: int = TABLE_WORDS) -> None:
    """Dump hex bytes at a specific offset for manual inspection."""
    data = path.read_bytes()
    byte_offset = offset
    byte_end = byte_offset + (num_words * 2)

    if byte_end > len(data):
        print(f"Warning: requested range extends beyond file size")
        byte_end = len(data)

    chunk = data[byte_offset:byte_end]
    words = [int.from_bytes(chunk[i:i+2], "big") for i in range(0, len(chunk), 2)]

    print(f"\nHex dump at offset 0x{offset:06X} in {path}:")
    print(f"Total: {len(words)} words ({len(chunk)} bytes)\n")

    for row in range(0, len(words), TABLE_WIDTH):
        row_words = words[row:row + TABLE_WIDTH]
        addr = offset + (row * 2)
        row_str = f"  0x{addr:06X}: "
        for word in row_words:
            row_str += f"0x{word:04X} "
        print(row_str)
    print()


def print_summary(paths: list[Path], candidates: list[Candidate], top: int, verbose: bool = False) -> None:
    print("ROM(s):")
    for path in paths:
        print(f"  - {path}")
    print()

    if not candidates:
        print("No MUT table candidates found with the current heuristics.")
        return

    scores = [candidate.score for candidate in candidates[:top]]
    print(f"Top {min(top, len(candidates))} candidate MUT table base addresses")
    print(f"(median score of shown results: {statistics.median(scores):.2f})\n")

    for index, candidate in enumerate(candidates[:top], start=1):
        sparse_indicator = " [SPARSE]" if candidate.is_sparse else ""
        print(
            f"{index:>2}. offset=0x{candidate.offset:06X}  score={candidate.score:6.2f}  "
            f"ptrs={candidate.pointer_like_count:>2}  ffff={candidate.ffff_count:>2}  "
            f"zero={candidate.zero_count:>2}  changed={candidate.changing_from_previous:>2}  "
            f"anchors={candidate.anchors_matched}  layout={candidate.anchor_layout:<19}  "
            f"unique={candidate.unique_word_count:>2}  top={candidate.top_value_share:.2f}{sparse_indicator}"
        )
        print(f"    first words: {format_words(candidate.first_words)}")
        if verbose:
            print_verbose_candidate_details(candidate)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find likely MUT table base addresses in one or more ROM files."
    )
    parser.add_argument(
        "roms",
        nargs="+",
        help="One or more ROM files. If multiple are given, the last file is scored against the previous one.",
    )
    parser.add_argument(
        "--known-request",
        action="append",
        default=[],
        metavar="REQ:VALUE",
        help="Known request/value anchor in hex, for example 21:921A or 07:90C2.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP,
        help=f"Number of candidates to print (default: {DEFAULT_TOP}).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print full table layout for each candidate.",
    )
    parser.add_argument(
        "--dump-hex",
        metavar="OFFSET",
        help="Dump raw hex bytes at a specific offset (e.g., 0xFE5E) for manual inspection.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    roms = [Path(item) for item in args.roms]
    missing = [str(path) for path in roms if not path.is_file()]
    if missing:
        for path in missing:
            print(f"ERROR: file not found: {path}")
        return 1

    # Handle --dump-hex option separately
    if args.dump_hex:
        offset_str = args.dump_hex.replace("0x", "").replace("0X", "")
        offset = int(offset_str, 16)
        for rom in roms:
            dump_hex_at_offset(rom, offset)
        return 0

    known_requests = [parse_known_request(item) for item in args.known_request]
    candidates = find_candidates(roms, known_requests)
    print_summary(roms, candidates, args.top, args.verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

