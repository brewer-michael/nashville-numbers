# Nashville Numbers — Hardware Design Spec (v2)

This is the single source of truth for the v2 hardware: which parts are used,
how they are wired, and the mechanical rules the enclosures follow. The
software defaults (`src/nashville_numbers/config.py`), the wiring diagrams
(`hardware/wiring/`), the BOM (`hardware/bom/`) and the OpenSCAD enclosures
(`hardware/enclosures/`) all follow this document. If you change something
here, change it there too.

All dimensions are millimetres. Pin numbers are **physical header pins**;
GPIO numbers are **BCM**.

---

## 1. System overview

```
 instrument / mixer aux / mic
            │  (line, Hi-Z or mic level)
            ▼
   USB audio interface (class compliant)
            │  USB
            ▼
   Raspberry Pi 5 (1 GB+)  or  Raspberry Pi 4 (1 GB+)
     │  I2C / GPIO (40-pin header)
     ├──► display  (one of: 16x2 LCD · 1.2" HT16K33 7-seg · TM1637 7-seg · MAX7219)
     ├──◄ panel button          (GPIO17)
     └──◄ footswitch jack, TS   (GPIO27)   [stage wedge builds]
```

Three reference builds:

| Build | Display | Enclosure | Use |
|---|---|---|---|
| **Desktop** | 16x2 character LCD, PCF8574 I2C backpack + BSS138 level shifter | `desktop_lcd_case.scad` | practice room, music stand, desk |
| **Stage** | Adafruit 1.2" 4-digit 7-segment, HT16K33 I2C backpack (red) | `stage_wedge.scad` | floor wedge at the performer's feet |
| **Budget** | TM1637 4-digit 7-segment module, 0.56" (or 0.36"), red | `stage_wedge.scad` with `display = "tm1637_056"` | lowest cost |

The footswitch jack is part of the Stage build and optional on the Budget
build (both use the stage wedge, which has the jack hole).

MAX7219 8-digit modules remain supported in software (needs a 74AHCT125 level
shifter, see §3.4) but have no dedicated enclosure.

## 2. Computer

| | Raspberry Pi 5 | Raspberry Pi 4 Model B | Raspberry Pi 3B+ |
|---|---|---|---|
| Status | recommended | recommended | works, slower |
| RAM needed | 1 GB is plenty (the app uses ≈ 60 MB) | 1 GB is plenty | 1 GB |
| PSU | **official 27 W 5.1 V/5 A USB-C** (a 3 A supply caps USB at 600 mA total) | official 15 W 5.1 V/3 A USB-C | 5.1 V/2.5 A micro-USB |
| Cooling in a closed case | official Active Cooler (recommended) | stick-on heatsink | stick-on heatsink |
| GPIO library | gpiozero + lgpio (RPi.GPIO does **not** work on Pi 5) | gpiozero + lgpio | gpiozero |

Common mechanical data (Pi 4 and Pi 5 share it):

* Board 85.0 × 56.0, corner radius 3.0, PCB ≈1.4 thick.
* Mounting holes Ø2.7 at (3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5);
  keep-out pads Ø6.0 around each hole (standoffs must be ≤ Ø6.0).
* Board coordinate system used everywhere in this repo: origin at the corner
  with the microSD edge (x = 0) and the power/HDMI edge (y = 0). The USB/Ethernet
  edge is x = 85, the GPIO header edge is y = 56. z = 0 is the PCB top surface.
* GPIO header: 2×20, pitch 2.54, row centreline y = 52.5, centred on x = 32.5.
  Pin 1 at (8.37, 51.23); even pins (2, 4, 6 …) are the outer row (y = 53.77).
  Header pins reach z = +8.5. **Dupont jumpers on the header need z ≤ +22 free
  above the header footprint** (housing + bend radius).
* Short edge x = 85: USB and Ethernet occupy y ≈ 1…55, up to z ≈ +16, and
  protrude ≈ 3 past the board edge. Pi 4 has Ethernet at the GPIO side
  (y ≈ 45.75); Pi 5 (and 3B+) has Ethernet at the power side (y ≈ 10.2). Design
  one opening that clears **both** layouts.
* Long edge y = 0: USB-C power centre x ≈ 11.2; micro-HDMI centres x ≈ 26.0 and
  39.5 (Pi 5: 25.8, 39.2); Pi 4 3.5 mm audio jack at x ≈ 54.0 (none on Pi 5).
  Connectors sit at z ≈ 0…+3.5 (audio jack to +6) and protrude ≈ 1–2.5 past the
  edge. Plug overmolds need clearance ≈ 12 × 8 (USB-C, micro-HDMI) around the
  connector centre where they pass through the wall.
