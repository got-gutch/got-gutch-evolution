# ROM Files — 2003 Evo VIII

## Naming Convention

All ROM files follow the pattern:

```
{owner}_{car_year}_{car_model}_{MM}_{DD}_{YYYY}[_tune_{NNN}_{description}].{ext}
```

| Segment         | Description                                                   |
|-----------------|---------------------------------------------------------------|
| `owner`         | Short identifier for the tuner (e.g. `bgutch`)                |
| `car_year`      | Model year of the car (e.g. `2003`)                           |
| `car_model`     | Car model shorthand (e.g. `evo8`)                             |
| `MM_DD_YYYY`    | Date the base ROM was captured (month_day_year)               |
| `tune_NNN`      | *(tune ROMs only)* Zero-padded tune sequence number           |
| `description`   | *(tune ROMs only)* Brief snake_case description of the change |
| `.ext`          | `.bin` = raw binary image; `.hex` = Intel HEX format          |

**Base ROM example:**
```
bgutch_2003_evo8_02_18_2026.bin
```

**Tune ROM example:**
```
bgutch_2003_evo8_02_18_2026_tune_001_rpm_limit.bin
bgutch_2003_evo8_02_18_2026_tune_001_rpm_limit.hex
```

## Directory Layout

| Directory | Contents                                                     |
|-----------|--------------------------------------------------------------|
| `stock/`  | Base ROM snapshots read directly from the ECU               |
| `tunes/`  | Derived tune ROMs built from a base ROM via EcuFlash         |

## Tooling

Use `scripts/rom_manager.py` to:
- List all ROMs with parsed metadata
- Show the tunes derived from a given base ROM
- Diff two ROM files byte-by-byte
