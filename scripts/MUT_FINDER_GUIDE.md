# MUT Table Finder Guide

## Overview

This guide explains how to use the MUT table finder tools to locate and verify MUT (Monitor Unit Table) addresses in Mitsubishi Evolution ROM files.

## Tools

### 1. `rom_mut_finder.py` - Find MUT Table Candidates

Scans ROM files to find likely MUT table locations based on heuristics.

#### Basic Usage

```bash
python scripts/rom_mut_finder.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex
```

#### Advanced Usage

**Compare multiple ROM versions** (recommended):
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t030-disable_cat.hex \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --top 12
```

**With known request anchors**:
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --known-request "21:921A" \
    --known-request "17:9134" \
    --known-request "07:90C2" \
    --top 12
```

**Verbose mode** (shows full table layout):
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --top 3 \
    --verbose
```

**Dump hex at specific offset**:
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --dump-hex 0xFE5E
```

#### New Features Added

1. **`--verbose` / `-v`**: Shows the full 15×8 table layout for each candidate
2. **`--dump-hex OFFSET`**: Dumps raw hex bytes at a specific offset for manual inspection

### 2. `mut_table_analyzer.py` - Analyze Specific Candidates

Once you have candidate offsets from `rom_mut_finder.py`, use this tool to analyze them in detail.

#### Basic Analysis

```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E
```

#### Compare Across ROM Versions

```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --compare
```

#### Generate EcuFlash XML

```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --xml
```

## Understanding Your Results

### From run_001.out

Your top candidates are:

1. **0x00FE5E** - score=156.75, 53 pointers, 25 FFFF, 25 zeros
2. **0x00FE60** - score=156.75, 53 pointers, 25 FFFF, 25 zeros  
3. **0x00FE5A** - score=156.60, 52 pointers, 25 FFFF, 26 zeros

#### Key Observations

**Clustering**: The top 8 candidates are all within 14 bytes (0xFE5A - 0xFE68). This is actually the **same table viewed at slightly different offsets**. The MUT table is likely at one of these addresses, and the others are just off by 2-8 bytes.

**Pattern Analysis**: Looking at the "first words":
```
offset=0x00FE5E: 0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000
offset=0x00FE60: 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000 0x1022
```

This shows an alternating pattern: `[pointer] [0x0000] [sentinel] [0x0000] ...`

This suggests a **sparse table layout** where:
- Columns 0, 2, 4, 6 contain memory addresses
- Columns 1, 3, 5, 7 are padding (0x0000) or flags

### No Anchor Matches

Your known requests didn't match:
- `21:921A` (Request 0x21 should point to 0x921A)
- `17:9134` (Request 0x17 should point to 0x9134)
- `07:90C2` (Request 0x07 should point to 0x90C2)

**Possible reasons:**
1. The MUT table uses sparse layout (request_id = position / 2)
2. The known values are from a different ROM version
3. The table offset is slightly different

## Next Steps

### 1. Verify Top Candidates

Use the analyzer to examine the top 3 candidates:

```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E

python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5A

python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE60
```

### 2. Compare Across ROM Versions

See which entries change between ROM versions (these are likely logging-related):

```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t030-disable_cat.hex \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --compare
```

### 3. Test in EcuFlash

Generate XML snippets for testing:

```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --xml > test_muttable.xml
```

Then add this to your EcuFlash XML definition and test with EvoScan.

### 4. Find the Exact Offset

The true MUT table likely starts at an even offset that's divisible by 2. Given your candidates:

**Most likely**: `0xFE5E` or `0xFE60`
- Both have the highest scores
- Both show clear pointer patterns
- `0xFE5E` (65,118 decimal) seems like a more "round" address

**To test**: Try these in EcuFlash's ROM editor:
1. Look at offset 0xFE5E in the hex editor
2. Check if it's the start of a structured table
3. Verify the pattern continues for 240 bytes (120 words)

## MUT Table Structure

A typical Evo 8 MUT table:
- **Size**: 15 rows × 8 columns = 120 words (240 bytes)
- **Layout**: Can be dense or sparse
  - **Dense**: Each word = one request, request_id = index (0-119)
  - **Sparse**: Only even columns used, request_id = row × 4 + (col/2)
- **Values**:
  - RAM pointers: 0x0700 - 0x9FFF (actual data location)
  - 0x0000: NULL / not implemented
  - 0xFFFF: Sentinel / end marker

## Common Request IDs (Evo 8)

Based on typical Evo 8/9 MUT tables:

| Request ID | Parameter | Typical Address Range |
|------------|-----------|----------------------|
| 0x01-0x04  | Basic ECU info | 0x9xxx |
| 0x05-0x0F  | Engine sensors | 0x9xxx |
| 0x10-0x1F  | Boost/Load | 0x9xxx |
| 0x20-0x2F  | Fuel/Timing | 0x9xxx |
| 0x30-0x3F  | Logging params | 0x9xxx |

## Troubleshooting

### "No candidates found"

Try:
- Increasing `MAX_POINTERS` in the script (line 38)
- Decreasing `MIN_POINTERS` (line 37)
- Checking if ROM file is valid (should be 256KB or 512KB)

### "Anchors don't match"

- Try sparse_even layout in the analyzer
- Your ROM may be a different version than anchor sources
- The anchors may be from Evo 7/9 (slightly different)

### "Too many candidates with similar scores"

- Use multiple ROM files for comparison
- Look for the candidate with the most "round" offset
- Check patterns manually in a hex editor

## Reference: Known Evo 8 MUT Offsets

Based on community knowledge:
- Some Evo 8 ROMs: around 0xFE00 - 0xFF00 range ✓ (your results!)
- Evo 7: often around 0xFD00 - 0xFE00
- Evo 9: varies by ROM ID

Your top candidate **0xFE5E is very promising** given:
- It's in the expected range
- Shows correct structural patterns
- Has high pointer density
- Balanced FFFF/zero counts

## Support Files

- `cars/2003-evo-viii/configs/evo-scan-data-settings/*.xml` - Reference EcuFlash configs
- `cars/2003-evo-viii/logs/` - EvoScan logs for validation

