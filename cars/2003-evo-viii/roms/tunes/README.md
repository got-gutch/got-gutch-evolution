# Tune ROMs — 2003 Evo VIII

Tune ROMs are derived from a base ROM using EcuFlash and flashed via EvoScan 2.9.
Each tune is saved in both `.bin` (raw binary) and `.hex` (Intel HEX) formats.

## Tune Inventory

| File | Base ROM Date | Tune # | Description |
|------|---------------|--------|-------------|
| `bgutch_2003_evo8_11_11_2025_tune_010_wastegateclear.bin` | 2025-11-11 | 010 | Wastegate clearance adjustment |
| `bgutch_2003_evo8_11_11_2025_tune_010_wastegateclear.hex` | 2025-11-11 | 010 | Wastegate clearance adjustment (HEX) |
| `bgutch_2003_evo8_11_11_2025_tune_020_map_scaling.bin` | 2025-11-11 | 020 | MAP sensor scaling update |
| `bgutch_2003_evo8_11_11_2025_tune_020_map_scaling.hex` | 2025-11-11 | 020 | MAP sensor scaling update (HEX) |
| `bgutch_2003_evo8_02_18_2026_tune_001_rpm_limit.bin` | 2026-02-18 | 001 | RPM limit adjustment |
| `bgutch_2003_evo8_02_18_2026_tune_001_rpm_limit.hex` | 2026-02-18 | 001 | RPM limit adjustment (HEX) |

## Tune Sequence Notes

- Tune numbers are zero-padded to 3 digits and increment by 10 within the same base ROM session, leaving room to insert tunes between existing ones.
- Tune 001 on the `02_18_2026` base started a fresh sequence for that flash session.

## How to Flash a Tune

1. Open EcuFlash and load the tune `.bin` file.
2. Connect the Tactrix Openport 1.3U to the OBD-II port.
3. In EvoScan 2.9 select **ECU → Write ROM** and select the `.bin` file.

## How to Compare a Tune Against Its Base ROM

```bash
python scripts/rom_manager.py diff \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_11_11_2025.bin \
    cars/2003-evo-viii/roms/tunes/bgutch_2003_evo8_11_11_2025_tune_010_wastegateclear.bin
```
