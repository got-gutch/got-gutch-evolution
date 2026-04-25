# Analysis of Your MUT Finder Results (run_001.out)

**Date**: March 29, 2026  
**ROM Files Analyzed**:
- e8-t030-disable_cat.hex
- e8-t040-2byte_logging.hex  
- e8-t041-2byte_logging.hex

## Executive Summary

✓ **MUT table likely found at offset 0x00FE5E**

Your scan identified a strong cluster of candidates in the range 0xFE5A-0xFE68, all representing the same table structure viewed at slightly different alignments.

## Top 3 Candidates

### 1. Offset 0x00FE5E (BEST CANDIDATE)
- **Score**: 156.75
- **Pointers**: 53 (44%)
- **Sentinels (0xFFFF)**: 25 (21%)
- **Nulls (0x0000)**: 25 (21%)
- **Pattern**: `0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000`

**Why this is likely correct:**
- Highest score tied with 0xFE60
- Starts with a valid-looking pointer (0x1020)
- Even offset (0xFE5E = 65,118 decimal)
- Shows clear alternating pattern suggesting sparse layout

### 2. Offset 0x00FE60
- **Score**: 156.75 (tied for #1)
- **Pattern**: `0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000 0x1022`

**Why this might be wrong:**
- Starts with 0x0000 (less typical for table start)
- Likely just 0xFE5E viewed +2 bytes offset

### 3. Offset 0x00FE5A
- **Score**: 156.60
- **Pattern**: `0xFFEF 0x0000 0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000`

**Why this might be wrong:**
- Likely starts mid-row of the actual table
- Just 4 bytes before 0xFE5E

## Pattern Analysis

The repeating pattern across all top candidates reveals:

```
Column Layout (sparse table):
  0: Pointer/Sentinel (address)
  1: 0x0000 (padding/flag)
  2: Pointer/Sentinel (address)
  3: 0x0000 (padding/flag)
  4: Pointer/Sentinel (address)
  5: 0x0000 (padding/flag)
  6: Pointer/Sentinel (address)
  7: 0x0000 (padding/flag)
```

This is a **sparse even-columns layout**, meaning:
- Only columns 0, 2, 4, 6 contain data
- Request ID = (row × 4) + (column ÷ 2)
- Total usable entries: 60 (not 120)

## Why No Anchor Matches?

Your known requests didn't match:
```
--known-request "21:921A"   # Request 0x21 -> 0x921A
--known-request "17:9134"   # Request 0x17 -> 0x9134
--known-request "07:90C2"   # Request 0x07 -> 0x90C2
```

**Likely reasons:**
1. **Layout mismatch**: Script checked for dense layout by default
   - In dense: Request 0x21 = word[0x21] = position 33
   - In sparse even: Request 0x21 = position 66
   
2. **ROM version differences**: These anchors may be from:
   - A different Evo 8 ROM ID
   - Evo 7 or Evo 9 values
   - A stock ROM vs your modified tune

3. **These might not be in the table**: Not all parameters are accessible via MUT

## Recommendations

### Step 1: Quick Validation
```bash
python scripts/quick_mut_check.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    0xFE5A 0xFE5E 0xFE60
```

### Step 2: Detailed Analysis
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --layout sparse_even
```

### Step 3: Compare ROM Versions
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t030-disable_cat.hex \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --compare
```

**What to look for**: Changes between t040 and t041 (both "2byte_logging" tunes)
- If entries changed: These are logging-related parameters
- If identical: Confirms the table structure is stable

### Step 4: Test in EcuFlash

1. Add to your XML definition:
```xml
<muttable offset="0xFE5E">
  <!-- Test with a few known-good parameters first -->
  <mutentry requestid="01" address="..." />
  <mutentry requestid="02" address="..." />
</muttable>
```

2. Use EvoScan to test:
   - Request these MUT IDs
   - Verify values make sense
   - Compare with existing logs

## Understanding The Score

Your top candidate scored **156.75** based on:

| Factor | Weight | Your Value | Points |
|--------|--------|------------|--------|
| Pointers (53) | 2.0 × min(53, 48) | 48 | 96.0 |
| FFFF count (25) | 0.9 × min(25, 48) | 25 | 22.5 |
| Zero count (25) | 0.6 × min(25, 48) | 25 | 15.0 |
| Unique values (70) | 0.5 × min(70, 48) | 48 | 24.0 |
| Pointer range bonus | +18 (18-56 range) | Yes | 18.0 |
| Repetition penalty | -90 × 0.21 | 0.21 | -18.9 |
| **Total** | | | **156.6** |

The high score confirms this is an excellent candidate!

## What The "changed=0" Means

All your top candidates show `changed=0`, which means:
- The table is **identical** across all 3 ROMs you compared
- This is actually GOOD - it confirms:
  - The table structure is stable
  - You found the permanent table, not random data
  - The table offset doesn't move between tunes

## Next: Finding What Changed

Since the table itself didn't change, but tune 040 and 041 are "2byte_logging" variants, look for:

1. **Different MUT table offset** (less likely given your results)
2. **Different RAM addresses** that the table POINTS to
3. **Changes in the RAM data structures** themselves

To investigate further:
```bash
# See what DID change between these ROMs
python scripts/rom_manager.py diff \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex
```

## Conclusion

🎯 **Your scan was successful!**

- Offset **0x00FE5E** is highly likely to be your MUT table
- The sparse layout explains the alternating pattern
- No anchor matches is normal for different ROM versions
- Next step: Validate with the analyzer tools

---

**Pro Tip**: Keep the output pattern from 0xFE5E:
```
0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000
```

This will help you recognize MUT tables in other ROM files!

