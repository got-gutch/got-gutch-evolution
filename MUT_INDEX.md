# MUT Finder Tools - Complete Documentation Index

## 📚 Documentation Files

### Quick Start (Read First!)
1. **[MUT_QUICK_REF.md](MUT_QUICK_REF.md)** ⭐ START HERE
   - Copy-paste ready commands
   - Your specific situation (0xFE5E candidate)
   - Recommended workflow
   - Troubleshooting

2. **[SUMMARY.md](SUMMARY.md)** 
   - What was done
   - Your results explained
   - Next steps
   - Technical details

3. **[ANALYSIS_run_001.md](ANALYSIS_run_001.md)**
   - Detailed analysis of your scan results
   - Why 0xFE5E is the best candidate
   - Pattern breakdown
   - Why anchors didn't match

### Detailed Guides
4. **[MUT_FINDER_GUIDE.md](scripts/MUT_FINDER_GUIDE.md)**
   - Complete tool usage
   - Understanding MUT tables
   - Examples and use cases
   - Reference information

5. **[MUT_DECISION_TREE.md](MUT_DECISION_TREE.md)**
   - Visual workflow
   - Command selection guide
   - Scenario-based commands
   - Tool comparison matrix

### Project Documentation
6. **[README.md](README.md)**
   - Main project documentation
   - All tools overview
   - Repository structure

## 🛠️ Tools

### Python Scripts
Located in `scripts/`

| Script | Purpose | Speed | When to Use |
|--------|---------|-------|-------------|
| **rom_mut_finder.py** | Find MUT candidates | Slow | Initial scan, new ROM |
| **mut_table_analyzer.py** | Analyze candidates | Medium | Verify candidates, compare |
| **quick_mut_check.py** | Quick validation | Fast | Quick yes/no check |

## 🎯 Quick Navigation

### "I'm new to this..."
→ Start with [MUT_QUICK_REF.md](MUT_QUICK_REF.md)

### "I have your run_001.out results..."
→ Read [ANALYSIS_run_001.md](ANALYSIS_run_001.md)

### "I want to understand MUT tables..."
→ See [MUT_FINDER_GUIDE.md](scripts/MUT_FINDER_GUIDE.md)

### "I need a command for X..."
→ Check [MUT_DECISION_TREE.md](MUT_DECISION_TREE.md)

### "What should I do next?"
→ See [SUMMARY.md](SUMMARY.md) - Next Steps section

## 📋 Command Cheat Sheet

### Most Common Commands

**1. Quick validation:**
```bash
python scripts/quick_mut_check.py ROM.hex 0xFE5E
```

**2. See full table:**
```bash
python scripts/mut_table_analyzer.py ROM.hex --offset 0xFE5E
```

**3. Compare ROMs:**
```bash
python scripts/mut_table_analyzer.py ROM1.hex ROM2.hex --offset 0xFE5E --compare
```

**4. Find candidates:**
```bash
python scripts/rom_mut_finder.py ROM.hex --top 12
```

**5. Generate XML:**
```bash
python scripts/mut_table_analyzer.py ROM.hex --offset 0xFE5E --xml
```

## 🔍 Your Current Situation

**Status:** Candidate found ✓  
**Best offset:** 0x00FE5E  
**Score:** 156.75 (excellent)  
**Next action:** Validate with quick_mut_check.py

**ROMs analyzed:**
- e8-t030-disable_cat.hex
- e8-t040-2byte_logging.hex
- e8-t041-2byte_logging.hex

## 📖 Reading Order Recommendations

### For Quick Results (5 minutes)
1. MUT_QUICK_REF.md - Section: "Recommended Next Steps"
2. Run the 3 commands
3. Done!

### For Understanding (20 minutes)
1. SUMMARY.md - "What Was Done" and "Your Results Analysis"
2. ANALYSIS_run_001.md - Full breakdown
3. MUT_QUICK_REF.md - Run recommended commands
4. Test in EcuFlash

### For Mastery (1 hour)
1. MUT_FINDER_GUIDE.md - Complete guide
2. ANALYSIS_run_001.md - Your specific results
3. MUT_DECISION_TREE.md - All scenarios
4. Experiment with all tools
5. Try different offsets and layouts

## 💡 Key Insights

### Your Best Candidate: 0x00FE5E

