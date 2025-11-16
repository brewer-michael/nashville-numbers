# ESP32-S3 Connection Guide for Nashville Numbers

**Complete wiring reference for building a custom Nashville Numbers PCB**

---

## Quick Reference: Pin Connections

### INMP441 I2S Microphone → ESP32-S3
```
INMP441 Pin    →  ESP32-S3 Pin    Function
─────────────────────────────────────────────
VDD            →  3.3V            Power
GND            →  GND             Ground
SD (data)      →  GPIO4           I2S Data In
WS (word sel)  →  GPIO5           I2S Word Select (Left/Right)
SCK (clock)    →  GPIO6           I2S Bit Clock
L/R            →  GND             Left channel (or 3.3V for right)
```

### TM1637 4-Digit LED Display → ESP32-S3
```
TM1637 Pin     →  ESP32-S3 Pin    Function
─────────────────────────────────────────────
VCC            →  5V              Power (can also use 3.3V)
GND            →  GND             Ground
CLK            →  GPIO18          Clock signal
DIO            →  GPIO19          Data I/O signal
```

### USB-C Programming & Power
```
USB-C Pin      →  Connection      Function
─────────────────────────────────────────────
VBUS (5V)      →  5V rail         Power input
GND            →  GND             Ground
D+             →  CP2102N D+      USB data positive
D-             →  CP2102N D-      USB data negative
CC1/CC2        →  5.1kΩ to GND    USB-C resistors (pull-down)
```

### CP2102N USB-UART Bridge → ESP32-S3
```
CP2102N Pin    →  ESP32-S3 Pin    Function
─────────────────────────────────────────────
TXD            →  GPIO44 (U0RXD)  Serial transmit
RXD            →  GPIO43 (U0TXD)  Serial receive
DTR            →  GPIO0 (via cap) Auto-reset circuit
RTS            →  EN (via cap)    Auto-programming circuit
VDD            →  3.3V            Power
GND            →  GND             Ground
```

### Power Supply
```
Input: 5V from USB-C
↓
AMS1117-3.3 LDO Regulator
↓
Output: 3.3V (500mA max)
↓
Powers: ESP32-S3, INMP441, CP2102N
```

---

## Detailed Schematics

### 1. ESP32-S3-WROOM-1 Core Circuit

```
                        ┌─────────────────────────────────────┐
                        │   ESP32-S3-WROOM-1-N8 Module       │
                        │   (48-pin QFN package)             │
                        ├─────────────────────────────────────┤
                        │                                     │
     [3.3V] ────────────┤ VDD (3, 46)                        │
                        │                                     │
     [GND] ─────────────┤ GND (1, 40, 41, Pad)              │
                        │                                     │
     [EN button] ───┬───┤ EN (9)          Reset/Enable       │
                    │   │                                     │
                   10kΩ │                                     │
                    │   │                                     │
                 [3.3V] │                                     │
                        │                                     │
     [BOOT button] ─┬───┤ GPIO0 (27)      Boot mode          │
                    │   │                                     │
                   10kΩ │                                     │
                    │   │                                     │
                  [GND] │                                     │
                        │                                     │
                        │ GPIO43 (15) ────────── TX (UART0)  │
                        │ GPIO44 (16) ────────── RX (UART0)  │
                        │                                     │
                        │ GPIO4  (4)  ────────── I2S SD      │
                        │ GPIO5  (5)  ────────── I2S WS      │
                        │ GPIO6  (6)  ────────── I2S SCK     │
                        │                                     │
                        │ GPIO18 (30) ────────── TM1637 CLK  │
                        │ GPIO19 (31) ────────── TM1637 DIO  │
                        │                                     │
                        │ GPIO38 (12) ────────── LED1 (power)│
                        │ GPIO39 (13) ────────── LED2 (status)│
                        │                                     │
                        └─────────────────────────────────────┘

Decoupling capacitors (place close to module):
  - 100nF ceramic (0805) between VDD and GND (x3)
  - 10µF ceramic (1206) between VDD and GND (x1)
```

