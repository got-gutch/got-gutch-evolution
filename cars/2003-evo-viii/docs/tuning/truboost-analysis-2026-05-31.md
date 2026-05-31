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

## Why the TruBoost Gauge Showed 17.5 psi But the Logs Show 33 psi

This is the most important finding of this session and it directly points to the root cause.

### The Ramp Transition (from `09.15.05` log)

| Time (s) | TPS% | RPM | MAP (psig) | WGDC |
|----------|------|-----|------------|------|
| 7.25 | 15.7% | 718 | 6.6 | **100%** |
| 7.59 | 15.3% | 625 | 8.9 | **100%** |
| 7.91 | 21.2% | 843 | **14.3** | **100%** |
| 8.25 | 27.5% | 2531 | **17.8** | 0% |
| 8.56 | 48.6% | 3406 | **33.1** | 0% |
| 8.87 | 100% | 3468 | 33.1 | 0% |

Boost went from **17.8 psi → 33 psi in 0.31 seconds.** EvoScan samples at ~4–5 Hz (~0.25s per sample), so the entire boost build is compressed into a single sample gap. The logger never captured the intermediate values.

### The TruBoost Gauge Reads Its Own Reference Port — Not the Manifold

The TruBoost controller measures boost using a dedicated **boost reference signal line** — the same line it uses to decide when to start opening the wastegate. This line is tee'd off **above the throttle body**, with a **reducer fitting** that steps the line down to the smaller diameter hose that came with the AEM TruBoost kit.

**The TruBoost gauge was showing 17.5 psi because that is what its reference line was seeing — not because boost was only 17.5 psi in the manifold.** The actual manifold boost was 33 psi the entire pull.

### Photo of the Tee Fitting

![TruBoost reference tee](tee-photo-2026-05-31.jpg)

The photo clearly shows the issue:
- **Top connections (red spring clips):** Full-diameter hose — the main boost reference line tee'd from above the throttle body
- **Bottom connections (green spring clips):** The reducer steps down to the significantly smaller diameter hose that came with the AEM TruBoost kit

The inner diameter of the bottom tube appears to be roughly **half** the top line. Since flow area scales with diameter **squared**, the smaller tube has approximately **~25% of the flow area** of the source line. At high boost this is essentially a pinhole relative to the volume the source tap can deliver — the TruBoost reference port is severely starved.

### Why Is the Reference Line Reading ~15.5 psi Lower Than the Manifold?

**The reducer fitting is the restriction.** This is not a leak — it is a flow restriction. Here's what's happening:

1. Manifold boost = **33 psi**, flowing through a full-diameter tap above the throttle body
2. The reducer steps the line down to the small-diameter hose from the gauge kit
3. At high boost/high flow, the smaller diameter **cannot equalize pressure fast enough** — there is a measurable pressure drop across the reducer
4. The TruBoost controller sees **~17.5 psi** through the restricted line
5. The TruBoost thinks boost is 17.5 psi and never fully commands the wastegate open
6. The wastegate stays shut — boost runs away to the ECU cut limit

The higher the actual boost, the larger the pressure drop across the restriction. At low boost (say 5–8 psi) the reducer probably reads close to accurate. At 33 psi there's a ~15.5 psi drop across it. This is a known issue with using undersized reference lines on high-boost applications.

> **The whistle behind the battery is a separate issue** — it is still worth investigating as an independent boost leak, but it is NOT the cause of the 17.5 vs 33 psi discrepancy. The reducer is.

### The WGDC Clue

Notice in the ramp above: **WGDC = 100% while boost is building from 6 → 14 psi, then drops to 0% at 17.8 psi and stays at 0% for the rest of the pull.** This is the ECU's ROM-side WGDC table making a brief appearance during spool — it commands 100% to help build boost, then drops out. Once it drops to 0%, the TruBoost is supposed to take over. But with the reference line leaking, it never gets an accurate boost signal and the gate stays shut.

### Summary of the Disconnect

| What | Reading | Why |
|------|---------|-----|
| EvoScan MAP (manifold) | 33 psi | Direct MAP sensor in the intake manifold — accurate |
| TruBoost gauge | 17.5 psi | Reads through a **reducer-restricted reference line** — ~15.5 psi pressure drop across the fitting at full boost |
| WGDC (ECU ROM) | 0% at WOT | 3 of 4 maps zeroed; ECU drops out and TruBoost takes over — but TruBoost is flying blind on a restricted signal |

**The reducer fitting is not "wrong" for low-boost applications, but at 33 psi it causes a ~15.5 psi measurement error. The TruBoost controller and wastegate actuator are both working from bad data.**

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

In the final session log (`09.19.16`) — after 3 maps were already zeroed — **WGDC is 0% the entire time including idle and decel**, and the car built to 33 psi just fine. So the remaining map is not contributing to the overboost.

### Should You Zero It?

**Yes — zero it**, with one caveat:

- The 4th map only fires at idle, decel, and early spool. It is **not causing the overboost** and not relevant to WOT boost control.
- With it zeroed, the ECU is completely hands-off on the wastegate in all conditions. This gives the TruBoost **clean, uncontested authority** — which is exactly what you want when dialing it in.
- The `09.19.16` session already proved the car operates fine with zero ECU WGDC authority — it drove, pulled, and hit rev limiter without issue.
- Once the reducer is replaced and the TruBoost starts actually controlling boost, you don't want the ECU's 4th map potentially fighting it at any RPM or load point.