* microSD: underside at x = 0, centred y ≈ 28, protrudes ≈ 2.5 past the edge,
  z ≈ −1.4…−3.
* Underside components need ≥ 3 of clearance; use 5 standoffs.
* Heatsink/cooler keep-out above the SoC: Pi 4 heatsink ≈ 15 × 15 × 10 around
  (x 22…37, y 24…39); Pi 5 Active Cooler ≈ 60 × 40 footprint, 16 tall incl. air
  gap, over x 3…63, y 12…52 (it sits next to the header; its fan pulls air
  from above, so leave vents over it).

These positions come from the official mechanical drawings but are rounded;
the enclosures use generous openings (≥ 2 clearance per side) so ±1 errors do
not matter.

## 3. Electrical design

### 3.1 Pin map (BCM GPIO)

| Function | GPIO | Header pin | Notes |
|---|---|---|---|
| 3.3 V | – | 1, 17 | logic supply for 3.3 V parts |
| 5 V | – | 2, 4 | direct from the PSU |
| GND | – | 6, 9, 14, 20, 25, 30, 34, 39 | |
| I2C1 SDA | 2 | 3 | LCD (via level shifter), HT16K33 |
| I2C1 SCL | 3 | 5 | LCD (via level shifter), HT16K33 |
| Panel button | 17 | 11 | to GND (pin 9); internal pull-up |
| Footswitch jack tip | 27 | 13 | via 1 kΩ series resistor + 100 nF to GND; sleeve to GND (pin 14) |
| TM1637 CLK | 23 | 16 | |
| TM1637 DIO | 24 | 18 | |
| SPI0 MOSI → MAX7219 DIN | 10 | 19 | via 74AHCT125 |
| SPI0 SCLK → MAX7219 CLK | 11 | 23 | via 74AHCT125 |
| SPI0 CE0 → MAX7219 CS | 8 | 24 | via 74AHCT125 |

The Pi's GPIO pins are **3.3 V only**. Every 5 V device below is connected
so that no pull-up resistor can drag a GPIO pin above 3.3 V.

### 3.2 Desktop: 16x2 LCD (HD44780 + PCF8574 backpack)

* LCD VCC = **5 V** (pin 2). The HD44780 contrast and backlight need 5 V.
* The backpack has 4.7 kΩ pull-ups to its VCC, so its SDA/SCL float at 5 V.
  Connect it through a **BSS138 bidirectional level shifter** (Adafruit 757 or
  the generic 4-channel "I2C-safe" board): LV = 3.3 V (pin 1), HV = 5 V (pin 4),
  both GND pins to GND.
* I2C address 0x27 (PCF8574T) or 0x3F (PCF8574AT). Adafruit's own LCD backpack
  uses an MCP23008 instead (address 0x20); set `display.lcd.expander`.
* Most cheap modules use the Hitachi A00 character ROM (`charmap: "A00"`).

### 3.3 Stage: Adafruit 1.2" 7-segment + HT16K33 backpack

* Backpack pins: `IO` → 3.3 V (pin 1) — this sets the I2C pull-up level;
  `+` → 5 V (pin 4) — LED power (boards since 2023 have a boost converter and
  also work from 3.3 V); `−` → GND; `D` → SDA; `C` → SCL. Address 0x70.
* Assembled module ≈ 120 × 50 × 13. The 1.2" digits are ≈ 30 tall; a red
  acrylic filter in front of the digits improves contrast under stage lights.
* HT16K33 RAM layout for this backpack: digits at byte addresses 0x00, 0x02,
  0x06, 0x08; colon at 0x04. Segment bits: 0 = A … 6 = G, 7 = DP.

### 3.4 Budget: TM1637 module; legacy MAX7219

* TM1637 modules carry 10 kΩ pull-ups to their VCC, so **power them from
  3.3 V (pin 17), never 5 V**. Red digits are bright enough at 3.3 V; blue and
  white are not.
* Body sizes: 0.36" 4-digit display 30.1 × 14.0 (module PCB 42 × 24, 4× Ø2.2
  holes); 0.56" 4-digit display 50.3 × 19.0 (module PCB ≈ 50.5 × 25, varies by
  vendor). Measure your module.
* The driver bit-bangs the TM1637 protocol with open-drain emulation (the Pi
  never drives DIO high and releases it for the ACK bit).