### 2. INMP441 I2S Microphone Circuit

```
     [3.3V] ──────┬─────────────────────┐
                  │                     │
                 0.1µF                  │
                  │                     │
     [GND] ───────┴─────────────────┐   │
                                    │   │
                  ┌─────────────────┼───┼──────────┐
                  │  INMP441 MEMS   │   │          │
                  │  Microphone     │   │          │
                  ├─────────────────┼───┼──────────┤
                  │                 │   │          │
                  │ VDD ────────────┘   │          │
                  │ GND ────────────────┘          │
                  │                                 │
                  │ L/R ──────────── [GND]         │
                  │                  (left channel) │
                  │                                 │
                  │ WS  ────────────────────► GPIO5 (ESP32)
                  │ SCK ────────────────────► GPIO6 (ESP32)
                  │ SD  ────────────────────► GPIO4 (ESP32)
                  │                                 │
                  └─────────────────────────────────┘

Notes:
- L/R pin: GND = left channel, VDD = right channel
- Use 100nF bypass cap close to VDD pin
- Keep I2S traces short (<2 inches ideal)
```

### 3. TM1637 LED Display Circuit

```
     [5V or 3.3V] ───────┬──────────────┐
                         │              │
                        0.1µF           │
                         │              │
     [GND] ──────────────┴──────────┐   │
                                    │   │
              ┌─────────────────────┼───┼──────┐
              │   TM1637 Driver IC  │   │      │
              │   + 4-Digit Display │   │      │
              ├─────────────────────┼───┼──────┤
              │                     │   │      │
              │ VCC ────────────────┘   │      │
              │ GND ────────────────────┘      │
              │                                │
              │ CLK ──────────┬────────► GPIO18 (ESP32)
              │               │                │
              │              10kΩ              │
              │               │                │
              │            [VCC]               │
              │                                │
              │ DIO ──────────┬────────► GPIO19 (ESP32)
              │               │                │
              │              10kΩ              │
              │               │                │
              │            [VCC]               │
              │                                │
              └────────────────────────────────┘

Notes:
- 10kΩ pull-up resistors on CLK and DIO lines
- Can use 3.3V or 5V (display is brighter at 5V)
- TM1637 is 5V tolerant on data pins
```

### 4. USB-C & CP2102N USB-UART Circuit

```
 USB-C Connector                   CP2102N                      ESP32-S3
 ┌──────────────┐                ┌──────────┐                  ┌────────┐
 │              │                │          │                  │        │
 │ VBUS (5V) ───┼────────┬───────┤ VDD      │                  │        │
 │              │        │       │          │                  │        │
 │ GND ─────────┼────────┼───────┤ GND      │                  │        │
 │              │        │       │          │                  │        │
 │ D+ ──────────┼────────────────┤ D+       │                  │        │
 │              │                │          │                  │        │
 │ D- ──────────┼────────────────┤ D-       │                  │        │
 │              │                │          │                  │        │
 │ CC1 ─────────┼───┬            │          │                  │        │
 │              │   │            │          │                  │        │
 │ CC2 ─────────┼───┤            │          │                  │        │
 │              │   │            │          │                  │        │
 └──────────────┘   │            │ TXD ─────┼──────────────────┤ GPIO44 │
                    │            │          │                  │ (RX)   │
                  5.1kΩ          │ RXD ─────┼──────────────────┤ GPIO43 │
                    │            │          │                  │ (TX)   │
                  [GND]          │          │                  │        │
                                 │ DTR ─────┼────┬──┬──────────┤ GPIO0  │
        [5V] ───────┬────────────┤ 3V3OUT   │    │  │          │        │
                    │            │          │   0.1µF          │        │
                   0.1µF         │ RTS ─────┼────┼──┼──┬───────┤ EN     │
                    │            │          │    │  │  │       │        │
                  [GND]          └──────────┘    │  │ 0.1µF    └────────┘
                                                 │  │  │
                                               [GND] │ [GND]
                                                    │
                                                  10kΩ
                                                    │
                                                  [GND]

Auto-reset circuit:
- DTR → 0.1µF → GPIO0 (BOOT pin)
- RTS → 0.1µF → EN (ENABLE pin)
- GPIO0 pulled down via 10kΩ resistor
- Allows automatic programming without pressing buttons
```

