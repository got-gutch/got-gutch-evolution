# Stock / Base ROMs — 2003 Evo VIII

Base ROMs are read directly from the ECU using EvoScan 2.9 via the Tactrix Openport 1.3U.
Each file is a full binary image of the ECU at the time it was read.

## ROM Inventory

| File | Date | Notes |
|------|------|-------|
| `bgutch_2003_evo8_11_11_2025.bin` | 2025-11-11 | Base ROM before wastegate and MAP scaling work |
| `bgutch_2003_evo8_02_18_2026.bin` | 2026-02-18 | Base ROM before RPM limit tune |

## How to Read a ROM

1. Connect the Tactrix Openport 1.3U to the OBD-II port.
2. Open EvoScan 2.9 and select **ECU → Read ROM**.
3. Save the file here using the naming convention defined in `../README.md`.

## How to Compare Two Base ROMs

```bash
python scripts/rom_manager.py diff \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_11_11_2025.bin \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_02_18_2026.bin
```
