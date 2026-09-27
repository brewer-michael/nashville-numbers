#!/usr/bin/env python3
"""Render every enclosure part with OpenSCAD and check that it can be built.

For each enclosure and variant:
  1. every printable part (print orientation) is a single watertight body
     (or the expected number of bodies), fits a 180 x 180 x 180 mm printer
     and rests on z = 0;
  2. in the assembled position no printed part intersects any "ghost" - the
     Pi 4 and Pi 5 with coolers, ports, plug bodies and GPIO jumpers, the
     display module and its wiring, button, jack, level shifter - and the
     printed parts do not intersect each other.

Needs: openscad (2021.01+), python3 with numpy, scipy, trimesh and manifold3d.
Usage: python3 tools/check_cad.py [--keep DIR] [enclosure ...]
Exit code 0 = all checks passed.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from itertools import combinations
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent.parent
BED = 180.0                 # fits Prusa MINI / Bambu Lab A1 mini class printers
MAX_OVERLAP_MM3 = 0.5

ENCLOSURES = {
    'desktop_lcd_case': {
        'variants': [{}],
        'print': {'shell': 1, 'base': 1, 'clamps': 3},
        'assembled': ['shell_asm', 'base_asm', 'clamps_asm'],
        'ghosts': ['ghosts_pi4', 'ghosts_pi5', 'ghost_display', 'ghost_controls'],
    },
    'stage_wedge': {
        'variants': [{'display': 'ht16k33_12'}, {'display': 'tm1637_056'},
                     {'display': 'tm1637_036'}],
        # clamp tabs: 4 for the 1.2" module, 2 for the TM1637 modules
        'print': {'shell': 1, 'base': 1,
                  'clamps': lambda v: 4 if v.get('display') == 'ht16k33_12' else 2},
        'assembled': ['shell_asm', 'base_asm', 'clamps_asm', 'filter_asm'],
        'ghosts': ['ghosts_pi4', 'ghosts_pi5', 'ghost_display', 'ghost_controls'],
    },
}


def scad_value(v):
    return f'"{v}"' if isinstance(v, str) else str(v)


def render(scad, part, variant, out_dir):
    tag = '_'.join([part] + [str(v) for v in variant.values()])
    out = Path(out_dir) / f"{Path(scad).stem}__{tag}.stl"
    if out.exists():
        return out
    args = ['openscad', '-o', str(out), '-D', f'part={scad_value(part)}']
    for k, v in variant.items():
        args += ['-D', f'{k}={scad_value(v)}']
    args.append(str(scad))
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0 or not out.exists():
        if 'Current top level object is empty' in proc.stderr:
            return None
        raise RuntimeError(f"openscad failed for {scad} part={part}:\n{proc.stderr[-2000:]}")
    return out


def load(path):
    mesh = trimesh.load_mesh(str(path), process=True)
    return mesh


def overlap(a, b):
    if a is None or b is None:
        return 0.0
    # quick reject on bounding boxes
    lo = np.maximum(a.bounds[0], b.bounds[0])
    hi = np.minimum(a.bounds[1], b.bounds[1])
    if np.any(hi <= lo):
        return 0.0
    inter = trimesh.boolean.intersection([a, b], engine='manifold')
    return float(abs(inter.volume)) if inter is not None and len(inter.faces) else 0.0


def check_enclosure(name, spec, out_dir):
    scad = HERE / f"{name}.scad"
    failures = []
    for variant in spec['variants']:
        label = name + (' ' + ' '.join(f"{k}={v}" for k, v in variant.items()) if variant else '')
        print(f"== {label}")
        for part, bodies in spec['print'].items():
            bodies = bodies(variant) if callable(bodies) else bodies
            mesh = load(render(scad, part, variant, out_dir))
            n = len(mesh.split(only_watertight=False))
            ext = mesh.extents
            on_bed = abs(mesh.bounds[0][2]) < 0.01
            ok = mesh.is_watertight and n == bodies and max(ext) <= BED and on_bed
            print(f"   print  {part:<10} {'ok ' if ok else 'FAIL'} bodies={n} "
                  f"watertight={mesh.is_watertight} "
                  f"size={ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm  "
                  f"volume={mesh.volume / 1000:.1f} cm3")
            if not ok:
                failures.append(f"{label}: print part {part}")
        assembled = {p: render(scad, p, variant, out_dir) for p in spec['assembled']}
        assembled = {p: load(f) if f else None for p, f in assembled.items()}
        ghosts = {g: load(render(scad, g, variant, out_dir)) for g in spec['ghosts']}
        for p, mesh in assembled.items():
            for g, ghost in ghosts.items():
                v = overlap(mesh, ghost)
                status = 'ok ' if v <= MAX_OVERLAP_MM3 else 'FAIL'
                print(f"   fit    {p:<11} vs {g:<13} {status} overlap={v:.2f} mm3")
                if v > MAX_OVERLAP_MM3:
                    failures.append(f"{label}: {p} intersects {g} ({v:.1f} mm3)")
        for (p1, m1), (p2, m2) in combinations(assembled.items(), 2):
            v = overlap(m1, m2)
            status = 'ok ' if v <= MAX_OVERLAP_MM3 else 'FAIL'
            print(f"   fit    {p1:<11} vs {p2:<13} {status} overlap={v:.2f} mm3")
            if v > MAX_OVERLAP_MM3:
                failures.append(f"{label}: {p1} intersects {p2} ({v:.1f} mm3)")
    return failures


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('enclosures', nargs='*', default=list(ENCLOSURES))
    ap.add_argument('--keep', help='directory for the rendered STLs (default: temporary)')
    args = ap.parse_args()
    out_dir = args.keep or tempfile.mkdtemp(prefix='cadcheck-')
    os.makedirs(out_dir, exist_ok=True)
    failures = []
    for name in args.enclosures:
        failures += check_enclosure(name, ENCLOSURES[name], out_dir)
    if failures:
        print("\nFAILED:\n  " + "\n  ".join(failures))
        return 1
    print("\nAll enclosure checks passed.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
