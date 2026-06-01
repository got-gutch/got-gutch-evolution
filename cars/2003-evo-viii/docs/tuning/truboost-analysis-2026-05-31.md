# TruBoost Tuning Session Analysis — 2026-05-31

**Vehicle:** 2003 Mitsubishi Lancer Evolution VIII  
**Date:** May 31, 2026  
**TruBoost Settings:**
- Crack PSI (open): **11 psi**
- Duty Cycle Target: **13 psi**

**Tools Used:** `evoscan_parser.py --wot`, `boost_tuner.py --target 21 --spring 11 --hack01`

---

## Log Files

| Log | Total Rows | WOT Pulls | Notes |
|-----|-----------|-----------|-------|
| [EvoScanDataLog_2026.05.31_09.12.36.csv](../../logs/EvoScanDataLog_2026.05.31_09.12.36.csv) | 99 | 1 | WOT pull, boost cut confirmed |
| [EvoScanDataLog_2026.05.31_09.13.47.csv](../../logs/EvoScanDataLog_2026.05.31_09.13.47.csv) | 67 | 0 | Idle/cruise only, no WOT |
| [EvoScanDataLog_2026.05.31_09.15.05.csv](../../logs/EvoScanDataLog_2026.05.31_09.15.05.csv) | 118 | 1 | WOT pull, boost cut confirmed |
| [EvoScanDataLog_2026.05.31_09.19.16.csv](../../logs/EvoScanDataLog_2026.05.31_09.19.16.csv) | 86 | 2 | Two WOT pulls, light knock detected |

---

## WOT Pull Summary

| Log | Pull | Max Boost (psig) | RPM Range | Max Speed | Avg WGDC | Max KnockSum | Avg Timing |
|-----|------|-----------------|-----------|-----------|----------|--------------|------------|
| 09.12.36 | 1 | **33.09** | 4406–6312 | 46 mph | 0% | 0 | 12° |
| 09.15.05 | 1 | **33.09** | 3468–5968 | 74 mph | 0% | 0 | 11° |
| 09.19.16 | 1 | **32.90** | 3500–7000 | 79 mph | 0% | **2** | 13° |
| 09.19.16 | 2 | **32.90** | 5031–5718 | 89 mph | 0% | **1** | 12° |

> **MAP was logged as PSIA. Boost psig = MAP psia − 14.7. All values above are psig.**

---

## Why the Logs Showed 33 psi (The Phantom Overboost)

This is the most important finding of this session and completely changes the narrative from a dangerous mechanical overboost to a simple software calibration error.

### 1. The USDM 1-Bar MDP Sensor
The USDM 2003 Evo VIII does not have a factory MAP sensor capable of reading positive manifold pressure (boost). It utilizes a 1-bar MDP (Manifold Differential Pressure) sensor meant entirely for EVAP and EGR diagnostics. This sensor maxes out at atmospheric pressure (0 psig / 14.5 psia).

### 2. The Software Calculation Error
The `Mitsubishi MUTII EFI.xml` configuration file was using Request ID 38 with a mathematically incorrect formula designed for a JDM 3-bar MAP sensor: `0.19348 * x`.

### 3. The Phantom 33 PSI
The moment the car enters *any* positive boost during WOT, the factory 1-bar sensor instantly pegs its maximum hardware voltage (~4.84V, which corresponds to an ADC value of `x=247`). 
When EvoScan applies the 3-bar formula to that flatlined 247 value, the math works out to exactly 33 psi:
`0.19348 * 247 = 47.78 psia`
`47.78 psia - 14.7 = 33.08 psig`

The 33 psi we saw in all our logs is **literally just the 1-bar sensor maxing out**, which EvoScan misinterpreted as 33 psi because of the 3-bar scaling formula. The TruBoost gauge reading of 17.5 PSI previously (and 8-10 PSI currently on baseline spring pressure) is the actual physical boost level of the engine. The engine was perfectly safe the entire time.

### The WGDC Clue

Notice in the logs: **WGDC = 0% across the entirety of the WOT pull.** This means the ECU's ROM-side WGDC table was completely hands-off. The ECU was not causing an overboost, and the TruBoost was doing exactly what it was set up to do, but our logging software was lying to us.

---

