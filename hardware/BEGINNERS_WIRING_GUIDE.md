# Beginner's Wiring Guide - ESP32-S3 Nashville Numbers

**The simplest possible guide to connecting everything together**

---

## What You're Building

A single PCB with everything integrated:

```
          ┌─────────────────────────────────────────┐
          │                                         │
 USB-C ──▶│  [Microphone]  [Brain]  [Display]     │
          │   Listen       ESP32     Show           │
          │   to audio     Process   chords         │
          │                                         │
          └─────────────────────────────────────────┘
               Nashville Numbers - All in One!
```

**Total cost per board:** ~$10-12 (with JLCPCB assembly)

---

## The 5 Main Components

### 1. 🧠 ESP32-S3-WROOM-1 (The Brain)
- **What it does:** Listens to audio, detects chords, controls display
- **Cost:** $2.80
- **Package:** Pre-made module with WiFi antenna
- **Pins:** 48 pins (but we only use about 12)

### 2. 🎤 INMP441 (The Microphone)
- **What it does:** Captures audio and converts to digital
- **Cost:** $1.20
- **Interface:** I2S (digital audio, just 3 wires + power)
- **Quality:** Studio-quality MEMS microphone

### 3. 📟 TM1637 + 4-Digit Display (The Screen)
- **What it does:** Shows chord numbers (like "1", "4", "5")
- **Cost:** $1.10 total
- **Interface:** Just 2 wires + power
- **Brightness:** Adjustable, super bright for stage use

### 4. 🔌 CP2102N (The USB Chip)
- **What it does:** Lets you program via USB
- **Cost:** $0.85
- **Features:** Auto-reset (no button pressing!)

### 5. ⚡ AMS1117-3.3 (The Power Supply)
- **What it does:** Converts 5V USB to 3.3V for chips
- **Cost:** $0.12
- **Output:** 500mA (plenty for this project)

---

## Connection Overview (Simplified)

```
                   Power Flow
                   ──────────
   USB-C (5V)
       │
       ├──────────► TM1637 Display (can use 5V)
       │
       ▼
   AMS1117-3.3 Regulator
       │
       │ (3.3V)
       ├──────────► ESP32-S3
       ├──────────► INMP441 Mic
       └──────────► CP2102N

                   Data Flow
                   ─────────
   INMP441 Mic ──(I2S)──► ESP32 ──(2-wire)──► TM1637 Display
                            ▲
                            │
                       (USB Serial)
                            │
                        CP2102N ◄─── USB-C
```

---

## Pin-by-Pin Connections

### 🎤 Microphone to ESP32

**INMP441 has 6 pins:**

```
Looking at INMP441 module:
┌─────────────┐
│  ○ ○ ○     │  ← Small hole (mic opening)
│  ○ ○ ○     │
└─────────────┘
 │ │ │ │ │ │
 │ │ │ │ │ └─ L/R    → Connect to GND (left channel)
 │ │ │ │ └─── WS     → Connect to ESP32 GPIO5
 │ │ │ └───── SCK    → Connect to ESP32 GPIO6
 │ │ └─────── SD     → Connect to ESP32 GPIO4
 │ └───────── GND    → Connect to Ground
 └─────────── VDD    → Connect to 3.3V
```

**Quick table:**
| INMP441 Pin | Goes To | What It Does |
|-------------|---------|--------------|
| VDD | 3.3V | Power |
| GND | Ground | Ground |
| SD | ESP32 GPIO4 | Audio data |
| SCK | ESP32 GPIO6 | Bit clock |
| WS | ESP32 GPIO5 | Left/Right timing |
| L/R | Ground | Select left channel |

**Add one capacitor:** 100nF (0.1µF) between VDD and GND, close to the mic

---

### 📟 Display to ESP32

**TM1637 + Display has 4 pins:**

```
TM1637 chip side view:
┌──────────┐
│ ○ ○ ○ ○  │
└──────────┘
  │ │ │ │
  │ │ │ └─ DIO → ESP32 GPIO19 (with 10kΩ pull-up to VCC)
  │ │ └─── CLK → ESP32 GPIO18 (with 10kΩ pull-up to VCC)
  │ └───── GND → Ground
  └─────── VCC → 5V (or 3.3V, but dimmer)
```

**Quick table:**
| Display Pin | Goes To | Notes |
|-------------|---------|-------|
| VCC | 5V | Brighter! (3.3V also works) |
| GND | Ground | Ground |
| CLK | ESP32 GPIO18 | Clock signal + 10kΩ to VCC |
| DIO | ESP32 GPIO19 | Data signal + 10kΩ to VCC |

**Important:** Add 10kΩ resistors from CLK and DIO to VCC (pull-up resistors)

---

### 🔌 USB Chip to ESP32

**CP2102N connections:**

