#!/usr/bin/env python3
"""Generate the per-build bills of materials from one parts table.

Writes desktop.csv, stage.csv and budget.csv next to this folder, the
generated tables in bom/README.md and hardware/README.md, and the parts data
of the shopping checklist page, checklist.html (between
"<!-- BEGIN GENERATED: ... -->" markers). The page's store links and pack
prices are kept by hand in its "shop-data" block; this script checks that
every part has an entry there.

Quantities follow hardware/SPEC.md, the wiring cut lists
(hardware/wiring/README.md) and the enclosure hardware
(hardware/enclosures/README.md). Prices are rough USD street prices
(September 2026) for budgeting, not quotes.

Usage: python3 tools/build_bom.py [--check]
  --check   exit 1 if any generated file is out of date (used by CI)
"""

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

BOM = Path(__file__).resolve().parent.parent
HARDWARE = BOM.parent
CHECKLIST = BOM / 'checklist.html'
BUILDS = {
    'desktop': 'Desktop (16x2 LCD, desktop case)',
    'stage': 'Stage (Adafruit 1.2" 7-segment, floor wedge, footswitch)',
    'budget': 'Budget (TM1637 0.56" 7-segment, floor wedge)',
}
OPT = 'optional'

# id, section, item, specification, example / source, unit USD, notes,
# {build: qty or (qty, OPT)}. The id is also the part's key in checklist.html.
PARTS = [
    ('pi', 'Computer', 'Raspberry Pi 5, 1 GB',
     'Raspberry Pi 5 1 GB, or a Raspberry Pi 4 Model B 1 GB or larger (the cases fit both)',
     'Raspberry Pi approved resellers', 45.00,
     'list prices 2026: Pi 5 1 GB $45, Pi 4 1 GB $35, Pi 4 2 GB $65; the app needs about 60 MB',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('psu', 'Computer', 'Power supply',
     'Pi 5: official 27 W USB-C, 5.1 V 5 A. Pi 4: official 15 W USB-C, 5.1 V 3 A ($8)',
     'Raspberry Pi 27 W USB-C power supply', 12.00,
     'on a 3 A supply a Pi 5 limits all USB ports to 600 mA, shared with the audio interface',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('cooler', 'Computer', 'Cooler',
     'Pi 5: official Active Cooler. Pi 4: stick-on heatsink',
     'Raspberry Pi Active Cooler', 5.00,
     'the cases are vented over the cooler',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('sd', 'Computer', 'microSD card',
     '32 GB, A1 or A2 rated',
     'Raspberry Pi 32 GB card, SanDisk, Samsung', 8.00,
     'Raspberry Pi OS Lite 64-bit (Bookworm or Trixie)',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('audio', 'Audio', 'USB audio interface',
     'USB class compliant; choose by source, see hardware/SPEC.md section 4',
     'Behringer UCA222 (line in)', 30.00,
     'Hi-Z guitar or bass: Behringer UCG102 (~$30) or UM2 (~$50, also takes a mic)',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('cable', 'Audio', 'Input cable',
     'from your source to the interface',
     'for the UCA222: 1/4-inch TS to 2x RCA', 6.00,
     '',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('lcd', 'Display', '16x2 character LCD with I2C backpack',
     'HD44780 16x2, 80 x 36 mm PCB, 71.2 x 24.2 mm bezel, PCF8574 I2C backpack',
     'generic "LCD1602 I2C" module', 7.00,
     'backlight colour to taste; check the bezel size against the case (enclosures/README.md)',
     {'desktop': 1}),
    ('shifter', 'Display', 'I2C level shifter',
     'BSS138 bidirectional, 4 channels, board up to 21 x 17 mm',
     'Adafruit 757 or generic "I2C-safe" 4-channel board', 4.00,
     'keeps the 5 V LCD backpack pull-ups off the 3.3 V GPIO pins',
     {'desktop': 1}),
    ('ht16k33', 'Display', '1.2-inch 4-digit 7-segment display with I2C backpack, red',
     'HT16K33 backpack, 120 x 50 mm, digits 30 mm tall',
     'Adafruit 1270', 17.50,
     'other colours work; red suits the red filter',
     {'stage': 1}),
    ('tm1637', 'Display', '0.56-inch 4-digit 7-segment module, red',
     'TM1637, module PCB about 50.5 x 25 mm',
     'generic "TM1637 4-digit" module', 3.00,
     'runs on 3.3 V; the 0.36-inch module (42 x 24 mm) also fits, with its own shell',
     {'budget': 1}),
    ('filter', 'Display', 'Red filter, 2 mm transparent acrylic',
     'stage: 116 x 46 mm; budget 0.56-inch: 54 x 23 mm',
     'laser-cut from hardware/enclosures/cut/, or hand-cut from an A5 sheet', 5.00,
     'improves contrast under stage lights; a red lighting gel on clear acrylic also works',
     {'stage': 1, 'budget': (1, OPT)}),
    ('button', 'Controls', 'Push button, 16 mm, momentary',
     'normally open, 16 mm panel hole, up to 35 mm deep behind the panel',
     'metal 16 mm momentary button with solder lugs or screw terminals', 3.00,
     'new song / lock key / safe shutdown',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('jack', 'Controls', 'Footswitch jack',
     '1/4-inch (6.35 mm) mono TS, open frame, 3/8-inch bush for a 9.5 mm hole',
     'Switchcraft 11 or a generic open-frame mono jack', 2.00,
     'goes in the back wall of the floor wedge',
     {'stage': 1, 'budget': (1, OPT)}),
    ('r1', 'Controls', 'R1 resistor 1 kOhm',
     '0.25 W, 5 % or better, axial',
     'any carbon or metal film', 0.10,
     'in series with the jack tip, soldered at the jack',
     {'stage': 1, 'budget': (1, OPT)}),
    ('c1', 'Controls', 'C1 capacitor 100 nF',
     'ceramic X7R, 50 V or more, through-hole (marked 104)',
     'any radial MLCC or disc', 0.20,
     'jack tip (GPIO side of R1) to sleeve, soldered at the jack',
     {'stage': 1, 'budget': (1, OPT)}),
    ('footswitch', 'Controls', 'Footswitch, momentary',
     'momentary, with a 1/4-inch TS cable; normally open or closed',
     'Boss FS-5U, or any momentary sustain pedal', 25.00,
     'the software learns the pedal polarity; skip it if you own one',
     {'stage': (1, OPT), 'budget': (1, OPT)}),
    ('jumpers', 'Wiring', 'Dupont jumper wires F-F, 20 cm',
     '2.54 mm, 26-28 AWG, 40-way rainbow ribbon; peel off what you need',
     'any 40-way F-F 20 cm jumper ribbon', 5.00,
     'uses 12 (desktop), 9 (stage), 6 (budget, 8 with a footswitch); colours in wiring/README.md',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('heatshrink', 'Wiring', 'Heat-shrink tubing',
     '2:1, 3.2 mm and 4.8 mm',
     'share of an assortment', 1.00,
     'lengths per build in wiring/README.md',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('tie', 'Wiring', 'Cable tie, 2.5 mm',
     'small nylon tie',
     'any', 0.05,
     'strain relief at the jack',
     {'stage': 1, 'budget': (1, OPT)}),
    ('solder', 'Wiring', 'Solder',
     'rosin core, 0.8 mm',
     'any', 0.00,
     'about 20 cm',
     {'desktop': 1, 'stage': 1, 'budget': 1}),
    ('filament', 'Enclosure', 'Filament, grams',
     'desktop: PLA or PETG; floor wedge: PETG. 0.2 mm layers, 3 perimeters, 20 % infill',
     'any 1.75 mm filament', 0.02,
     'estimated from the part volumes; STLs in enclosures/stl/',
     {'desktop': 130, 'stage': 205, 'budget': 220}),
    ('inserts', 'Enclosure', 'Heat-set insert M3',
     'for a 4.0 mm hole, up to 6 mm long',
     'CNC Kitchen or Ruthex M3 x 5.7', 0.10,
     'case closure; or M3 thread-forming screws with closure = "selftap"',
     {'desktop': 3, 'stage': 3, 'budget': 3}),
    ('m3', 'Enclosure', 'Screw M3 x 8',
     'button head (ISO 7380) or socket head (ISO 4762)',
     'any', 0.10,
     'through the base plate into the inserts',
     {'desktop': 3, 'stage': 3, 'budget': 3}),
    ('m25', 'Enclosure', 'Screw M2.5 x 8',
     'pan or button head; self-tapping for plastic, or a machine screw',
     'any', 0.10,
     '4 hold the Pi; the rest hold the display clamp tabs (3 desktop, 4 stage, 2 budget)',
     {'desktop': 7, 'stage': 8, 'budget': 6}),
    ('bumpers', 'Enclosure', 'Rubber bumpers',
     'adhesive, up to 13 mm diameter (12.7 mm is common), about 3 mm tall',
     'any', 0.15,
     'recesses under the base',
     {'desktop': 4, 'stage': 4, 'budget': 4}),
    ('foamtape', 'Enclosure', 'Double-sided foam tape',
     'a 20 x 15 mm piece',
     'any mounting tape', 0.20,
     'holds the level shifter on the base plate',
     {'desktop': 1}),
    ('duallock', 'Enclosure', 'Hook-and-loop or 3M Dual Lock, 25 x 60 mm',
     'adhesive backed',
     'any', 1.00,
     'for pedalboard mounting; recesses under the base',
     {'stage': (2, OPT), 'budget': (2, OPT)}),
]

# units for quantities that are not a count (shown on the checklist page)
UNITS = {'filament': 'g'}

COLUMNS = ['section', 'item', 'qty', 'specification', 'example / source',
           'approx unit USD', 'approx total USD', 'optional', 'notes']


def rows(build):
    for _id, section, item, spec, source, unit, notes, qtys in PARTS:
        if build not in qtys:
            continue
        q = qtys[build]
        qty, optional = (q[0], True) if isinstance(q, tuple) else (q, False)
        yield {'section': section, 'item': item, 'qty': qty, 'spec': spec,
               'source': source, 'unit': unit, 'total': qty * unit,
               'optional': optional, 'notes': notes}


def totals(build):
    req = sum(r['total'] for r in rows(build) if not r['optional'])
    opt = sum(r['total'] for r in rows(build) if r['optional'])
    return req, req + opt


def money(x):
    return f'{x:.2f}'


def csv_text(build):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(COLUMNS)
    for r in rows(build):
        w.writerow([r['section'], r['item'], r['qty'], r['spec'], r['source'],
                    money(r['unit']), money(r['total']), 'yes' if r['optional'] else '',
                    r['notes']])
    req, full = totals(build)
    w.writerow(['Total', 'required parts', '', '', '', '', money(req), '', ''])
    w.writerow(['Total', 'including optional parts', '', '', '', '', money(full), '', ''])
    return buf.getvalue()


def md_parts_table(build):
    lines = ['| Qty | Part | Example | Approx. USD |', '|---:|---|---|---:|']
    for r in rows(build):
        name = r['item'] + (' *(optional)*' if r['optional'] else '')
        cost = f"{r['total']:.2f}" if r['total'] else '-'
        lines.append(f"| {r['qty']} | {name} | {r['source']} | {cost} |")
    req, full = totals(build)
    lines.append(f'| | **Total** | | **{req:.0f}** |')
    if full != req:
        lines.append(f'| | Total with the optional parts | | {full:.0f} |')
    return '\n'.join(lines)


def md_summary_table():
    lines = ['| Build | Parts, approx. USD | With optional parts | CSV |',
             '|---|---:|---:|---|']
    for b, title in BUILDS.items():
        req, full = totals(b)
        lines.append(f'| {title} | {req:.0f} | {full:.0f} | [`{b}.csv`]({b}.csv) |')
    return '\n'.join(lines)


def md_hardware_totals():
    return ' / '.join(f'{b.capitalize()} about ${totals(b)[0]:.0f}' for b in BUILDS)


def page_data():
    """The checklist page's parts data: one JSON object per part."""
    parts = []
    for pid, section, item, _spec, _source, unit, _notes, qtys in PARTS:
        use = {b: (q[0] if isinstance(q, tuple) else q) for b, q in qtys.items()}
        optional = [b for b, q in qtys.items() if isinstance(q, tuple)]
        parts.append({'id': pid, 'section': section, 'item': item, 'use': use,
                      'optional': optional, 'unit': UNITS.get(pid), 'bomUsd': unit})
    lines = ',\n'.join(json.dumps(p, ensure_ascii=False) for p in parts)
    body = '{"builds": ' + json.dumps(list(BUILDS)) + ',\n"parts": [\n' + lines + '\n]}'
    return ('<script type="application/json" id="bom-data">\n'
            + body.replace('</', '<\\/') + '\n</script>')


def checklist_problems(text):
    """Parts without store data in the page, or store data for parts that are gone."""
    m = re.search(r'<script type="application/json" id="shop-data">(.*?)</script>', text, re.S)
    if not m:
        return ['no shop-data block']
    shop = json.loads(m.group(1))
    ids = [p[0] for p in PARTS]
    problems = [f'part "{i}" has no shop-data entry' for i in ids if i not in shop['parts']]
    problems += [f'shop-data entry "{i}" is not in the parts table'
                 for i in shop['parts'] if i not in ids]
    problems += [f'build "{b}" has no shop-data entry' for b in BUILDS if b not in shop['builds']]
    return problems


def generated_blocks():
    blocks = {BOM / 'README.md': {'summary': md_summary_table()},
              HARDWARE / 'README.md': {'bom totals': md_hardware_totals()},
              CHECKLIST: {'parts data': page_data()}}
    for b in BUILDS:
        blocks[BOM / 'README.md'][f'{b} parts'] = md_parts_table(b)
    return blocks


def sync(path, blocks, text):
    for key, body in blocks.items():
        k = re.escape(key)
        pat = re.compile(rf'(<!-- BEGIN GENERATED: {k} -->\n).*?(<!-- END GENERATED: {k} -->)',
                         re.S)
        if not pat.search(text):
            raise SystemExit(f'{path}: marker block "{key}" not found')
        text = pat.sub(lambda m, body=body: m.group(1) + body + '\n' + m.group(2), text)
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--check', action='store_true',
                    help='fail if a generated file is out of date instead of writing it')
    args = ap.parse_args()
    outputs = {BOM / f'{b}.csv': csv_text(b) for b in BUILDS}
    for path, blocks in generated_blocks().items():
        outputs[path] = sync(path, blocks, path.read_text(encoding='utf-8'))
    stale = []
    for path, text in outputs.items():
        old = path.read_text(encoding='utf-8') if path.exists() else None
        if old != text:
            stale.append(path.relative_to(HARDWARE.parent))
            if not args.check:
                path.write_text(text, encoding='utf-8')
    problems = checklist_problems(outputs[CHECKLIST])
    if problems:
        print(f'{CHECKLIST.name}:\n  ' + '\n  '.join(problems))
    if args.check and stale:
        print('out of date (run hardware/bom/tools/build_bom.py):\n  '
              + '\n  '.join(map(str, stale)))
    if problems or (args.check and stale):
        return 1
    for b in BUILDS:
        req, full = totals(b)
        print(f'{b:<8} ${req:7.2f} required, ${full:7.2f} with optional parts')
    return 0


if __name__ == '__main__':
    sys.exit(main())