### 5. Power Supply Circuit

```
USB 5V Input                AMS1117-3.3                3.3V Output
     │                      ┌────────┐                     │
     │                      │        │                     │
     ├──────────┬───────────┤ VIN  VOUT├─────┬─────────────┤
     │          │           │        │      │             │
     │         10µF         │  GND   │     10µF          100nF (×4)
     │      (1206)          │        │   (1206)         (0805)
     │          │           └────┬───┘      │             │
     │          │                │          │             │
  ───┴──────────┴────────────────┴──────────┴─────────────┴───
                              GND Plane

Input Protection (optional):
  - Polyfuse (500mA or 1A) on 5V line
  - Schottky diode for reverse protection
  - TVS diode for ESD protection

Current consumption estimates:
  - ESP32-S3 active:      80-160mA
  - ESP32-S3 WiFi on:     +80-120mA
  - INMP441:              1.4mA
  - TM1637 + display:     20-80mA
  - CP2102N:              10mA
  - Total typical:        ~120-270mA
  - Total max (WiFi on):  ~350mA
```

### 6. LED Indicators & Buttons

```
Power LED (optional):
     [3.3V] ─────┬
                 │
               470Ω
                 │
             LED (red, 0805)
                 │
     [GND] ──────┴

Status LED (GPIO39):
     [GPIO39] ───┬
                 │
               470Ω
                 │
             LED (blue, 0805)
                 │
     [GND] ──────┴

BOOT Button:
     [GPIO0] ────┬──── [BOOT button] ──── [GND]
                 │
               10kΩ
                 │
              [3.3V]

RESET Button:
     [EN] ───────┬──── [RESET button] ─── [GND]
                 │
               10kΩ
                 │
              [3.3V]
```

---

## PCB Layout Guidelines

### Component Placement Priority

```
Layer Stack (2-layer PCB):
  Top Layer:    Signal + Components
  Bottom Layer: Ground plane + Power traces

Placement order (top view):
┌─────────────────────────────────────────────────┐
│  [USB-C]                          [INMP441 Mic] │
│                                                  │
│  [CP2102N]    [ESP32-S3-WROOM-1]    [TM1637]   │
│                                                  │
│  [LDO]        [10µF caps]           [Display]   │
│                                                  │
│  [BOOT] [RST] [Power LED] [Status LED]         │
└─────────────────────────────────────────────────┘
            70mm × 50mm board
```

### Critical Design Rules

#### 1. **Ground Plane**
- Bottom layer = solid ground pour
- Top layer = ground fill where space allows
- Multiple vias connecting top/bottom ground (every 5-10mm)

#### 2. **Power Distribution**
```
5V power trace:  ≥0.5mm width (16mil)
3.3V power:      ≥0.4mm width (16mil)
Signal traces:   ≥0.2mm width (8mil)
Minimum spacing: ≥0.2mm (8mil)
```

#### 3. **I2S Audio Traces** (CRITICAL!)
```
INMP441 → ESP32-S3:
  - Keep traces short (<30mm ideal, <50mm max)
  - Route on top layer
  - Keep parallel spacing ≥3× trace width
  - Run over solid ground plane
  - Add ground vias at start/end of traces
  - NO 90° angles (use 45° or curved)

Signal integrity:
  SD, WS, SCK should be:
    - Same length ±5mm
    - Not cross split in ground plane
    - Away from switching power supply
```

#### 4. **USB Differential Pairs** (D+/D-)
```
Impedance: 90Ω differential
  - Trace width: 0.3mm (12mil)
  - Spacing: 0.3mm (12mil)
  - Keep equal length ±1mm
  - Route together (coupled)
  - Minimum bend radius: 3× trace width
  - NO vias if possible
```