```
CP2102N pinout (20-pin QFN):
       ┌─────────┐
  D+ ─┤         ├─ TXD  → ESP32 GPIO44 (RX)
  D- ─┤ CP2102N ├─ RXD  → ESP32 GPIO43 (TX)
 VDD ─┤         ├─ DTR  → 0.1µF cap → ESP32 GPIO0
 GND ─┤         ├─ RTS  → 0.1µF cap → ESP32 EN
       └─────────┘
```

**Quick table:**
| CP2102N Pin | Goes To | Purpose |
|-------------|---------|---------|
| VDD | 3.3V | Power |
| GND | Ground | Ground |
| D+ | USB-C D+ | USB data |
| D- | USB-C D- | USB data |
| TXD | ESP32 GPIO44 (RX) | Serial transmit |
| RXD | ESP32 GPIO43 (TX) | Serial receive |
| DTR | 0.1µF → GPIO0 | Auto-program magic |
| RTS | 0.1µF → EN | Auto-reset magic |

**The "magic" auto-reset circuit:**
- DTR goes through 0.1µF capacitor to GPIO0
- RTS goes through 0.1µF capacitor to EN
- GPIO0 also has 10kΩ resistor to ground
- This lets you upload code without pressing buttons!

---

### ⚡ Power Supply

**AMS1117-3.3 connections (dead simple):**

```
       ┌──────────────┐
  5V ──┤ VIN     VOUT ├── 3.3V
       │              │
   ○ ──┤ GND      ADJ ├── ○ (not used)
       └──────────────┘

Add capacitors:
  10µF on input  (between VIN and GND)
  10µF on output (between VOUT and GND)
```

**That's it!** Super simple regulator.

---

### 🧠 ESP32-S3 Pin Summary

**ESP32-S3-WROOM-1 is a 48-pin module. Here's what we use:**

| ESP32 Pin | Function | Connects To |
|-----------|----------|-------------|
| **Power Pins** |||
| Pin 3 | 3.3V | Power input |
| Pin 46 | 3.3V | Power input |
| Pin 1 | GND | Ground |
| Pin 40, 41 | GND | Ground |
| Pad (bottom) | GND | Ground (important!) |
| **Programming** |||
| Pin 9 | EN | Reset button + RTS via cap |
| Pin 27 | GPIO0 | Boot button + DTR via cap |
| Pin 15 | GPIO43 | CP2102N RXD (serial TX) |
| Pin 16 | GPIO44 | CP2102N TXD (serial RX) |
| **Microphone (I2S)** |||
| Pin 4 | GPIO4 | INMP441 SD (data) |
| Pin 5 | GPIO5 | INMP441 WS (word select) |
| Pin 6 | GPIO6 | INMP441 SCK (clock) |
| **Display** |||
| Pin 30 | GPIO18 | TM1637 CLK |
| Pin 31 | GPIO19 | TM1637 DIO |
| **Optional LEDs** |||
| Pin 12 | GPIO38 | Power LED (+ 470Ω resistor) |
| Pin 13 | GPIO39 | Status LED (+ 470Ω resistor) |

**All other pins:** Not connected (leave floating)

---

## Step-by-Step: First Time Using EasyEDA

### Part 1: Set Up Your Account (5 minutes)

1. **Go to** https://easyeda.com
2. **Click** "Start Designing Now" (free)
3. **Sign up** with email or Google
4. **Verify** your email
5. **Done!** You're ready to design

### Part 2: Find a Reference Design (10 minutes)

1. **Go to** https://oshwlab.com/explore
2. **Search for** "ESP32-S3"
3. **Look for** a simple dev board project
4. **Click** "Open in Editor"
5. **Click** "Clone" to copy to your account

### Part 3: Understand the Interface (5 minutes)

```
EasyEDA Interface:
┌──────────────────────────────────────────────────┐
│ File Edit View ... Help             [User]       │ ← Top menu
├──────────────────────────────────────────────────┤
│ 🔧 📐 ✏️ 🔍 ...                                  │ ← Toolbar
├───────┬──────────────────────────────────────────┤
│       │                                          │
│ Parts │      Canvas (your schematic here)        │
│ Lib   │                                          │
│       │                                          │
│ LCSC  │                                          │
│       │                                          │
└───────┴──────────────────────────────────────────┘
```

**Key tools:**
- **W** = Wire (connect components)
- **P** = Place component
- **M** = Move
- **Del** = Delete
- **Ctrl+Z** = Undo (your best friend!)

### Part 4: Add Components (30 minutes)

#### Finding parts in EasyEDA:

1. **Click** "Parts" on left sidebar
2. **Click** "LCSC Components" tab
3. **Search** for part name
4. **Click** "Place" to add to schematic

**Parts to search for:**

