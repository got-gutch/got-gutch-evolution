# Tune ROMs — 2003 Evo VIII

Tune ROMs are derived from a base ROM using EcuFlash and flashed via EvoScan 2.9.
Only `.hex` (Intel HEX) formats are tracked here as they are the primary flash artifacts.

## Tune Inventory

| Tune # | File | Base ROM Date | Flash Date | Description |
|--------|------|---------------|------------|-------------|
| 001 | [`e8-t001-rpm-limit.hex`](./e8-t001-rpm-limit.hex) | 2025-11-11 | 2026-02-18 | **First Flash:** RPM limit adjustment |
| 010 | [`e8-t010-wgclear.hex`](./e8-t010-wgclear.hex) | 2025-11-11 | Feb 2026 | WGDC tables cleared; Boost Cut Delay Timer reduced; Turbo Boost Error Correct zeroed; boost load/limit tables updated |
| 020 | [`e8-t020-mapscale.hex`](./e8-t020-mapscale.hex) | 2025-11-11 | Feb 2026 | MAP sensor scaling update |
| 021 | [`e8-t021-mut1.hex`](./e8-t021-mut1.hex) | 2025-11-11 | Feb 2026 | Attempted MUT 2-byte load configuration (Failed) |
| 022 | [`e8-t022-mut2.hex`](./e8-t022-mut2.hex) | 2025-11-11 | Feb 2026 | Refined MUT 2-byte load addresses (Failed) |
| 023 | [`e8-t023-v1byte.hex`](./e8-t023-v1byte.hex) | 2025-11-11 | 2026-03-07 | Revert to Tune 020 logic; Pivot to 1-byte load logging |

## Tune Sequence Notes

- **Flash History:**
  - **Tune 023:** Flashed on 2026-03-07 at 08:55:00. This flash successfully reverted the ECU to Tune 020 logic while incorporating 1-byte load logging to bypass the 2-byte stability issues encountered in Tunes 021 and 022. Log preserved in [`023_tune.log`](./023_tune.log).
- **Tune 010 Notes:**
  - WGDC tables were zeroed out, except table 4, which was set to all `100` values.
  - Boost Cut Delay Timer was reduced to `500`.
  - Turbo Boost Error Correct table was zeroed out.
  - Turbo Boost Error Correct values: `0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0`.
  - Boost Desired Engine Load Table 1 was updated to: `159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 133.125 125 110.625`.
  - Boost Desired Engine Load Table 2 was updated to: `159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 159.375 143.125 133.125 125 110.625`.
  - Boost Limit table was updated to: `230 230 225 225 225 225 225 225 225`.
- **Naming Convention:** All tunes now use the prefix `e8-tXXX` (Evo 8 - Tune XXX) followed by a short descriptor to fit within the narrow EvoScan "Write ROM" window.
- **2-Byte vs 1-Byte Load:** After several attempts (Tunes 021/022) to stabilize 2-byte MUT load logging, the project is shifting to 1-byte load logging. While 1-byte has less precision, it is more reliable for tracking higher load boundaries without the offset/alignment issues encountered in the 2-byte attempts.
- Tune numbers are zero-padded to 3 digits and increment by 10 within the same base ROM session, leaving room to insert tunes between existing ones.
- Tune 001 on the `02_18_2026` base started a fresh sequence for that flash session.

## How to Flash a Tune

1. Open EcuFlash and load the tune `.hex` file.
2. Connect the Tactrix Openport 1.3U to the OBD-II port.
3. In EvoScan 2.9 select **ECU → Write ROM** and select the `.hex` file.

## How to Compare a Tune Against Its Base ROM

```bash
python scripts/rom_manager.py diff \
    cars/2003-evo-viii/roms/stock/bgutch_2003_evo8_11_11_2025.hex \
    cars/2003-evo-viii/roms/tunes/bgutch_2003_evo8_11_11_2025_tune_010_wastegateclear.hex
```