## WGDC Map Analysis — Should You Zero the 4th Map?

### What the Logs Show

The non-zero WGDC activity across logs 1–3 (before 3 maps were zeroed) follows a clear pattern:

| Condition | WGDC | RPM | TPS | MAP (psig) |
|-----------|------|-----|-----|------------|
| Idle / low RPM decel | **100%** | 625–1562 | ~15–22% | vacuum to ~11 psi |
| Coasting / engine braking | 17→34→51→68→85→100% | 1000–2500 | ~15% | vacuum |
| WOT ramp (spool phase) | **100%** | 625–2531 | 15–27% | building to ~14 psi |
| WOT fully open | **0%** | 3468+ | 100% | 33 psi |

**The 4th remaining map is the idle/decel/low-load map.** It commands WGDC=100% while the car is at idle, coasting, and during the very beginning of the spool before TPS goes high. Once the pull is fully underway (TPS ≥ ~30%, RPM ≥ ~2500), WGDC drops to 0% and the TruBoost takes over.

In the final session log (`09.19.16`) — after 3 maps were already zeroed — **WGDC is 0% the entire time including idle and decel**, and the car operated just fine. So the remaining map is not contributing to any WGDC interference.

### Should You Zero It?

**Yes — zero it**, for clean engineering house-keeping:

- The 4th map only fires at idle, decel, and early spool. It is **not relevant to WOT boost control**.
- With it zeroed, the ECU is completely hands-off on the wastegate in all conditions. This gives the TruBoost **clean, uncontested authority** — which is exactly what you want when dialing it in.
- The `09.19.16` session already proved the car operates fine with zero ECU WGDC authority — it drove, pulled, and hit rev limiter without issue.

---

## Root Cause Analysis

The "overboost/runaway" failure was a mathematical phantom. The engine was running on baseline wastegate spring pressure (8-10 psi) or previously up to 17.5 psi, completely within safe mechanical limits.

**Immediate Conclusions:**

1. **The 33 PSI Overboost is Fake:** It is just the 1-bar MDP sensor flatline scaled with a 3-bar formula.
2. **The Engine is Safe:** The true boost level is what the TruBoost gauge is showing (currently 8-10 psi).
3. **ECU WGDC is Hands-Off:** At WOT, the ECU commands 0% WGDC. The TruBoost has full control.

---

## Immediate Recommendations (Updated)

| Priority | Action |
|----------|--------|
| 🟢 **1 — Uncheck Request ID 38 (MAP) in EvoScan** | Since the factory sensor cannot read boost, logging it with the wrong formula only causes confusion. Stop logging it until an aftermarket 3-bar MAP sensor is installed and patched into the ROM. |
| 🟢 **2 — Zero out the 4th WGDC map** | Safe to do. It only fires at idle/decel/early spool. Zeroing it gives the TruBoost clean uncontested authority and is good engineering house-keeping. |
| 🟢 **3 — Walk the TruBoost Duty Cycle up safely** | Now that we know the engine is operating safely on spring pressure (8-10 psi), we can slowly increase the TruBoost Duty Cycle from its baseline to target our true 14 psi window. |
| 🟡 **4 — Focus on Load-based Tuning** | Since we cannot log true boost via MAP, rely on `Load1B` (or `LoadCalc`) for load-based tuning insights alongside the physical TruBoost gauge readings. |

## Boost Controller Settings Reference

| Parameter | Current | Next Steps |
|-----------|---------|-------------------|
| Crack PSI | 11 psi | Keep at 11 psi |
| Duty Cycle | 13% | Walk up slowly to target 14 psi |
| ECU WGDC (maps 1–3) | 0% | Keep at 0% |
| ECU WGDC (map 4) | Active | **Zero it out** for a clean baseline |

---

## Session Notes

- Log `09.13.47` (67 rows, no WOT) was likely captured at idle/low load — possibly a warm-up or parameter check pass.
- InjDutyCycle at peak boost: **50–83%** — injectors are not maxed out, fueling headroom exists.
- FuelTrim_InUse = 0 across all WOT rows — closed-loop fuel trim is being suspended at WOT, which is normal.
- TimingAdv climbs from ~8° to 23° across the RPM range — normal progression, but advancing into 21–23° at 33 psi of boost with knock events is concerning.
