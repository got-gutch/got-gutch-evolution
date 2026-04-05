# Modifications — 2003 Evo VIII

> YouTube channel: https://www.youtube.com/@bradgutch — shorts for this car have titles starting with **"Evo 8"**

## K&N Typhoon Cold Air Intake

| Field       | Value                          |
|-------------|-------------------------------|
| Part        | K&N Typhoon Cold Air Intake    |
| Installed   | 2003–2014 (exact date unknown) |
| Purpose     | Increased airflow to the turbo |

**References / YouTube Shorts:** https://www.youtube.com/@bradgutch *(find short titled "Evo 8 …" and add link here)*

---

## New Windshield

| Field     | Value                         |
|-----------|------------------------------|
| Installed | 2003–2014 (exact date unknown)|
| Reason    | Replacement                   |

**References / YouTube Shorts:** https://www.youtube.com/@bradgutch *(find short titled "Evo 8 …" and add link here)*

---

## New Front Bumper

| Field     | Value                         |
|-----------|------------------------------|
| Installed | 2003–2014 (exact date unknown)|
| Reason    | Replacement                   |

**References / YouTube Shorts:** https://www.youtube.com/@bradgutch *(find short titled "Evo 8 …" and add link here)*

---

## Aftermarket Intercooler

| Field       | Value                                        |
|-------------|---------------------------------------------|
| Part        | Slightly larger aftermarket intercooler      |
| Vendor      | Unknown                                      |
| Installed   | 2014–2026 (exact date unknown)               |
| Purpose     | Improved charge cooling over stock unit      |

**References / YouTube Shorts:** https://www.youtube.com/@bradgutch *(find short titled "Evo 8 …" and add link here)*

---

## Meagan Racing Radiator

| Field       | Value                                        |
|-------------|---------------------------------------------|
| Part        | Meagan Racing Radiator                       |
| Installed   | On or around Dec 3, 2025                     |
| Purpose     | Improved cooling capacity                    |

**References / YouTube Shorts:** https://youtube.com/shorts/M4zNpgPBOyk?si=UKC8vTpiQe7WUJKZ

---

## Exedy Flywheel and Clutch Kit

| Field       | Value                                                                      |
|-------------|---------------------------------------------------------------------------|
| Flywheel    | Exedy MF04 Chromoly Racing Flywheel                                        |
| Clutch      | Exedy Sport Clutch Kit — Part # 05803HD                                    |
| Installed   | 2014–2026 (exact date unknown)                                             |
| Purpose     | Reduced rotating mass, improved clutch engagement for performance driving  |

**References / YouTube Shorts:** https://www.youtube.com/@bradgutch *(find short titled "Evo 8 …" and add link here)*

---

## Right and Left Drip Moldings Replacement

| Field     | Value           |
|-----------|-----------------|
| Installed | March 2, 2026   |
| Reason    | Replacement     |

**Data Logs:** [EvoScanDataLog_2026.03.02_18.01.58.csv](../../logs/EvoScanDataLog_2026.03.02_18.01.58.csv)

**References / YouTube Shorts:** https://youtube.com/shorts/UXUkUpyreZQ?si=6SoOyYVxbmHiZqml

---

## Exhaust System Upgrade (Down Pipe Back)

| Field       | Value                                                |
|-------------|------------------------------------------------------|
| Race Pipe   | Boosted Fabrication Resonated Race Pipe (Ultra Quiet Style) |
| Cat-Back    | Tomei Titanium Cat-Back Exhaust                      |
| Installed   | March 2, 2026                                        |
| Purpose     | Performance exhaust upgrade — replaced from down pipe back |

**Over-Boost Condition & ECU Fuel Cut:** Data logs captured after this modification revealed a critical over-boost event that triggered an ECU fuel cut (the audible "boom").

<img src="https://github.com/user-attachments/assets/d4633249-4159-4310-bd0d-200ce3616277" alt="Over-boost event graph showing Engine RPM, Speed, and Boost (MAP) during the fuel cut">

**The Breakdown:**
1. **The Overboost Spike:** At approximately 3,400 RPM under 100% throttle, MAP sensor hit **47.78 psia**. This translates to **33.08 psi of boost** (47.78 psia - 14.7 atmospheric = 33.08 psig). Target boost was 21 psi — **overshooting by 12 psi in a split second**.

