# Hardware

Everything needed to build a Nashville Numbers unit.

| | |
|---|---|
| [`SPEC.md`](SPEC.md) | design spec: parts, pin map, electrical rules, mechanical rules - the single source of truth |
| [`bom/`](bom/README.md) | bills of materials per build, with quantities and approximate prices, and a shopping checklist with store links |
| [`wiring/`](wiring/README.md) | wiring diagrams, pin-by-pin tables, soldering and bring-up tests |
| [`enclosures/`](enclosures/README.md) | 3D-printable enclosures (OpenSCAD source, ready STLs, print and assembly guide) |

## Pick a build

| Build | Display | Enclosure | Best for |
|---|---|---|---|
| **Desktop** | 16x2 character LCD: number, chord, key and the progression so far | desktop LCD case | practice room, lessons, music stand |
| **Stage** | 1.2" red 7-segment digits (30 mm tall), readable from standing height | floor wedge with footswitch jack | gigs, rehearsals, jams |
| **Budget** | 0.56" red 7-segment (TM1637) | floor wedge | lowest cost |

Approximate parts cost in US dollars, including a USB audio interface
([BOM](bom/README.md)):
<!-- BEGIN GENERATED: bom totals -->
Desktop about $131 / Stage about $146 / Budget about $124
<!-- END GENERATED: bom totals -->

Every build uses the same computer and audio chain: a **Raspberry Pi 5** or
**Raspberry Pi 4** (1 GB is plenty for either), its official power supply, a
USB audio interface, and one panel button. The same software runs all of
them; only `display.type` in the config differs.

## Build order

1. **Order the parts** from the [BOM](bom/README.md) for your build.
2. **Install the software** on the Pi and check it with `--simulate --demo`
   ([Installation](../docs/INSTALLATION.md)).
3. **Wire on the bench** following [`wiring/`](wiring/README.md), power off.
   Check with `i2cdetect -y 1` and `nashville-numbers --test-display`.
4. **Check the audio** with `nashville-numbers --test-audio`.
5. **Print the enclosure** ([`enclosures/`](enclosures/README.md)) while you
   test; install the heat-set inserts.
6. **Assemble**, then run `--test-display` once more before closing the case.
7. **Gig-proof it** (optional): enable the read-only overlay file system
   ([Installation §6](../docs/INSTALLATION.md#6-make-it-gig-proof-optional-recommended-for-stage-use)).

## Electrical rules that matter

* Raspberry Pi GPIO pins are **3.3 V only**. The LCD runs on 5 V, so its I2C
  lines go through the BSS138 level shifter; the TM1637 module is powered
  from 3.3 V because its pull-ups go to its supply; the MAX7219 is driven
  through a 74AHCT125.
* **5 V (pins 2 and 4) sits next to 3.3 V (pin 1) and GPIO2 (pin 3).**
  Power off while wiring and count pins twice.
* On a **Pi 5**, use the official 27 W supply, or USB ports (and the audio
  interface) are limited to 600 mA in total.