#### 5. **Decoupling Capacitors**
```
ESP32-S3 module:
  - 100nF ceramic as close as possible to VDD pins
  - Place on same side as module
  - Via to ground plane immediately next to GND pin

General rule:
  - Every IC gets a 100nF cap (VDD to GND)
  - Place within 5mm of the IC power pin
  - Short, wide traces to power pins
```

#### 6. **Module Mounting**
```
ESP32-S3-WROOM-1:
  - Center pad MUST connect to GND with multiple vias
  - Thermal relief not required (better ground connection)
  - RF antenna area: keep clear (no copper, no traces)
  - 15mm keepout zone at antenna end
```

### Example Trace Widths (1oz copper)

| Current | Temp Rise | Trace Width | Use Case |
|---------|-----------|-------------|----------|
| 100mA   | 10°C      | 0.15mm (6mil) | Signals |
| 300mA   | 10°C      | 0.4mm (16mil) | 3.3V power |
| 500mA   | 10°C      | 0.6mm (24mil) | 5V input |
| 1A      | 10°C      | 1.0mm (40mil) | High current |

---

## Manufacturing Files Checklist

When ordering from JLCPCB, you need:

### 1. **Gerber Files** (PCB fabrication)
```
Required layers:
  ✓ Top Copper (GTL)
  ✓ Bottom Copper (GBL)
  ✓ Top Silkscreen (GTO)
  ✓ Bottom Silkscreen (GBO)
  ✓ Top Soldermask (GTS)
  ✓ Bottom Soldermask (GBS)
  ✓ Board Outline (GKO or GML)
  ✓ Drill file (TXT or DRL)
```

### 2. **BOM (Bill of Materials)**
```
Excel/CSV format with columns:
  - Comment (part value, e.g., "10uF")
  - Designator (e.g., "C1, C2")
  - Footprint (e.g., "1206")
  - LCSC Part # (e.g., "C19702")
```

### 3. **Pick-and-Place File (CPL)**
```
CSV format with columns:
  - Designator
  - Mid X (mm)
  - Mid Y (mm)
  - Layer (Top/Bottom)
  - Rotation (degrees)
```

**EasyEDA exports all of these automatically!**

---

## Pin Assignment Summary

### ESP32-S3 GPIO Allocation

| GPIO | Function | Connected To | Notes |
|------|----------|--------------|-------|
| **GPIO0** | Boot Mode | BOOT button + CP2102N DTR | Pulled up to 3.3V |
| **GPIO43** | UART0 TX | CP2102N RXD | Serial output |
| **GPIO44** | UART0 RX | CP2102N TXD | Serial input |
| **GPIO4** | I2S SD | INMP441 SD | I2S data in |
| **GPIO5** | I2S WS | INMP441 WS | I2S word select |
| **GPIO6** | I2S SCK | INMP441 SCK | I2S clock |
| **GPIO18** | TM1637 CLK | Display CLK | Display clock |
| **GPIO19** | TM1637 DIO | Display DIO | Display data |
| **GPIO38** | LED | Power indicator | Optional |
| **GPIO39** | LED | Status indicator | Optional |
| **EN** | Enable | RESET button + CP2102N RTS | Module enable |

**Available for expansion:**
- GPIO1, GPIO2, GPIO3, GPIO7, GPIO8, GPIO9, GPIO10, GPIO11
- GPIO12, GPIO13, GPIO14, GPIO15, GPIO16, GPIO17, GPIO21
- GPIO35, GPIO36, GPIO37, GPIO40, GPIO41, GPIO42, GPIO45, GPIO46, GPIO47, GPIO48

**Strapping pins** (use with caution):
- GPIO0: Boot mode (pulled up)
- GPIO45: VDD_SPI voltage select
- GPIO46: ROM boot mode

---

## Testing Plan

### Bring-Up Checklist (After Assembly)

#### 1. **Visual Inspection**
- [ ] No solder bridges between pins
- [ ] All components oriented correctly
- [ ] USB-C connector properly aligned
- [ ] No cold solder joints

