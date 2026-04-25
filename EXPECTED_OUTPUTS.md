# Expected Tool Outputs - Examples

This document shows what the output looks like for each tool so you know what to expect.

## 1. quick_mut_check.py

### Example Run
```bash
$ python scripts/quick_mut_check.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex 0xFE5E 0xFE60 0xFE5A
```

### Expected Output
```
ROM: e8-t041-2byte_logging.hex
Checking 3 offset(s)...

Results:
--------------------------------------------------------------------------------
Offset 0x00FE5E: HIGH ✓✓✓
  Pointers:  53  |  Zeros:  25  |  FFFs:  25  |  Unique:  70

Offset 0x00FE60: HIGH ✓✓✓
  Pointers:  53  |  Zeros:  25  |  FFFs:  25  |  Unique:  70

Offset 0x00FE5A: HIGH ✓✓✓
  Pointers:  52  |  Zeros:  26  |  FFFs:  25  |  Unique:  70

--------------------------------------------------------------------------------
✓ RECOMMENDATION: Try offset 0x00FE5E first (HIGH ✓✓✓)
  Alternative offsets: 0x00FE60, 0x00FE5A
```

**Interpretation:**
- All three offsets look valid (HIGH confidence)
- Start with 0xFE5E (recommended)
- They're likely the same table at different alignments

---

## 2. mut_table_analyzer.py (basic)

### Example Run
```bash
$ python scripts/mut_table_analyzer.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex --offset 0xFE5E
```

### Expected Output
```
################################################################################
# ROM: e8-t041-2byte_logging.hex
################################################################################

================================================================================
MUT Table at offset 0x00FE5E
================================================================================

Full table layout (15 rows × 8 columns):

      Col:   0       1       2       3       4       5       6       7
      --------------------------------------------------------------------
  Row  0 (0x00FE5E):  1020*   NULL   FFDF*   NULL   1021*   NULL   FFBF*   NULL  
  Row  1 (0x00FE6E):  1022*   NULL   FF7F*   NULL   1023*   NULL   FF3F*   NULL  
  Row  2 (0x00FE7E):  1024*   NULL   FEFF*   NULL   1025*   NULL   FEBF*   NULL  
  Row  3 (0x00FE8E):  1026*   NULL   FE7F*   NULL   1027*   NULL   FE3F*   NULL  
  Row  4 (0x00FE9E):  1028*   NULL   FDFF*   NULL   1029*   NULL   FDBF*   NULL  
  Row  5 (0x00FEAE):  102A*   NULL   FD7F*   NULL   102B*   NULL   FD3F*   NULL  
  Row  6 (0x00FEBE):  102C*   NULL   FCFF*   NULL   102D*   NULL   FCBF*   NULL  
  Row  7 (0x00FECE):  102E*   NULL   FC7F*   NULL   102F*   NULL   FC3F*   NULL  
  Row  8 (0x00FEDE):  1030*   NULL   FBFF*   NULL   1031*   NULL   FBBF*   NULL  
  Row  9 (0x00FEEE):  1032*   NULL   FB7F*   NULL   1033*   NULL   FB3F*   NULL  
  Row 10 (0x00FEFE):  1034*   NULL   FAFF*   NULL   1035*   NULL   FABF*   NULL  
  Row 11 (0x00FF0E):  1036*   NULL   FA7F*   NULL   1037*   NULL   FA3F*   NULL  
  Row 12 (0x00FF1E):  1038*   NULL   F9FF*   NULL   1039*   NULL   F9BF*   NULL  
  Row 13 (0x00FF2E):  103A*   NULL   F97F*   NULL   103B*   NULL   F93F*   NULL  
  Row 14 (0x00FF3E):  103C*   NULL   F8FF*   NULL   FFFF    NULL   FFFF    NULL  

  * = looks like a RAM pointer (0x0700-0x9FFF)

Table Statistics:
  Total entries:     120
  RAM pointers:      53 (44.2%)
  NULL (0x0000):     25
  Sentinel (0xFFFF): 25
  Other values:      17
  Unique values:     70
```

