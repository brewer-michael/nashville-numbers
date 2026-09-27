# Bills of materials

One complete parts list per build, each with quantities, a specification and
an example part. Every build shares the same computer, audio chain and
button; they differ in the display, the enclosure and the footswitch.

<!-- BEGIN GENERATED: summary -->
| Build | Parts, approx. USD | With optional parts | CSV |
|---|---:|---:|---|
| Desktop (16x2 LCD, desktop case) | 131 | 131 | [`desktop.csv`](desktop.csv) |
| Stage (Adafruit 1.2" 7-segment, floor wedge, footswitch) | 146 | 173 | [`stage.csv`](stage.csv) |
| Budget (TM1637 0.56" 7-segment, floor wedge) | 124 | 159 | [`budget.csv`](budget.csv) |
<!-- END GENERATED: summary -->

Prices are rough US street prices (September 2026) for budgeting, not quotes,
and include the USB audio interface (about $30), which you can skip if you
already own a class-compliant one. Raspberry Pi raised the prices of its 2 GB
and larger boards in 2026 because of memory costs; the 1 GB boards kept
theirs, and 1 GB is plenty (the app uses about 60 MB).

The CSV files are the full lists for ordering. The tables below are the same
lists in short form.

## Shopping checklist

[`checklist.html`](checklist.html) is the same parts list as a page to shop
from: pick your build, follow the links to real store listings, and tick
each part off as you get it. Open it in a browser from a clone (GitHub shows
its source, not the page); your ticks are kept in that browser. It also lists
the tools you need.

Its prices are what each listing costs, and small parts only come in packs,
so a first build costs more there than in the tables below (the Desktop build
is about $212 to buy against $131 per unit). The difference is spares, and
it shrinks as you tick off things you already own.

## Desktop

<!-- BEGIN GENERATED: desktop parts -->
| Qty | Part | Example | Approx. USD |
|---:|---|---|---:|
| 1 | Raspberry Pi 5, 1 GB | Raspberry Pi approved resellers | 45.00 |
| 1 | Power supply | Raspberry Pi 27 W USB-C power supply | 12.00 |
| 1 | Cooler | Raspberry Pi Active Cooler | 5.00 |
| 1 | microSD card | Raspberry Pi 32 GB card, SanDisk, Samsung | 8.00 |
| 1 | USB audio interface | Behringer UCA222 (line in) | 30.00 |
| 1 | Input cable | for the UCA222: 1/4-inch TS to 2x RCA | 6.00 |
| 1 | 16x2 character LCD with I2C backpack | generic "LCD1602 I2C" module | 7.00 |
| 1 | I2C level shifter | Adafruit 757 or generic "I2C-safe" 4-channel board | 4.00 |
| 1 | Push button, 16 mm, momentary | metal 16 mm momentary button with solder lugs or screw terminals | 3.00 |
| 1 | Dupont jumper wires F-F, 20 cm | any 40-way F-F 20 cm jumper ribbon | 5.00 |
| 1 | Heat-shrink tubing | share of an assortment | 1.00 |
| 1 | Solder | any | - |
| 130 | Filament, grams | any 1.75 mm filament | 2.60 |
| 3 | Heat-set insert M3 | CNC Kitchen or Ruthex M3 x 5.7 | 0.30 |
| 3 | Screw M3 x 8 | any | 0.30 |
| 7 | Screw M2.5 x 8 | any | 0.70 |
| 4 | Rubber bumpers | any | 0.60 |
| 1 | Double-sided foam tape | any mounting tape | 0.20 |
| | **Total** | | **131** |
<!-- END GENERATED: desktop parts -->

## Stage

<!-- BEGIN GENERATED: stage parts -->
| Qty | Part | Example | Approx. USD |
|---:|---|---|---:|
| 1 | Raspberry Pi 5, 1 GB | Raspberry Pi approved resellers | 45.00 |
| 1 | Power supply | Raspberry Pi 27 W USB-C power supply | 12.00 |
| 1 | Cooler | Raspberry Pi Active Cooler | 5.00 |
| 1 | microSD card | Raspberry Pi 32 GB card, SanDisk, Samsung | 8.00 |
| 1 | USB audio interface | Behringer UCA222 (line in) | 30.00 |
| 1 | Input cable | for the UCA222: 1/4-inch TS to 2x RCA | 6.00 |
| 1 | 1.2-inch 4-digit 7-segment display with I2C backpack, red | Adafruit 1270 | 17.50 |
| 1 | Red filter, 2 mm transparent acrylic | laser-cut from hardware/enclosures/cut/, or hand-cut from an A5 sheet | 5.00 |
| 1 | Push button, 16 mm, momentary | metal 16 mm momentary button with solder lugs or screw terminals | 3.00 |
| 1 | Footswitch jack | Switchcraft 11 or a generic open-frame mono jack | 2.00 |
| 1 | R1 resistor 1 kOhm | any carbon or metal film | 0.10 |
| 1 | C1 capacitor 100 nF | any radial MLCC or disc | 0.20 |
| 1 | Footswitch, momentary *(optional)* | Boss FS-5U, or any momentary sustain pedal | 25.00 |
| 1 | Dupont jumper wires F-F, 20 cm | any 40-way F-F 20 cm jumper ribbon | 5.00 |
| 1 | Heat-shrink tubing | share of an assortment | 1.00 |
| 1 | Cable tie, 2.5 mm | any | 0.05 |
| 1 | Solder | any | - |
| 205 | Filament, grams | any 1.75 mm filament | 4.10 |
| 3 | Heat-set insert M3 | CNC Kitchen or Ruthex M3 x 5.7 | 0.30 |
| 3 | Screw M3 x 8 | any | 0.30 |
| 8 | Screw M2.5 x 8 | any | 0.80 |
| 4 | Rubber bumpers | any | 0.60 |
| 2 | Hook-and-loop or 3M Dual Lock, 25 x 60 mm *(optional)* | any | 2.00 |
| | **Total** | | **146** |
| | Total with the optional parts | | 173 |
<!-- END GENERATED: stage parts -->

## Budget

<!-- BEGIN GENERATED: budget parts -->
| Qty | Part | Example | Approx. USD |
|---:|---|---|---:|
| 1 | Raspberry Pi 5, 1 GB | Raspberry Pi approved resellers | 45.00 |
| 1 | Power supply | Raspberry Pi 27 W USB-C power supply | 12.00 |
| 1 | Cooler | Raspberry Pi Active Cooler | 5.00 |
| 1 | microSD card | Raspberry Pi 32 GB card, SanDisk, Samsung | 8.00 |
| 1 | USB audio interface | Behringer UCA222 (line in) | 30.00 |
| 1 | Input cable | for the UCA222: 1/4-inch TS to 2x RCA | 6.00 |
| 1 | 0.56-inch 4-digit 7-segment module, red | generic "TM1637 4-digit" module | 3.00 |
| 1 | Red filter, 2 mm transparent acrylic *(optional)* | laser-cut from hardware/enclosures/cut/, or hand-cut from an A5 sheet | 5.00 |
| 1 | Push button, 16 mm, momentary | metal 16 mm momentary button with solder lugs or screw terminals | 3.00 |
| 1 | Footswitch jack *(optional)* | Switchcraft 11 or a generic open-frame mono jack | 2.00 |
| 1 | R1 resistor 1 kOhm *(optional)* | any carbon or metal film | 0.10 |
| 1 | C1 capacitor 100 nF *(optional)* | any radial MLCC or disc | 0.20 |
| 1 | Footswitch, momentary *(optional)* | Boss FS-5U, or any momentary sustain pedal | 25.00 |
| 1 | Dupont jumper wires F-F, 20 cm | any 40-way F-F 20 cm jumper ribbon | 5.00 |
| 1 | Heat-shrink tubing | share of an assortment | 1.00 |
| 1 | Cable tie, 2.5 mm *(optional)* | any | 0.05 |
| 1 | Solder | any | - |
| 220 | Filament, grams | any 1.75 mm filament | 4.40 |
| 3 | Heat-set insert M3 | CNC Kitchen or Ruthex M3 x 5.7 | 0.30 |
| 3 | Screw M3 x 8 | any | 0.30 |
| 6 | Screw M2.5 x 8 | any | 0.60 |
| 4 | Rubber bumpers | any | 0.60 |
| 2 | Hook-and-loop or 3M Dual Lock, 25 x 60 mm *(optional)* | any | 2.00 |
| | **Total** | | **124** |
| | Total with the optional parts | | 159 |
<!-- END GENERATED: budget parts -->

The budget build's jack, R1, C1, cable tie and footswitch are optional: the
floor wedge always has the jack hole, so you can add the footswitch later.
A 0.36-inch TM1637 module works too, with its own shell
(`stage_wedge-tm1637_036-shell.stl`).

## Buying notes

* **Pi 4 instead of Pi 5**: use the official 15 W USB-C supply and a stick-on
  heatsink instead of the 27 W supply and the Active Cooler. Both boards fit
  both enclosures.
* **Adafruit 1270** is a kit: you solder the display and the header onto the
  backpack. Follow Adafruit's assembly guide.
* **LCD and TM1637 modules vary between vendors.** The enclosures are drawn
  for the common sizes listed in the specification column. Measure yours with
  calipers before printing and compare with
  [the enclosure guide](../enclosures/README.md#check-your-modules).
* **Heat-set inserts**: any M3 insert made for a 4.0 mm hole, up to 6 mm
  long. Without inserts, set `closure = "selftap"` in the enclosure file and
  use M3 thread-forming screws for plastic.
* **Red filter**: 2 mm transparent red cast acrylic. Laser-cutting services
  cut it from the DXF in [`../enclosures/cut/`](../enclosures/cut/); by hand,
  score it with a knife along a steel rule and snap it. A red lighting gel
  (for example LEE 106) taped to clear 2 mm acrylic works as well.
* **Footswitch**: any momentary footswitch with a 1/4-inch TS plug, normally
  open or normally closed, including keyboard sustain pedals. Latching
  pedals do not work.
* The **legacy MAX7219** build has no enclosure; its parts are in the
  [wiring guide](../wiring/README.md#legacy-build-max7219-via-74ahct125).

## Tools

* 3D printer with at least a 180 x 180 x 180 mm build volume
* Soldering iron (a spare conical tip for the heat-set inserts), solder
* Wire strippers, flush cutters, heat gun or lighter for the heat-shrink
* Screwdrivers for M2.5 and M3 screws
* Multimeter, for the continuity checks before the first power-on
* Calipers, to check your display module against the enclosure

## Regenerating

The CSVs, the tables above and the parts data in `checklist.html` are
generated from one parts table:

```bash
python3 hardware/bom/tools/build_bom.py           # rewrite the files
python3 hardware/bom/tools/build_bom.py --check   # CI: fail if they are stale
```

Change quantities, parts or prices in `tools/build_bom.py`, not in the
generated files. Store links, pack prices and the shopping descriptions are
in the `shop-data` block of `checklist.html`; edit them there. Every part
needs an entry there, keyed by its id in the parts table, or `--check` fails.
