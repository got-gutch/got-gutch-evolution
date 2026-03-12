# Stock / Base ROMs — 2003 Evo VIII

## Vehicle & ROM Info
- **Make:** Mitsubishi
- **Model:** Lancer
- **Submodel:** EVO8
- **Transmission:** Manual
- **Year:** 2004
- **Case ID:** MN132874
- **Internal ID:** 94170008
- **Memory Model:** SH7052

Base ROMs are read directly from the ECU using EvoScan 2.9 via the Tactrix Openport 1.3U.

## ROM Inventory

| File | Date | Notes |
|------|------|-------|
| [`bgutch_2003_evo8_02_18_2026.hex`](./bgutch_2003_evo8_02_18_2026.hex) | 2026-02-18 | **Golden ROM:** The final stock pull before the first tune was flashed. |

## How to Read a ROM

1. Connect the Tactrix Openport 1.3U to the OBD-II port.
2. Open EvoScan 2.9 and select **ECU → Read ROM**.
3. Save the file here as a `.hex` file.

## How to Compare a Tune to the Golden ROM

```bash
python scripts/rom_manager.py diff \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_02_18_2026.hex \
    cars/2003-evo-viii/roms/tunes/e8-t001-rpm-limit.hex
```