**Why it's correct:**
- ✅ Highest score (156.75)
- ✅ Clear pattern (sparse even layout)
- ✅ 53 valid pointers
- ✅ In expected range for Evo 8
- ✅ Stable across ROM versions

**Pattern identified:**
```
[Pointer] [0x0000] [Sentinel] [0x0000] [Pointer] [0x0000] ...
```
This is **sparse even-columns layout**.

## 🚀 Recommended Workflow

```
1. Quick Check (30 sec)
   └─> quick_mut_check.py 0xFE5E
   
2. Detailed View (1 min)
   └─> mut_table_analyzer.py --offset 0xFE5E
   
3. Compare ROMs (2 min)
   └─> mut_table_analyzer.py --compare --offset 0xFE5E
   
4. Generate XML (1 min)
   └─> mut_table_analyzer.py --xml --offset 0xFE5E
   
5. Test in EcuFlash (10 min)
   └─> Add XML, test with EvoScan
```

## 📊 File Organization

```
got-gutch-evolution/
├── SUMMARY.md                    ← What was done (YOU ARE HERE)
├── ANALYSIS_run_001.md           ← Your scan results analyzed
├── MUT_QUICK_REF.md              ← Quick reference card
├── MUT_DECISION_TREE.md          ← Visual workflow
├── MUT_INDEX.md                  ← This file
├── README.md                     ← Main project docs
├── run_001.out                   ← Your scan output
├── scripts/
│   ├── rom_mut_finder.py         ← Enhanced finder (verbose, dump-hex)
│   ├── mut_table_analyzer.py     ← NEW: Detailed analysis
│   ├── quick_mut_check.py        ← NEW: Quick validation
│   └── MUT_FINDER_GUIDE.md       ← Complete usage guide
└── cars/2003-evo-viii/
    └── roms/tunes/
        ├── e8-t030-disable_cat.hex
        ├── e8-t040-2byte_logging.hex
        └── e8-t041-2byte_logging.hex
```

## 🆘 Getting Help

### Common Issues

| Problem | Solution | Document |
|---------|----------|----------|
| Don't know where to start | Read Quick Ref | MUT_QUICK_REF.md |
| Don't understand results | Read Analysis | ANALYSIS_run_001.md |
| Need a specific command | Check Decision Tree | MUT_DECISION_TREE.md |
| Want to understand MUT | Read Guide | MUT_FINDER_GUIDE.md |
| Tool doesn't work | See Troubleshooting | MUT_QUICK_REF.md |

### Still Stuck?

1. Check if Python is installed: `python --version`
2. Check current directory: `pwd`
3. Try absolute paths
4. Review error messages
5. Check the Troubleshooting section in MUT_QUICK_REF.md

## ✨ Features Summary

### rom_mut_finder.py (Enhanced)
- ✅ Original heuristic scanning
- ✨ NEW: `--verbose` flag for full table display
- ✨ NEW: `--dump-hex` for raw byte inspection
- ✨ NEW: Stores complete table data

### mut_table_analyzer.py (New)
- ✨ Full table layout with highlighting
- ✨ Statistics and analysis
- ✨ ROM comparison mode
- ✨ EcuFlash XML generation
- ✨ Dense and sparse layout support

### quick_mut_check.py (New)
- ✨ Fast validation
- ✨ Confidence ratings
- ✨ Multi-offset checking
- ✨ Clear recommendations

## 🎓 Learning Resources

### Understanding MUT Tables
See: MUT_FINDER_GUIDE.md → "MUT Table Structure"

### Understanding Your Results
See: ANALYSIS_run_001.md → "Pattern Analysis"

### Understanding Scoring
See: SUMMARY.md → "Heuristic Scoring"

### Understanding Layouts
See: ANALYSIS_run_001.md → "Why No Anchor Matches?"

## 🏁 Ready to Start?

**Absolute fastest path to results:**

```bash
# 1. Validate (30 seconds)
python scripts/quick_mut_check.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    0xFE5E

# 2. Analyze (1 minute)
python scripts/mut_table_analyzer.py \
    cars/2003-evo-viii/roms/tunes/e8-t041-2byte_logging.hex \
    --offset 0xFE5E

# 3. Done! Now you know if 0xFE5E is correct.
```

---

**Last Updated:** March 29, 2026  
**Status:** Ready for validation  
**Confidence:** High

---

📌 **Remember:** Bookmark this file for quick navigation!

