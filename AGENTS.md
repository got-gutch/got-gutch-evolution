# AGENTS.md

## What This Repo Is
- Multi-vehicle tuning and maintenance workspace, with current activity centered in `cars/2003-evo-viii/`.
- Source of truth is markdown records + artifacts: docs, ROM files, logs, and images.

## Big-Picture Architecture
- Artifact-first layout:
  - `cars/<vehicle>/docs/` for maintenance, repairs, and modification history.
  - `cars/<vehicle>/logs/` for EvoScan CSVs and log bundles.
  - `cars/<vehicle>/roms/` for stock/tuned ROM snapshots.
  - `scripts/` for CLI tools that summarize logs and compare ROMs.
- Human workflow: perform work on car -> capture evidence (date + logs/photos) -> update vehicle docs -> run scripts for analysis summaries when needed.

## Critical Developer/Tuner Workflows
1. Add a maintenance entry (example: windshield replacement)
   - Edit `cars/2003-evo-viii/docs/repairs/README.md` (or the relevant vehicle docs file).
   - Follow the existing entry template/table style from `cars/2003-evo-viii/docs/repairs/README.md`.
   - Include part, install date, vendor/technician if known, and reason for replacement.
2. Add an identified issue for follow-up (example: front suspension banging under braking)
   - Record issue under `cars/2003-evo-viii/docs/repairs/README.md` as planned/future work.
   - Keep symptom wording concrete, include when it occurs, and add next diagnostic step.
   - Link any related logs/images in `cars/2003-evo-viii/logs/` or `cars/2003-evo-viii/docs/`.
3. Record a modification and analyze created logs
   - Add/update the modification entry in `cars/2003-evo-viii/docs/modifications/README.md`.
   - Summarize logs with `python scripts/evoscan_parser.py cars/2003-evo-viii/logs --summary`.
   - Inspect WOT pulls with `python scripts/evoscan_parser.py <log.csv> --wot`.
   - Reference resulting log filenames directly in the modification notes.

## Project-Specific Conventions
- Keep modification/repair entries in the same markdown table format already used in:
  - `cars/2003-evo-viii/docs/modifications/README.md`
  - `cars/2003-evo-viii/docs/repairs/README.md`
- Preserve ROM filename schema used by `scripts/rom_manager.py`:
  - `{owner}_{car_year}_{car_model}_{MM}_{DD}_{YYYY}[_tune_{NNN}_{description}].{bin|hex}`
- Keep EvoScan log naming as generated (`EvoScanDataLog_YYYY.MM.DD_HH.MM.SS.csv`); do not rename casually.
- Keep CLI output formats stable where possible; existing docs and saved outputs depend on readable, consistent output.

## Integration Points
- External toolchain from `README.md`: EvoScan 2.9 (logging), EcuFlash (ROM/XML editing), Openport 1.3U (flashing).
- XML/config references in `cars/2003-evo-viii/configs/evo-scan-data-settings/*.xml`.
- Long-lived evidence artifacts include markdown analyses and captured command output files (for example `ANALYSIS_run_001.md`, `run_001.out`).

## Where Agents Should Look Before Editing
- `README.md` for repo map and canonical commands.
- `cars/2003-evo-viii/README.md` for vehicle-specific context.
- `cars/2003-evo-viii/docs/modifications/README.md` and `cars/2003-evo-viii/docs/repairs/README.md` for entry format to mirror.
- Target script docstring and `argparse` section in `scripts/*.py` before changing CLI behavior.

