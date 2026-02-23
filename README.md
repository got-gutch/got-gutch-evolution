# got-gutch-evolution

Projects used to facilitate and manage on-going Mitsubishi Lancer Evolution tuning.

## Repository Layout

```
got-gutch-evolution/
├── cars/
│   └── 2003-evo-viii/          ← 2003 USDM Mitsubishi Lancer Evolution VIII
│       ├── README.md           ← vehicle details, purchase history, YouTube channel
│       ├── roms/
│       │   ├── README.md       ← ROM naming convention
│       │   ├── stock/          ← base ROM snapshots read directly from the ECU
│       │   └── tunes/          ← derived tune ROMs (.bin and .hex)
│       └── docs/
│           ├── modifications/
│           │   ├── 2003-2014/  ← mods performed 2003–2014
│           │   └── 2014-2026/  ← mods performed 2014–2026
│           └── repairs/        ← repair records
└── scripts/
    ├── evoscan_parser.py       ← parse EvoScan 2.9 data log CSV files
    ├── rom_manager.py          ← list, compare and diff ROM files
    └── tune_tables.py          ← extract octane / ignition tables from ROM files
```

## Tooling

All scripts require **Python 3.10+** and use only the standard library.

### EvoScan log parser

```bash
# Summarise all channels in a log file
python scripts/evoscan_parser.py path/to/log.csv

# Export a cleaned CSV
python scripts/evoscan_parser.py path/to/log.csv --export cleaned.csv
```

### ROM manager

```bash
# List all ROMs under the car's ROM directory
python scripts/rom_manager.py list cars/2003-evo-viii/roms

# Show tunes derived from a specific base ROM
python scripts/rom_manager.py tunes bgutch_2003_evo8_11_11_2025.bin \
    --dir cars/2003-evo-viii/roms/tunes

# Byte-level diff two ROM files
python scripts/rom_manager.py diff \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_11_11_2025.bin \
    cars/2003-evo-viii/roms/tunes/bgutch_2003_evo8_11_11_2025_tune_010_wastegateclear.bin
```

### Tune tables

```bash
# Print the octane table from a ROM
python scripts/tune_tables.py show cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_11_11_2025.bin --table octane

# Diff the ignition table between two ROMs
python scripts/tune_tables.py compare \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_11_11_2025.bin \
    cars/2003-evo-viii/roms/tunes/bgutch_2003_evo8_11_11_2025_tune_020_map_scaling.bin \
    --table ignition

# Export a table to CSV
python scripts/tune_tables.py export \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_11_11_2025.bin \
    --table octane --out /tmp/octane.csv
```

## ROM Naming Convention

```
{owner}_{car_year}_{car_model}_{MM}_{DD}_{YYYY}[_tune_{NNN}_{description}].{ext}
```

See `cars/2003-evo-viii/roms/README.md` for full details.

## ECU Toolchain

| Tool            | Version / Model              |
|-----------------|------------------------------|
| Data logging    | EvoScan 2.9                  |
| ROM editing     | EcuFlash                     |
| Flash cable     | Tactrix Openport 1.3U        |
