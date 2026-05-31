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

## ⚠️ Critical Findings

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

## Immediate Recommendations

> ⛔ **Do not make any more WOT pulls until this is resolved. The car is hitting 33 psi on every pull and has started knocking.**

| Priority | Action |
|----------|--------|
| 🔴 **1 — Verify solenoid port plumbing** | Confirm Port 1 = Vent, Port 2 = Wastegate actuator, Port 3 = Turbo pressure source. Swap if needed. |
| 🔴 **2 — Chase the boost leak whistle behind the battery** | A leak in the WG reference line will prevent the actuator from seeing full boost signal and keep the gate shut. |
| 🟡 **3 — Drastically reduce TruBoost duty cycle target** | Try backing the duty cycle setting down to **7–8 psi** to see if the solenoid can start controlling boost at a lower target before walking it up. |
| 🟡 **4 — Test at zero-duty (solenoid off / disconnected)** | Run a pull with the TruBoost solenoid electrically disconnected. Boost should be controlled only by the wastegate spring (~11 psi). If boost still hits 33 psi with the solenoid disconnected, the wastegate actuator itself is the problem. |
| 🟢 **5 — Consider ECU WGDC table** | With WGDC at 0% from the ECU, there's no safety net. A ROM update to add a moderate base WGDC table would give the ECU some ability to modulate boost even if the external controller misbehaves. |

---

## Boost Controller Settings Reference

| Parameter | Current | Suggested Next Test |
|-----------|---------|---------------------|
| Crack PSI | 11 psi | Keep at 11 psi |
| Duty Cycle | 13 psi | **Reduce to 7–8 psi** |
| ECU WGDC | 0% (ROM) | Discuss with tuner — add base table |

---

## Session Notes

- Log `09.13.47` (67 rows, no WOT) was likely captured at idle/low load — possibly a warm-up or parameter check pass.
- InjDutyCycle at peak boost: **50–83%** — injectors are not maxed out, fueling headroom exists.
- FuelTrim_InUse = 0 across all WOT rows — closed-loop fuel trim is being suspended at WOT, which is normal.
- TimingAdv climbs from ~8° to 23° across the RPM range — normal progression, but advancing into 21–23° at 33 psi of boost with knock events is concerning.