* MAX7219 is a 5 V part whose logic-high threshold is 3.5 V. Buffer DIN, CLK
  and CS through a 74AHCT125 powered from 5 V (its inputs accept 3.3 V
  logic). Tie the unused buffer's input to GND and all four OE pins to GND.
  Decouple the 74AHCT125 with 100 nF across VCC and GND (pins 14 and 7).

### 3.5 Controls

* **Panel button** — 16 mm (or 12 mm) momentary, normally-open, between GPIO17
  and GND. Short press: new song (reset key and chord history). Hold 1.5 s:
  lock/unlock the current key. Hold 6 s: safe shutdown.
* **Footswitch jack** (stage wedge builds) — 1/4" (6.35 mm) mono TS jack.
  Tip → R1 1 kΩ → GPIO27, sleeve → GND, and C1 100 nF (ceramic) from the
  GPIO27 side of R1 to GND, soldered at the jack. The Pi's internal pull-up
  holds the line high. R1 limits current if someone plugs in a live
  instrument or line cable; R1 + C1 filter noise picked up on long stage
  cables. Works with any momentary footswitch (Boss FS-5U, a keyboard sustain
  pedal, …); the software learns the pedal polarity at start-up.

### 3.6 Power budget

| Load | Current |
|---|---|
| Pi 5 running the app | ≈ 0.6–1.0 A |
| Pi 4 running the app | ≈ 0.6–0.9 A |
| USB audio interface | 0.1–0.5 A |
| LCD + backlight | ≈ 0.03 A |
| HT16K33 1.2" at full brightness | ≤ 0.2 A |
| TM1637 at 3.3 V | ≤ 0.08 A |
| MAX7219 8-digit at full brightness | ≤ 0.3 A |

The official PSUs cover every build with margin.

## 4. Audio input

Any USB class-compliant interface works (no drivers on Raspberry Pi OS).
Choose by source:

| Source | Interface type | Example |
|---|---|---|
| mixer aux send, keyboard, pedalboard output | line in (RCA / 1/4") | Behringer UCA202 / UCA222 |
| electric guitar or bass, directly | Hi-Z instrument input | Behringer UM2, UMC22, UCG102 |
| acoustic instrument or the whole band | mic preamp + mic, or a USB mic | UM2 + dynamic mic, any USB mic |

A direct, clean signal (line or DI) gives far better chord detection than a
room mic.

## 5. Mechanical rules for the enclosures

### 5.1 General

* Units mm, OpenSCAD 2021.01 compatible (no newer-only features). Fonts:
  "Liberation Sans" (bundled with OpenSCAD).
* Every printable part is exported in its print orientation (resting on
  z = 0), fits a **180 × 180 × 180** print volume and prints **without
  supports**.
* Overhangs ≤ 45° from vertical. Bridges ≤ 15, except over the shallow
  recesses on the underside of the base (bumpers, hook-and-loop), where a
  sagging bridge is invisible.
* Material: PETG for the floor wedge, PLA or PETG for the desktop case.
* Clearance parameters: `tol = 0.2` (holes, pockets), `fit = 0.3` (part-to-part).

### 5.2 Construction pattern (both enclosures)

* **Base plate** (`base_t` = 3): flat plate that carries the Pi on 4
  standoffs (Ø6.0 × 5 tall, Ø2.2 × 7 deep pilots for **M2.5 × 8** screws,
  self-tapping or machine screws cut into the plastic). Printed flat.
* **Shell**: four walls and the sloped display face in one piece, printed
  **face-down** (the face on the bed). The side walls then stand vertical and
  the front and back walls lean by the face angle (≤ 30°), so nothing needs
  support.
* The base plate drops into the shell's open bottom (`fit` clearance) and is
  held by **3 × M3 × 8 screws** (6 to 10 long work) through counterbored holes
  in the base (Ø3.4, head recess Ø6.2 × 2) into **M3 heat-set inserts** (hole
  Ø4.0 × 6.0, plus Ø3.4 × 4 beyond it for the screw tip) in corner posts of
  the shell (Ø9 desktop, Ø10 stage, merged into the walls). Posts sit in the
  front-left, front-right and back-right corners; the back-left corner holds
  the Pi's USB/Ethernet end. `closure = "selftap"` replaces the insert holes
  with Ø2.6 × 10 pilots for M3 thread-forming screws.
* The Pi sits in the back-left corner, USB/Ethernet edge against the left
  wall, power/HDMI edge against the back wall. Its port openings are
  **U-notches open to the bottom rim** (the Pi rises into the shell on the
  base plate): left wall 55.6 wide up to the plug tops, back wall 55.3 wide
  for USB-C, both micro-HDMI and the Pi 4 audio jack. The microSD card is
  inside; flash it before assembly.
* **Display clamp tabs**: a display module is held against the face by small
  printed tabs (10 wide, 3.2 thick) screwed with M2.5 × 8 into Ø7 bosses
  beside the module; each tab presses 3.5 onto the module's back. The bosses
  stop 0.3 short of the module back so the tabs clamp. This works whatever a
  module's own mounting holes are. Tabs sit where the module has no wiring:
  desktop 3 (bottom-left, bottom-right, top edge right of the 16-pin header),
  1.2-inch 7-segment 4 (long edges), TM1637 2 (long edges).
* 4 recesses Ø13.5 × 0.8 on the base underside for adhesive rubber bumpers
  (Ø12.7). The stage base also has two 25 × 60 × 0.8 recesses for
  hook-and-loop / Dual Lock (pedalboard mounting).
* Vents: slots 2.4 wide. Intake low on the front and right walls, exhaust
  through the face above the Pi (over the Pi 5 Active Cooler), and slots in
  the base under the Pi.
* Holes in walls that print vertical are truncated teardrops pointing up in
  the print orientation, clipped so the nut or button bezel still covers
  them.

### 5.3 Desktop LCD enclosure (`desktop_lcd_case.scad`)

* Holds: Pi 4 or Pi 5, 16x2 LCD with PCF8574 backpack, BSS138 level shifter,
  one 16 mm button.
* Outside 125 × 82, 38 tall at the front, 85 at the back; face tilted **30°**
  from horizontal; walls 2.5, face 3.
* LCD module: PCB 80 × 36 × 1.6; bezel 71.2 × 24.2 × 7.0 centred on the PCB;
  viewing area 64.5 × 14.5 (window 66.0 × 16.5); backpack 41.6 × 19.1 × 11;
  its 4-pin I2C header points sideways out of one end and the Dupont
  jumpers there need about 20 of free space beyond the LCD PCB edge on
  either side (parameter `lcd_header_side`, default: room on both sides).
  The LCD is centred across the face, 28 up the slope, located by a 1.5 high
  ridge around the bezel.
* Level shifter board ≤ 21 × 17 (jumpers stand ≈ 15 above it): foam-taped to
  the base plate inside a locating ridge at the front right.
* 16 mm button in the right side wall: panel hole Ø16.2, flat Ø22 inside for
  the nut, 35 of depth behind the panel.

### 5.4 Stage wedge enclosure (`stage_wedge.scad`)

* Holds: Pi 4 or Pi 5, display (`display = "ht16k33_12"` default,
  `"tm1637_056"`, `"tm1637_036"`), 16 mm button, 1/4" footswitch jack (R1/C1
  soldered on its lugs).
