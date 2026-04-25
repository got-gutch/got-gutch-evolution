# MUT Finder Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│  START: Need to find MUT table in Evo 8 ROM                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │ Do you have a candidate       │
         │ offset already?               │
         └───┬─────────────────────┬─────┘
             │ YES                 │ NO
             │                     │
             ▼                     ▼
    ┌────────────────┐    ┌────────────────────────┐
    │ QUICK CHECK    │    │ RUN FULL SCAN          │
    │                │    │                        │
    │ Use:           │    │ Use:                   │
    │ quick_mut_     │    │ rom_mut_finder.py      │
    │ check.py       │    │                        │
    └────────┬───────┘    │ Options:               │
             │            │ • Multiple ROMs        │
             ▼            │ • --known-request      │
    ┌────────────────┐    │ • --top 12             │
    │ Valid?         │    │ • --verbose            │
    └───┬────────┬───┘    └──────────┬─────────────┘
        │ YES    │ NO                 │
        │        │                    ▼
        │        │           ┌─────────────────────┐
        │        │           │ Got candidates?     │
        │        │           └────┬────────────┬───┘
        │        │                │ YES        │ NO
        │        │                │            │
        │        │                ▼            ▼
        │        │       ┌─────────────┐  ┌─────────────┐
        │        └──────>│ Try         │  │ Adjust      │
        │                │ different   │  │ heuristics  │
        │                │ offset      │  │ or get      │
        │                └─────────────┘  │ more ROMs   │
        │                                 └─────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ DETAILED ANALYSIS                   │
│                                     │
│ Use: mut_table_analyzer.py          │
│                                     │
│ Shows:                              │
│ • Full table layout                 │
│ • Pointer highlighting              │
│ • Statistics                        │
└──────────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Looks correct?       │
        └────┬─────────────┬───┘
             │ YES         │ NO
             │             │
             ▼             ▼
    ┌────────────────┐   ┌─────────────┐
    │ COMPARE ROMS   │   │ Try next    │
    │                │   │ candidate   │
    │ Use:           │   └─────────────┘
    │ analyzer.py    │
    │ --compare      │
    │                │
    │ Find:          │
    │ • Differences  │
    │ • Stability    │
    └────────┬───────┘
             │
             ▼
    ┌────────────────────┐
    │ GENERATE XML       │
    │                    │
    │ Use:               │
    │ analyzer.py --xml  │
    │                    │
    │ Output:            │
    │ • EcuFlash snippet │
    └──────────┬─────────┘
               │
               ▼
    ┌──────────────────────┐
    │ TEST IN ECUFLASH     │
    │                      │
    │ 1. Add XML to ROM    │
    │    definition        │
    │ 2. Test with EvoScan │
    │ 3. Verify values     │
    └───────────┬──────────┘
                │
                ▼
        ┌───────────────┐
        │ Values make   │
        │ sense?        │
        └───┬───────┬───┘
            │ YES   │ NO
            │       │
            ▼       ▼
    ┌───────────┐  ┌──────────────┐
    │ SUCCESS!  │  │ Try sparse   │
    │ ✓         │  │ layout or    │
    │           │  │ different    │
    │ Document  │  │ offset       │
    │ in XML    │  └──────────────┘
    └───────────┘
```

## Current Status: YOU ARE HERE ⬇️

```
┌─────────────────────────────────────────────────┐
│ ✓ Scan complete                                 │
│ ✓ Top candidate identified: 0x00FE5E            │
│ ✓ Score: 156.75 (excellent)                     │
│ ✓ Pattern analysis: sparse even layout          │
│                                                 │
│ NEXT STEP:                                      │
│ → Run quick_mut_check.py to validate           │
│ → Run mut_table_analyzer.py for details        │
└─────────────────────────────────────────────────┘
```

## Quick Command Reference by Scenario

### Scenario 1: "I want to quickly check if 0xFE5E is valid"
```bash
python scripts/quick_mut_check.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    0xFE5E
```
⏱️ Time: 5 seconds  
📊 Output: Confidence rating

---

### Scenario 2: "I want to see the full table at 0xFE5E"
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E
```
⏱️ Time: 10 seconds  
📊 Output: Full 15×8 table with stats

---

### Scenario 3: "I want to see what changed between ROM versions"
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --compare
```
⏱️ Time: 20 seconds  
📊 Output: Difference report

---

### Scenario 4: "I need XML for EcuFlash"
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --xml
```
⏱️ Time: 10 seconds  
📊 Output: XML snippet

---

### Scenario 5: "I want to find new candidates"
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t030-disable_cat.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --top 12
```
⏱️ Time: 30 seconds  
📊 Output: Top 12 candidates

---

### Scenario 6: "I want detailed scan with full tables"
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --top 3 \
    --verbose
```
⏱️ Time: 20 seconds  
📊 Output: Top 3 with full table layouts

---

### Scenario 7: "I want to manually inspect raw bytes"
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --dump-hex 0xFE5E
```
⏱️ Time: 5 seconds  
📊 Output: Hex dump at offset

---

## Tool Selection Guide

| Goal | Tool | Speed | Detail |
|------|------|-------|--------|
| Validate offset | quick_mut_check.py | ⚡⚡⚡ | ★☆☆ |
| See table layout | mut_table_analyzer.py | ⚡⚡☆ | ★★★ |
| Compare ROMs | mut_table_analyzer.py --compare | ⚡☆☆ | ★★★ |
| Generate XML | mut_table_analyzer.py --xml | ⚡⚡☆ | ★★☆ |
| Find candidates | rom_mut_finder.py | ⚡☆☆ | ★★☆ |
| Deep analysis | rom_mut_finder.py --verbose | ⚡☆☆ | ★★★ |
| Raw inspection | rom_mut_finder.py --dump-hex | ⚡⚡⚡ | ★☆☆ |

⚡ = Fast  
★ = Detailed

---

## Troubleshooting Flow

```
Error or unexpected result?
         │
         ├─ "No output" ──────────> Check Python installation
         │                          Try: python --version
         │
         ├─ "File not found" ─────> Check path / current directory
         │                          Use absolute paths
         │
         ├─ "No candidates" ──────> Adjust MIN_POINTERS / MAX_POINTERS
         │                          Try different ROM files
         │
         ├─ "All low scores" ─────> ROM might be corrupted
         │                          Verify with hex editor
         │
         ├─ "Invalid offset" ─────> Try nearby offsets (±2 bytes)
         │                          Check if ROM is same version
         │
         └─ "Values don't match" ─> Try sparse_even layout
                                    Check if different ROM ID
```

---

**Remember**: The MUT table location is ROM-specific. Your offset (0xFE5E) is for **your specific Evo 8 ROM ID**. Different ROM IDs may have different offsets!