| What You Need | Search Term | LCSC Part # |
|---------------|-------------|-------------|
| ESP32-S3 module | "ESP32-S3-WROOM-1" | C2913202 |
| Microphone | "INMP441" | C2842657 |
| Display driver | "TM1637" | C7485 |
| USB chip | "CP2102N" | C464093 |
| Voltage regulator | "AMS1117-3.3" | C6186 |
| USB-C connector | "USB-C 16pin" | C165948 |
| 10µF capacitor | "10uF 1206" | C19702 |
| 100nF capacitor | "100nF 0805" | C49678 |
| 10kΩ resistor | "10K 0805" | C17414 |
| 470Ω resistor | "470R 0805" | C17710 |

**Pro tip:** Filter by "Basic Parts" - they're cheaper to assemble!

### Part 5: Wire It Up (1 hour)

**Use this guide as reference:**
1. Place all components on schematic
2. Press **W** to start a wire
3. Click on a component pin
4. Click on another pin to connect
5. Repeat for all connections from the tables above

**Label your wires:**
- Right-click wire → "Net Label"
- Name it (e.g., "GPIO4_I2S_SD")
- Helps keep track of complex connections

**Add power symbols:**
- Press **P** → Search "VCC" → Place for 3.3V
- Press **P** → Search "GND" → Place for ground
- Connect power pins to these symbols

### Part 6: Check Your Work (15 minutes)

**Run these checks:**

1. **Visual check:**
   - [ ] All components placed?
   - [ ] All pins connected?
   - [ ] Power symbols (VCC, GND) everywhere needed?

2. **Electrical check:**
   - Click "Design" → "Design Rule Check"
   - Fix any errors (red warnings)
   - Warnings (yellow) usually OK

3. **Print check:**
   - Click "File" → "Print" → "PDF"
   - Look at printout
   - Easier to spot mistakes on paper!

### Part 7: Convert to PCB (30 minutes)

1. **Click** "Design" → "Convert to PCB"
2. **Watch** magic happen! Components appear
3. **Auto-route:**
   - Click "Auto" → "Auto Router"
   - Wait for it to connect everything
   - Usually does 95% of the work

4. **Manual fixes:**
   - Move components for better layout
   - Re-route critical traces (I2S, USB)
   - Add ground pour (fill empty space with ground)

### Part 8: Add Ground Pour (10 minutes)

**This is important for signal quality!**

1. Click **"Track"** → **"Copper Area"**
2. Click around the board edge (draw outline)
3. Double-click to finish
4. In properties: Select **"GND"** net
5. Click **"Rebuild"**
6. Repeat for bottom layer

### Part 9: Design Rule Check (5 minutes)

1. Click **"Design"** → **"DRC"**
2. Fix any errors shown
3. Common issues:
   - Traces too close
   - Traces too thin
   - Missing connections

**JLCPCB capabilities (safe values):**
- Minimum trace width: 0.15mm (use 0.2mm to be safe)
- Minimum spacing: 0.15mm (use 0.2mm to be safe)
- Minimum hole: 0.3mm

### Part 10: Order from JLCPCB (30 minutes)

1. **Click** "Fabrication" → "PCB Fabrication"
2. **Auto-fill** most settings
3. **Check these settings:**
   ```
   Layers: 2
   Size: (auto-detected)
   Quantity: 5 or 10
   Thickness: 1.6mm
   Color: Green (cheapest) or your choice
   Surface: HASL (cheapest)
   ```

4. **Enable SMT Assembly:**
   - Toggle "SMT Assembly" ON
   - Select "Top Side"
   - Confirm parts list

5. **Review BOM:**
   - Check all parts have LCSC numbers
   - Verify quantities
   - Parts without LCSC# won't be assembled!

6. **Check CPL (component positions):**
   - Preview shows where parts go
   - Fix any rotations (common issue)

7. **Add to cart**
8. **Checkout** (shipping usually $10-25)
9. **Wait 7-10 days!**

---

## What Happens Next

### Timeline:
- **Day 1:** You submit order
- **Day 1-2:** JLCPCB reviews files (they may ask questions)
- **Day 3-5:** PCB fabrication
- **Day 6-7:** Component assembly
- **Day 8:** Quality check & shipping
- **Day 10-14:** Arrives at your door!

### What You'll Receive:
- ✅ Fully assembled PCBs (5 or 10 boards)
- ✅ All components soldered
- ✅ Tested (they check for shorts)
- ✅ Packed in anti-static bag

### What You Need to Do:
1. **Visual inspection** - check for damage
2. **Plug in USB-C** cable
3. **Install drivers** (if needed)
4. **Upload code** from Nashville Numbers repo
5. **Test with guitar!**

---

## Common Mistakes to Avoid

### ❌ Schematic Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Forgot power pins | Component won't work | Every IC needs VCC and GND |
| Wrong GPIO numbers | Code won't match hardware | Double-check pin numbers |
| Missing pull-up resistors | TM1637 won't work | Add 10kΩ on CLK and DIO |
| Wrong capacitor values | Circuit unstable | Use exactly 0.1µF and 10µF |