* Outside 142 × 108, 42 tall at the front, 92 at the back; walls 3, face 4.
* Face tilted **25°** from horizontal. From a standing player 1 to 2 m away
  the line of sight is 40° to 60° below horizontal, so the face is within
  about 25° of head-on, and LED digits read well far beyond that. A steeper
  face would make the wedge much taller for little gain.
* Display centred across the face, 34 up the slope. Window = the module's
  digit area (1.2-inch: 110 × 40); behind it a 2 deep pocket for a 2 mm red
  acrylic filter overlapping the window by 3 all round (1.2-inch filter
  116 × 46, 0.56-inch 54 × 23, 0.36-inch 35 × 19); the filter outline is
  exported as DXF (laser) and 1:1 SVG (hand-cutting). The module presses the
  filter into the pocket.
* A 2.4 rib stiffens the face above the display window.
* Button on the face, back right; 1/4" TS jack in the back wall right of
  the Pi's port notch (hole Ø9.6); outside, the jack needs a Ø15 × 42 keep-out
  for the plug.
* Must survive being kicked: walls 3, face 4, ribbed. It is not designed to
  be stood on.
* All cables (USB-C power, USB audio, footswitch) leave the back or the
  left side, never the front.

### 5.5 Verification (CI)

`hardware/enclosures/tools/check_cad.py` must pass:

1. Every exported part is watertight and a single connected body (the clamp
   tab files: one body per tab).
2. Every part fits the 180 × 180 × 180 print volume and rests on z = 0.
3. Assembled, no printed part intersects the ghost models of the parts the
   enclosure holds and the space they need: Pi 4 **and** Pi 5 with cooler,
   underside parts, ports and the plugs in them, Dupont jumpers on the GPIO
   header; the display module, its backpack and wiring; level shifter,
   button, jack and footswitch plug.
4. The printed parts do not intersect each other when assembled.
