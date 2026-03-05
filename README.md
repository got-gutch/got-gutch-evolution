# got-gutch-evolution

Projects used to facilitate and manage on-going tuning and maintenance for multiple vehicles, with a primary focus on the Mitsubishi Lancer Evolution VIII. This repository manages tuning artifacts, datalogs, ROMs, and documentation for each car. While the Evo is the current focus, the structure supports additional vehicles and their respective tuning journeys.

## Repository Layout

```
got-gutch-evolution/
├── cars/
│   ├── 2003-evo-viii/          ← 2003 USDM Mitsubishi Lancer Evolution VIII
│   │   ├── README.md           ← vehicle details, purchase history, YouTube channel
│   │   ├── roms/
│   │   │   ├── README.md       ← ROM naming convention
│   │   │   ├── stock/          ← base ROM snapshots read directly from the ECU
│   │   │   └── tunes/          ← derived tune ROMs (.bin and .hex)
│   │   ├── docs/
│   │   │   ├── modifications/
│   │   │   │   └── README.md   ← all modifications (2003–2026)
│   │   │   └── repairs/        ← repair records
│   │   └── logs/               ← important EvoScan datalogs
│   └── 2017-ford-focusrs/      ← 2017 Ford Focus RS (Current Status: waiting on an engine from Mountune)
└── scripts/
    ├── evoscan_parser.py       ← parse EvoScan 2.9 data log CSV files
    ├── rom_manager.py          ← list, compare and diff ROM files
    ├── tune_tables.py          ← extract octane / ignition tables from ROM files
    └── boost_tuner.py          ← suggest WGDC updates for 3-port boost control
```

## Tooling

All scripts require **Python 3.10+**. It is recommended to use a virtual environment.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Git Bash / Windows)
source /c/Users/bgutch/GotGutchWorkSpace/.got-gutch-venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### EvoScan log parser

```bash
# Summarise all channels in a directory of EvoScan logs
python scripts/evoscan_parser.py cars/2003-evo-viii/logs

# Summarise a specific log file
python scripts/evoscan_parser.py cars/2003-evo-viii/logs/EvoScanDataLog_2026.03.02_18.01.58.csv

# Export a cleaned CSV from a log
python scripts/evoscan_parser.py cars/2003-evo-viii/logs/EvoScanDataLog_2026.03.02_18.01.58.csv --export output.csv
```

### ROM manager

```bash
# List all ROMs under the Evo's ROM directory
python scripts/rom_manager.py list cars/2003-evo-viii/roms

# Show tunes derived from a specific base ROM
python scripts/rom_manager.py tunes bgutch_2003_evo8_02_18_2026.hex \
    --dir cars/2003-evo-viii/roms/tunes

# Byte-level diff two ROM files
python scripts/rom_manager.py diff \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_02_18_2026.hex \
    cars/2003-evo-viii/roms/tunes/bgutch_2003_evo8_02_18_2026_tune_001_rpm_limit.hex
```

### Tune tables

```bash
# Print the octane table from a real ROM
python scripts/tune_tables.py show cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_02_18_2026.hex --table octane

# Diff the ignition table between two real ROMs
python scripts/tune_tables.py compare \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_02_18_2026.hex \
    cars/2003-evo-viii/roms/tunes/bgutch_2003_evo8_02_18_2026_tune_001_rpm_limit.hex \
    --table ignition
```

### Boost tuner

Analyze WOT pulls to validate plumbing logic and suggest Wastegate Duty Cycle (WGDC) updates for tuning a 3-port solenoid.

```bash
# Analyze a log to check spring pressure or suggested WGDC increases
python scripts/boost_tuner.py cars/2003-evo-viii/logs/EvoScanDataLog_2026.03.02_18.01.58.csv --target 21.0 --spring 12.0
```

## ROM Naming Convention

```
{owner}_{car_year}_{car_model}_{MM}_{DD}_{YYYY}[_tune_{NNN}_{description}].{ext}
```

See [cars/2003-evo-viii/roms/README.md]('./cars/2003-evo-viii/roms/README.md') for full details.

## ECU Toolchain

| Tool            | Version / Model      |
|-----------------|----------------------|
| Data logging    | EvoScan 2.9          |
| ROM editing     | EcuFlash             |
| Flash cable     | Openport 1.3U        |
