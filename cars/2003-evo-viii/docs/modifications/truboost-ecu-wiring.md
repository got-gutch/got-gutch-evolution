# Wiring the AEM Tru-Boost to the Factory ECU

This guide outlines how to connect the AEM Tru-Boost 0-5V analog output to the factory ECU. Doing so allows EvoScan to log accurate boost readings without relying on the factory 1-bar MDP sensor, which maxes out at atmospheric pressure.

## The Hardware Strategy: Use a Patch Harness

Instead of hacking into your factory engine wire loom, it is highly recommended to buy an Evo 8 ECU Patch Harness (often called a boomslang or extension harness).

```text
[Factory Wiring Harness] ---> [Plug-and-Play Patch Harness] ---> [Factory ECU]
                                         |
                            (Wire Tru-Boost Here!)
```

**Why this makes it easy:** It sits as a bridge between your factory car plugs and the ECU. You can sit comfortably at a desk, splice the AEM wire directly into the patch harness, and then just walk out to the car and plug it in line. If you ever make a mistake or want to revert to stock, you just unplug the patch harness.

## Step-by-Step Wiring Guide

The Tru-Boost harness has a **White Wire** designated for the 0-5V Analog Output. Your factory ECU has a dedicated pin for the old 1-bar MDP sensor that was diagnosed as useless for logging boost. By cutting the MDP signal wire and feeding it the Tru-Boost's white wire, EvoScan will seamlessly read the true gauge pressure instead.

### 1. Identify Your Pins (2003 Evo VIII 4-Plug ECU)

You will be pinning or splicing into **Pin 73 (Manifold Differential Pressure Sensor Input)**.
- **Location:** Pin 73 is located on the smallest of the four ECU plugs (the 22-pin connector, usually all the way on the right side of the ECU block). 
- **Color:** It is typically a **Light Green** wire on the factory loom.

### 2. Make the Connection

**Option A: Custom Patch Harness (Recommended)**  
If you are ordering a patch harness, you can have the vendor modify it before shipping. For example, you can send the following request to [Tuning Technology](https://www.tuningtechnology.net/) when purchasing their Denso 76-Way Extension Harness:

> I am purchasing your "Denso 76-Way Extension Harness (26p-16p-12p-22p)" for a USDM 2003 Mitsubishi Evolution VIII ECU. Before you ship it, I would like to pay a custom service fee to have you modify the jumper on your workbench to break out flying leads for two specific 0-5V auxiliary gauge inputs:
> 
> 1. AEM TruBoost Input (0-5V): On the 22-pin connector plug, please cut the wire at Pin 73 (Manifold Differential Pressure input). Cap or insulate the engine-harness side of the cut. On the ECU side of the cut, solder a 3-foot flying lead using white wire, clearly labeled "To TruBoost Analog Out".
> 
> 2. AEM X-Series Wideband Input (0-5V): On the 16-pin connector plug, please cut the wire at Pin 75 (Rear O2 Sensor input). Cap or insulate the engine-harness side of the cut. On the ECU side of the cut, solder a 3-foot flying lead using a blue (or preferred contrasting color) wire, clearly labeled "To Wideband Analog Out".
> 
> 3. Shared Clean Sensor Ground: Please tap into the wire at Pin 92 or Pin 98 (Sensor Ground circuit) on the extension harness. Solder a 3-foot flying lead using black wire, clearly labeled "ECU Sensor Ground". I will use this to ground the analog circuits of both gauges back to the ECU's reference plane to eliminate signal noise.
> 
> Please let me know the additional cost for the bench time to add these custom flying leads to my order so I can proceed with the purchase!

**Option B: DIY No-Soldering Method (Using Extension Harness)**  
If you don't want to pay for a pre-modified harness but still want to protect your factory wiring, you can modify a standard patch harness yourself:

1. Acquire a standard **Denso 76-Way Extension Harness (26p-16p-12p-22p)**.
2. Locate the wire for Pin 73 on the 22-pin plug of the *extension harness*.
3. **Cut it completely in half.** (This disconnects the factory 1-bar sensor on the intake manifold so its voltage doesn't fight the gauge).
4. Strip the insulation off the **ECU-side** of that cut wire on the extension harness, and strip the end of the **AEM White Wire**.
5. Use a high-quality Heat-Shrink Butt Connector or a Posi-Lock wire connector to join the AEM White wire to the ECU side of Pin 73. Shrink it down with a lighter or heat gun to seal it from moisture.
6. Tape up the other side of the cut wire (the side going toward the engine plugs) so it can't short out.
7. Finally, plug the modified extension harness in between your car's factory harness and the ECU.

### 3. Share a Common Ground

For a 0-5V analog signal to be accurate and steady, the gauge and the ECU need to agree on what "0 Volts" feels like.

1. Take the **Black Wire** from the AEM Tru-Boost harness and splice it into a factory ECU ground wire.
2. Specifically, use **Pin 92 or Pin 98 (Sensor Ground circuit)**. 

This eliminates signal "noise" or fluctuating boost readings in your logs.

## The Final Software Step in EvoScan

Once it's wired up, you just need to tell EvoScan to look at Pin 73 using the AEM scaling formula instead of the Mitsubishi MUTII math.

Open your EvoScan configuration, create a new custom evaluation item for Pin 73 (often labeled MAP/MDP or Request 38 depending on your XML setup), and replace your old formula with the official AEM 0-5V scaling math:

`Boost (psig) = (9.375 * Voltage) - 14.7`

Because EvoScan reads the 0-5V window as a 0-255 byte value (`x`), the exact EvoScan XML formula string looks like this:

```text
Formula="(0.1838 * x) - 14.7"
```

Once that's typed in, turn the key, and your laptop screen will perfectly mirror whatever the physical gauge face says.