**Interpretation:**
- Clear sparse layout (columns 1,3,5,7 are all NULL)
- 53 valid pointers (good density)
- Pattern is consistent throughout
- Last row has sentinels (typical end marker)

---

## 3. mut_table_analyzer.py (with --compare)

### Example Run
```bash
$ python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E --compare
```

### Expected Output (if different)
```
[... table layouts for both ROMs ...]

================================================================================
Table Comparison at offset 0x00FE5E
================================================================================

Comparing against base: e8-t040-2byte_logging.hex

vs e8-t041-2byte_logging.hex:
  ✗ Found 4 difference(s):

    Position [2,0] (0x00FE7E): 0x1024 -> 0x1025
    Position [2,4] (0x00FE86): 0x1025 -> 0x1026
    Position [5,2] (0x00FEB2): 0xFD7F -> 0xFD80
    Position [8,6] (0x00FEEA): 0xFBBF -> 0xFBC0
```

**OR if identical:**
```
vs e8-t041-2byte_logging.hex:
  ✓ Tables are identical
```

**Interpretation:**
- If identical: Table structure is stable (good!)
- If different: These entries changed between tunes (logging params?)

---

## 4. mut_table_analyzer.py (with --xml)

### Example Run
```bash
$ python scripts/mut_table_analyzer.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex --offset 0xFE5E --xml
```

### Expected Output
```
[... table layout and stats ...]

EcuFlash XML snippet:
<!-- MUT Table Definition - Test at offset 0x00FE5E -->
<muttable offset="0xFE5E" layout="dense">
  <mutentry requestid="0x00" address="0x1020" />
  <mutentry requestid="0x02" address="0xFFDF" />
  <mutentry requestid="0x04" address="0x1021" />
  <mutentry requestid="0x06" address="0xFFBF" />
  <mutentry requestid="0x08" address="0x1022" />
  <mutentry requestid="0x0A" address="0xFF7F" />
  <mutentry requestid="0x0C" address="0x1023" />
  <mutentry requestid="0x0E" address="0xFF3F" />
  <mutentry requestid="0x10" address="0x1024" />
  <mutentry requestid="0x12" address="0xFEFF" />
  <!-- ... and 43 more pointer entries -->
</muttable>
```

**Interpretation:**
- Copy this XML into your EcuFlash ROM definition
- Test with EvoScan
- Verify values make sense

---

## 5. rom_mut_finder.py (with --verbose)

### Example Run
```bash
$ python scripts/rom_mut_finder.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex --top 3 --verbose
```

### Expected Output
```
ROM(s):
  - cars\2003-evo-viii\roms\tunes\e8-t041-2byte_logging.hex

Top 3 candidate MUT table base addresses
(median score of shown results: 156.60)

 1. offset=0x00FE5E  score=156.75  ptrs=53  ffff=25  zero=25  changed= 0  anchors=0  layout=dense                unique=70  top=0.21
    first words: 0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000
    Full table layout (15 rows × 8 columns):
      Row  0: 0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000 
      Row  1: 0x1022 0x0000 0xFF7F 0x0000 0x1023 0x0000 0xFF3F 0x0000 
      Row  2: 0x1024 0x0000 0xFEFF 0x0000 0x1025 0x0000 0xFEBF 0x0000 
      [... rows 3-13 ...]
      Row 14: 0x103C 0x0000 0xF8FF 0x0000 0xFFFF 0x0000 0xFFFF 0x0000 

 2. offset=0x00FE60  score=156.75  ptrs=53  ffff=25  zero=25  changed= 0  anchors=0  layout=dense                unique=70  top=0.21
    first words: 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000 0x1022
    Full table layout (15 rows × 8 columns):
      Row  0: 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000 0x1022 
      [... etc ...]

 3. offset=0x00FE5A  score=156.60  ptrs=52  ffff=25  zero=26  changed= 0  anchors=0  layout=dense                unique=70  top=0.22
    first words: 0xFFEF 0x0000 0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000
    [... etc ...]
```