> **Caveat:** Get the reducer fixed first. Zeroing the last map before fixing the reference line just means the TruBoost has clean authority but is still working off a bad signal. Fix the hardware, then zero the map, then re-test.

---

## Immediate Recommendations (Updated)

### 1. ECU Boost Cut on Every Single Pull — 32.9 psi

Every WOT pull in every log hits **47.59–47.79 psia (32.9–33.1 psig)** and stays there. This is not a peak — MAP is **pegged at the ceiling** across the entire WOT window. The car is running into the ECU's boost cut limit (≈ 33 psi) on **every pull without exception**. The TruBoost controller at `crack=11 / duty=13` is **not controlling boost at all**.

### 2. WGDC = 0% the Entire Time

The `WGDC` column reads **0% on every WOT row** across all logs. This means the ECU's ROM-side wastegate duty cycle table is outputting zero — the ECU is not commanding the solenoid at all. The car is **100% relying on the TruBoost external controller** to manage the wastegate. Since the external controller is not holding boost down, the wastegate is staying shut and the turbo keeps building until the ECU cuts fuel.

### 3. KnockSum Activity in the Last Session (09.19.16)

In the final log, **KnockSum values of 1 and 2** appear during the WOT pulls. This is light knock — the ECU is detecting detonation events. With uncontrolled boost at 33 psi and timing advancing to 21–23°, this is a dangerous combination. The ECU is catching it, but continued operation in this state risks engine damage.

### 4. Fuel Cut Confirmed on 09.19.16

In the second-to-last row of the first pull in `09.19.16`, MAP drops sharply from 47.59 psia to **18.19 psia at 7000 RPM** while TPS is still at 100%. This is the ECU cutting fuel at the boost/load limit — same behavior as documented previously after the exhaust upgrade.

---

## Root Cause Analysis

The TruBoost solenoid is controlling the reference pressure line to the wastegate actuator. With `crack=11 psi` set, the solenoid should be allowing the wastegate to crack open at 11 psi, preventing boost from building past the target. Instead, boost is climbing straight to the ECU's 33 psi cut limit.

**Most likely causes (in order of probability):**

1. **TruBoost solenoid plumbing is incorrect** — if the port assignments (Vent / Wastegate / Turbo) are wrong, the solenoid may be working backwards, i.e., pressurizing the actuator reference line instead of venting it, which would hold the wastegate *closed* harder.

2. **TruBoost duty cycle setting of 13 psi is too aggressive** — at 13 psi the controller may be commanding the solenoid so heavily that it is pressurizing the WG actuator cap beyond what the spring can overcome, effectively sealing the wastegate shut.

3. **Wastegate actuator is stuck or undersized** — if the actuator cannot open against the boost pressure, the wastegate stays closed regardless of the solenoid command.

4. **Boost leak downstream of the WG reference port** — if the signal line to the actuator has a leak, the actuator sees lower pressure than the manifold and the gate stays closed. This ties back to the whistle behind the battery that was noted during boost leak testing.

---

## Immediate Recommendations (Updated)

> ⛔ **Do not make any more WOT pulls until the reducer is replaced. The car is hitting 33 psi on every pull and has started knocking.**

| Priority | Action |
|----------|--------|
| 🔴 **1 — Relocate the TruBoost gauge reference line** | To avoid using a reducer entirely, move the TruBoost reference line tap to a smaller-diameter vacuum source on the intake manifold that naturally matches the AEM hose size. The **Blow-Off Valve (BOV/diverter valve) vacuum line** is the safest and most common place to tee in for a boost gauge. *(Avoid tapping the Fuel Pressure Regulator (FPR) line, as a leak there can cause a dangerous lean condition under boost).* After this fix, the gauge and manifold boost readings should match. |
| 🔴 **2 — Separately investigate the whistle behind the battery** | This is an independent boost leak — not the cause of the gauge discrepancy, but still a real boost leak that can affect power and spool consistency. Find and repair it. |
| 🟡 **3 — Zero out the 4th WGDC map** | Safe to do. It only fires at idle/decel/early spool and isn't causing the overboost. Zeroing it gives the TruBoost clean uncontested authority. Do this **after** fixing the reducer so you're not walking into a test session with two unknowns. |
| 🟡 **4 — Reset TruBoost duty cycle to a conservative starting point** | After fixing the reference line, start with duty cycle at **10–11 psi** (matching crack pressure) and walk up slowly from there. The controller will now see accurate boost and can actually do its job. |
| 🟢 **5 — Re-log after the reducer fix** | First pull after the fix should be done carefully — the TruBoost will now command the wastegate for real. Boost should drop significantly from 33 psi. Tune from there. |

## Boost Controller Settings Reference

| Parameter | Current | After Reducer Fix |
|-----------|---------|-------------------|
| Crack PSI | 11 psi | Keep at 11 psi |
| Duty Cycle | 13 psi | Reset to 10–11 psi, walk up |
| ECU WGDC (maps 1–3) | 0% | Keep at 0% |
| ECU WGDC (map 4) | Active | **Zero it out** (after reducer fix) |

---

## Session Notes

- Log `09.13.47` (67 rows, no WOT) was likely captured at idle/low load — possibly a warm-up or parameter check pass.
- InjDutyCycle at peak boost: **50–83%** — injectors are not maxed out, fueling headroom exists.
- FuelTrim_InUse = 0 across all WOT rows — closed-loop fuel trim is being suspended at WOT, which is normal.
- TimingAdv climbs from ~8° to 23° across the RPM range — normal progression, but advancing into 21–23° at 33 psi of boost with knock events is concerning.