#### 2. **Power-On Tests** (no USB connection yet)
- [ ] Check 3.3V output from LDO (should be 0V, no power)
- [ ] Check for shorts between 5V and GND (should be open)
- [ ] Check for shorts between 3.3V and GND (should be open)

#### 3. **USB Connection Tests**
- [ ] Connect USB-C cable
- [ ] Measure 5V on USB VBUS pin
- [ ] Measure 3.3V on LDO output (~3.3V ±0.1V)
- [ ] Check current draw (<50mA at idle)
- [ ] CP2102N enumeration (check Device Manager / lsusb)

#### 4. **Programming Test**
- [ ] Install ESP32-S3 drivers (if needed)
- [ ] Open Arduino IDE or ESP-IDF
- [ ] Select board: "ESP32-S3 Dev Module"
- [ ] Upload blink sketch
- [ ] Verify status LED blinks

#### 5. **Peripheral Tests**
```cpp
// Test 1: I2S Microphone
// Upload code to read I2S samples
// Should see non-zero audio values

// Test 2: TM1637 Display
// Upload TM1637 library example
// Display should show numbers

// Test 3: Full chord detection
// Upload Nashville Numbers code
// Test with guitar/audio input
```

---

## Troubleshooting Guide

### Common Issues

| Problem | Possible Cause | Solution |
|---------|----------------|----------|
| **Board not detected** | CP2102N not enumerated | Check USB-C connection, install drivers |
| | Bad solder joints | Reflow CP2102N pins |
| | 3.3V missing | Check LDO regulator |
| **Upload fails** | Auto-reset not working | Manually press BOOT + RESET |
| | Wrong COM port | Check Device Manager |
| | GPIO0 not pulled down | Check 0.1µF cap on DTR line |
| **No 3.3V output** | LDO failure | Check input 5V, replace AMS1117 |
| | Short circuit | Find short with multimeter |
| **INMP441 no audio** | Wrong I2S pins | Verify GPIO4/5/6 connections |
| | L/R pin floating | Connect to GND or VDD |
| | Bad solder joint | Reflow INMP441 pins |
| **Display not working** | Wrong GPIO pins | Verify GPIO18/19 |
| | Missing pull-ups | Add 10kΩ resistors |
| | TM1637 damaged | Test with multimeter |
| **High current draw** | Short circuit | Check all power rails |
| | WiFi enabled | Disable WiFi in software |

---

## Next Steps

1. **Learn EasyEDA basics** - Watch tutorial videos (30 min)
2. **Clone reference design** - Find ESP32-S3 project on OSHWLab
3. **Modify schematic** - Add INMP441 and TM1637 per this guide
4. **Convert to PCB** - Let EasyEDA auto-route
5. **Manual optimization** - Improve I2S traces, add ground pour
6. **DRC check** - Run Design Rule Check in EasyEDA
7. **Export files** - Generate Gerber, BOM, CPL
8. **Order from JLCPCB** - Upload files, select PCBA service
9. **Wait 7-10 days** - Manufacturing and shipping
10. **Test and validate** - Follow testing plan above

---

## Additional Resources

### Datasheets
- [ESP32-S3-WROOM-1 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [INMP441 Datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf)
- [TM1637 Datasheet](https://www.mcielectronics.cl/website_MCI/static/documents/Datasheet_TM1637.pdf)
- [CP2102N Datasheet](https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf)

### Software Libraries
- [ESP32-audioI2S](https://github.com/schreibfaul1/ESP32-audioI2S) - Audio library
- [ESP-DSP](https://github.com/espressif/esp-dsp) - Official FFT library
- [TM1637Display](https://github.com/avishorp/TM1637) - Arduino library
- [ESP32 I2S Examples](https://github.com/espressif/esp-idf/tree/master/examples/peripherals/i2s)

### Tutorials
- [ESP32-S3 Getting Started](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/)
- [EasyEDA Tutorial Series](https://easyeda.com/page/tutorial)
- [JLCPCB Assembly Tutorial](https://jlcpcb.com/help/article/PCB-Assembly-FAQs)

---

**Questions?** Open an issue on the Nashville Numbers repository!