**Interpretation:**
- Top 3 are very close in score (same table, different alignment)
- All show the sparse pattern (alternating 0x0000)
- 0xFE5E starts with pointer (typical)

---

## 6. rom_mut_finder.py (with --dump-hex)

### Example Run
```bash
$ python scripts/rom_mut_finder.py cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex --dump-hex 0xFE5E
```

### Expected Output
```
Hex dump at offset 0x00FE5E in cars\2003-evo-viii\roms\tunes\e8-t041-2byte_logging.hex:
Total: 120 words (240 bytes)

  0x00FE5E: 0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000 
  0x00FE6E: 0x1022 0x0000 0xFF7F 0x0000 0x1023 0x0000 0xFF3F 0x0000 
  0x00FE7E: 0x1024 0x0000 0xFEFF 0x0000 0x1025 0x0000 0xFEBF 0x0000 
  0x00FE8E: 0x1026 0x0000 0xFE7F 0x0000 0x1027 0x0000 0xFE3F 0x0000 
  0x00FE9E: 0x1028 0x0000 0xFDFF 0x0000 0x1029 0x0000 0xFDBF 0x0000 
  0x00FEAE: 0x102A 0x0000 0xFD7F 0x0000 0x102B 0x0000 0xFD3F 0x0000 
  0x00FEBE: 0x102C 0x0000 0xFCFF 0x0000 0x102D 0x0000 0xFCBF 0x0000 
  0x00FECE: 0x102E 0x0000 0xFC7F 0x0000 0x102F 0x0000 0xFC3F 0x0000 
  0x00FEDE: 0x1030 0x0000 0xFBFF 0x0000 0x1031 0x0000 0xFBBF 0x0000 
  0x00FEEE: 0x1032 0x0000 0xFB7F 0x0000 0x1033 0x0000 0xFB3F 0x0000 
  0x00FEFE: 0x1034 0x0000 0xFAFF 0x0000 0x1035 0x0000 0xFABF 0x0000 
  0x00FF0E: 0x1036 0x0000 0xFA7F 0x0000 0x1037 0x0000 0xFA3F 0x0000 
  0x00FF1E: 0x1038 0x0000 0xF9FF 0x0000 0x1039 0x0000 0xF9BF 0x0000 
  0x00FF2E: 0x103A 0x0000 0xF97F 0x0000 0x103B 0x0000 0xF93F 0x0000 
  0x00FF3E: 0x103C 0x0000 0xF8FF 0x0000 0xFFFF 0x0000 0xFFFF 0x0000 
```

**Interpretation:**
- Raw hex view for manual inspection
- Shows clear alternating pattern
- Useful for comparing with hex editor
- Can paste into documentation

---

## What to Look For

### Good Signs ✅
- High confidence rating (✓✓✓)
- 40-60 pointers
- 20-30 sentinels/nulls
- Clear repeating patterns
- Similar scores for nearby offsets
- Stable across ROM versions

### Bad Signs ❌
- Low confidence (✗)
- < 12 or > 80 pointers
- Too repetitive (low unique count)
- Random-looking data
- Drastically different from nearby offsets

### Uncertain Signs ⚠️
- MEDIUM confidence (✓✓)
- Unusual pointer patterns
- Very different across ROM versions
- Many "other" values

---

## Common Patterns

### Sparse Even Layout (Your Case)
```
[Pointer] [0x0000] [Pointer] [0x0000] [Pointer] [0x0000] ...
```
Columns 0,2,4,6 contain data; 1,3,5,7 are padding

### Dense Layout (Alternative)
```
[Pointer] [Pointer] [Sentinel] [Pointer] [0x0000] [Pointer] ...
```
Every column potentially contains data

### End Markers
```
... [Pointer] [0x0000] [0xFFFF] [0x0000] [0xFFFF] [0x0000]
```
Typically last row has sentinels

---

**Note:** These are illustrative examples. Your actual output may vary slightly based on your specific ROM files, but the structure will be similar.