2. **Root Cause - WGDC at 100%:** The log shows Wastegate Duty Cycle (WGDC) was pegged at **100.0%** during the entire pull. In the Evo ECU, 100% duty cycle means the solenoid is keeping the wastegate slammed shut to build boost as fast as possible. With the new Tomei titanium exhaust installed, the turbo experienced significantly reduced backpressure and spooled much faster than the ECU expected. Because the WGDC didn't drop, the turbo kept pumping until it hit its physical limit.

3. **The "Loud Boom" (Fuel Cut):** When the ECU detected 33 psi, it hit the Boost Cut / Load Limit and immediately cut fuel to the injectors while under heavy load. This violent event is the ECU's safety mechanism to prevent engine damage. The log shows a KnockSum of only 1 during the spike, confirming the ECU intervened in time to save the motor from detonation.

**Action Required:** ECU tuning adjustment needed to prevent wastegate duty cycle from staying at 100% with the new low-backpressure exhaust system.

**Data Logs:** [EvoScanDataLog_2026.03.02_18.01.58.csv](../../logs/EvoScanDataLog_2026.03.02_18.01.58.csv) — see MAP column

**References / YouTube Shorts:** https://www.youtube.com/@bradgutch *(find short titled "Evo 8 …" and add link here)*

---

## STM Evo 7/8/9 O2 Downpipe — OEM-Style Housing

| Field       | Value                                                |
|-------------|------------------------------------------------------|
| Part        | STM Evo 7/8/9 O2 Downpipe Recirculated for OEM-Style Housing |
| Technician  | Eli at Tuned Up LLC                                  |
| Installed   | March 20, 2026                                       |
| Purpose     | Remove the factory downpipe restriction and improve exhaust flow |

**Notes:** The STM downpipe was installed by Tuned Up LLC along with the rear bushing replacement. This completes the latest exhaust hardware change and pairs with the existing Boosted Fabrication resonated race pipe and Tomei cat-back exhaust.

**Data Logs:**
- [EvoScanDataLog_2026.03.21_09.22.49.csv](../../logs/EvoScanDataLog_2026.03.21_09.22.49.csv)
- [EvoScanDataLog_2026.03.21_09.25.58.csv](../../logs/EvoScanDataLog_2026.03.21_09.25.58.csv)

---

## Rear Bushing Replacement

| Field       | Value                      |
|-------------|----------------------------|
| Installed   | March 20, 2026             |
| Reason      | Replacement / refresh      |
| Shop        | Tuned Up LLC               |

**Notes:** Rear bushings were replaced during the same service visit as the STM downpipe installation.

**Data Logs:**
- [EvoScanDataLog_2026.03.21_09.22.49.csv](../../logs/EvoScanDataLog_2026.03.21_09.22.49.csv)
- [EvoScanDataLog_2026.03.21_09.25.58.csv](../../logs/EvoScanDataLog_2026.03.21_09.25.58.csv)

---

## Boost Solenoid Vent — Muffler Redirect

| Field       | Value                                                |
|-------------|------------------------------------------------------|
| Installed   | April 5, 2026 (Easter 2026)                          |
| Reason      | Resolve boost solenoid issues; reduce intake contamination |
| Purpose     | Redirect boost solenoid vent from intake/input to a dedicated muffler |

**Notes:** Previously, the boost solenoid (3-port wastegate solenoid) was venting back to the intake/input. The vent line has been rerouted to a muffler so it vents to atmosphere through the muffler instead. This change resolved the boost solenoid issues that were present on the car. The car was reassembled and returned to service on Easter 2026.

**References / YouTube Shorts:** https://www.youtube.com/@bradgutch *(find short titled "Evo 8 …" and add link here)*

---

## ROM Flash — `e8-t030-disable_cat.hex`

| Field       | Value |
|-------------|-------|
| ROM       | `e8-t030-disable_cat.hex` |
| Flash Log | `030_tune.log` |
| Flashed   | March 21, 2026 |
| Purpose   | Disable cat-related behavior after the downpipe install |

**Notes:** The flash completed successfully and the verify pass matched all ECU pages. The log shows only `FB01` changed, which is consistent with a targeted tune update.

**Data Logs:**
- [EvoScanDataLog_2026.03.21_09.22.49.csv](../../logs/EvoScanDataLog_2026.03.21_09.22.49.csv)
- [EvoScanDataLog_2026.03.21_09.25.58.csv](../../logs/EvoScanDataLog_2026.03.21_09.25.58.csv)

---
