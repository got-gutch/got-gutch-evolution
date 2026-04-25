# MUT Finder Quick Reference

## 🎯 Your Current Situation

**Best candidate found**: `0x00FE5E`  
**ROMs analyzed**: e8-t030, e8-t040, e8-t041  
**Status**: Ready to validate and test

---

## 📋 Quick Commands

### 1. Validate Your Top Candidates
```bash
python scripts/quick_mut_check.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    0xFE5E 0xFE60 0xFE5A
```
⏱️ Fast - shows which offset looks most valid

---

### 2. See Full Table Layout
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E
```
📊 Shows the complete 15×8 table with pointers highlighted

---

### 3. Compare Across Your ROM Versions
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t030-disable_cat.hex \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --compare
```
🔍 Shows what changed between tune versions

---

### 4. Generate EcuFlash XML for Testing
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --xml
```
📝 Creates XML snippet to add to your EcuFlash definition

---

### 5. Re-run Full Scan (if needed)
```bash
python scripts/rom_mut_finder.py \
    cars/2003-evo-viii/roms/tunes/e8-t030-disable_cat.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --top 12 --verbose > run_002.out
```
🔎 Full heuristic scan with verbose output

---

## 🚀 Recommended Next Steps

### Step 1: Quick Check (30 seconds)
```bash
python scripts/quick_mut_check.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    0xFE5E
```

### Step 2: Full Analysis (1 minute)
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E
```

### Step 3: Compare Versions (2 minutes)
```bash
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t040-2byte_logging.hex \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E \
    --compare
```

### Step 4: Test in EcuFlash
1. Generate XML snippet
2. Add to your ROM definition
3. Test with EvoScan
4. Verify logged values make sense

---

## 📚 Documentation

- **Full guide**: `scripts/MUT_FINDER_GUIDE.md`
- **Your results analysis**: `ANALYSIS_run_001.md`
- **Main README**: `README.md`

---

## 🔧 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "File not found"
Check your current directory:
```bash
pwd  # Should show: .../got-gutch-evolution
```

### "No output" or "Hangs"
Try with explicit Python path:
```bash
python3 scripts/quick_mut_check.py ...
```
or
```bash
/c/Users/bgutch/GotGutchWorkSpace/.got-gutch-venv/Scripts/python scripts/quick_mut_check.py ...
```

---

## 💡 Pro Tips

1. **Always use multiple ROM versions** when scanning - it dramatically improves accuracy
2. **The verbose flag is your friend** - use it on your top 3 candidates
3. **Compare before testing** - see what changed between tunes first
4. **Start with sparse_even layout** - your pattern suggests this is the type
5. **Keep run_*.out files** - they're useful for tracking your search history

---

## 🎓 Understanding Your Results

### Your Top Candidate Pattern
```
0x1020 0x0000 0xFFDF 0x0000 0x1021 0x0000 0xFFBF 0x0000
  ↑     ↑      ↑     ↑      ↑     ↑      ↑     ↑
  Ptr   Pad    Sent  Pad    Ptr   Pad    Sent  Pad
```

This is **sparse even layout**:
- Columns 0,2,4,6: Memory addresses
- Columns 1,3,5,7: Padding (always 0x0000)
- Request ID = (row × 4) + (column ÷ 2)

### Score Meaning
- **156.75** = Excellent candidate
- **> 150** = Very likely valid
- **< 100** = Probably wrong

### Confidence Levels
- **HIGH ✓✓✓**: 40+ pointers, 20+ sentinels
- **MEDIUM ✓✓**: 25+ pointers, 10+ sentinels  
- **LOW ✓**: Meets minimum requirements
- **INVALID ✗**: Doesn't look like MUT table

---

*Last updated: March 29, 2026*