### ❌ PCB Layout Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| I2S traces too long | Noisy audio | Keep INMP441 traces <50mm |
| No ground pour | Poor signal quality | Add copper pour on both layers |
| USB traces wrong | Connection issues | 90Ω differential pair |
| Antenna area not clear | WiFi doesn't work | 15mm keepout at ESP32 antenna |

### ❌ Ordering Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Parts not in LCSC library | Can't assemble | Use "Basic Parts" filter |
| Wrong component rotation | Upside-down parts | Check CPL preview |
| Forgot SMT assembly | Get bare board only | Enable "SMT Assembly" |
| Wrong quantity | Too few boards | Order 5-10 (price difference small) |

---

## Quick Reference Cheat Sheet

### Connections in One Table

| From Component | Pin | → | To Component | Pin | Notes |
|----------------|-----|---|--------------|-----|-------|
| **INMP441** | VDD | → | Power | 3.3V | + 100nF cap |
| | GND | → | Power | GND | |
| | SD | → | ESP32 | GPIO4 | I2S data |
| | WS | → | ESP32 | GPIO5 | I2S word select |
| | SCK | → | ESP32 | GPIO6 | I2S clock |
| | L/R | → | Power | GND | Left channel |
| **TM1637** | VCC | → | Power | 5V | Or 3.3V |
| | GND | → | Power | GND | |
| | CLK | → | ESP32 | GPIO18 | + 10kΩ pull-up |
| | DIO | → | ESP32 | GPIO19 | + 10kΩ pull-up |
| **CP2102N** | VDD | → | Power | 3.3V | |
| | GND | → | Power | GND | |
| | D+ | → | USB-C | D+ | 90Ω differential |
| | D- | → | USB-C | D- | 90Ω differential |
| | TXD | → | ESP32 | GPIO44 | Serial |
| | RXD | → | ESP32 | GPIO43 | Serial |
| | DTR | → | ESP32 | GPIO0 | Via 0.1µF cap |
| | RTS | → | ESP32 | EN | Via 0.1µF cap |
| **ESP32-S3** | Pin 3, 46 | → | Power | 3.3V | + 100nF caps |
| | Pin 1, 40, 41 | → | Power | GND | |
| **AMS1117** | VIN | → | Power | 5V | + 10µF cap |
| | GND | → | Power | GND | |
| | VOUT | → | Power | 3.3V | + 10µF cap |
| **USB-C** | VBUS | → | Power | 5V | |
| | GND | → | Power | GND | |
| | CC1, CC2 | → | Power | GND | Via 5.1kΩ |

### Capacitor Placement

```
Every IC power pin:     100nF (0.1µF) ceramic, 0805 size
AMS1117 input/output:   10µF ceramic, 1206 size
ESP32 module (×3):      100nF near pins 3, 46
INMP441:                100nF near VDD pin
CP2102N:                100nF near VDD pin
```

### Resistor Values

```
TM1637 CLK pull-up:     10kΩ (0805)
TM1637 DIO pull-up:     10kΩ (0805)
GPIO0 pull-down:        10kΩ (0805)
EN pull-up:             10kΩ (0805)
Power LED:              470Ω (0805)
Status LED:             470Ω (0805)
USB CC1/CC2:            5.1kΩ (0805)
```

---

## Help & Resources

### 🆘 Stuck? Try These:

1. **EasyEDA Tutorial Videos**
   - https://easyeda.com/page/tutorial
   - Start with "Getting Started" series

2. **ESP32-S3 Datasheet**
   - https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
   - Page 12 has pin layout diagram

3. **JLCPCB Assembly Guide**
   - https://jlcpcb.com/help/article/PCB-Assembly-FAQs
   - Answers most ordering questions

4. **Nashville Numbers Discord/Forum**
   - (Add your community link here)
   - Ask for help from other builders!

### 📧 Questions?

Open an issue on the Nashville Numbers GitHub repository with:
- Screenshot of your schematic
- Description of the problem
- What you've tried so far

We're here to help! 🎸

---

## Final Encouragement

**You can do this!**

PCB design seems scary at first, but it's really just:
1. Connect the dots (schematic)
2. Arrange the parts (layout)
3. Click "order" (manufacturing)

Thousands of beginners design their first PCB every day. With EasyEDA and JLCPCB assembly, it's easier than ever.

**Start simple:**
- Clone an existing ESP32-S3 design
- Modify it slowly
- Test each change
- Ask for help when stuck

**In 2-3 weeks you'll have:**
- ✅ A custom Nashville Numbers PCB
- ✅ New PCB design skills
- ✅ A project that costs 90% less than the Pi version
- ✅ Something you made yourself!

Good luck! 🚀🎵
