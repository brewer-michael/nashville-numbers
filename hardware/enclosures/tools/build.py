#!/usr/bin/env python3
"""Export the enclosure files: print-ready STLs, filter cut files, preview images.

  stl/       every printed part, already in its print orientation (binary STL)
  cut/       the stage wedge's red filter: DXF for laser cutting, SVG as a
             1:1 template for cutting by hand
  renders/   PNG previews shown in README.md

Needs OpenSCAD 2021.01 or newer. The PNGs need an X display: on a headless
Linux machine the script re-runs itself under xvfb-run when that is installed.

Usage: python3 tools/build.py [--no-png] [--only PATTERN] [--jobs N] [--out DIR]
"""

import argparse
import fnmatch
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
STAGE_DISPLAYS = ['ht16k33_12', 'tm1637_056', 'tm1637_036']
IMAGE_SIZE = (1200, 900)


@dataclass
class Job:
    path: str                       # output, relative to the output directory
    scad: str                       # enclosure file stem
    part: str
    variables: dict = field(default_factory=dict)
    camera: tuple = ()              # eye x, y, z, centre x, y, z (PNG only)


def cam(eye, centre):
    return tuple(eye) + tuple(centre)


def jobs():
    out = []
    # desktop LCD case
    for part in ('shell', 'base', 'clamps'):
        out.append(Job(f'stl/desktop_lcd_case-{part}.stl', 'desktop_lcd_case', part))
    desk_views = {
        'assembly': ('assembly', cam((300, -250, 230), (62, 40, 38))),
        'rear': ('assembly', cam((-188, 328, 232), (62, 41, 40))),
        'cutaway': ('cutaway', cam((330, -180, 190), (55, 41, 30))),
        'exploded': ('exploded', cam((570, -365, 275), (62, 50, 100))),
        'print': ('print_layout', cam((-230, -420, 330), (128, -40, 18))),
    }
    for name, (part, camera) in desk_views.items():
        out.append(Job(f'renders/desktop_lcd_case-{name}.png', 'desktop_lcd_case', part,
                       camera=camera))

    # stage wedge: one base, a shell, clamp tabs and a filter per display
    out.append(Job('stl/stage_wedge-base.stl', 'stage_wedge', 'base'))
    for d in STAGE_DISPLAYS:
        v = {'display': d}
        out.append(Job(f'stl/stage_wedge-{d}-shell.stl', 'stage_wedge', 'shell', v))
        out.append(Job(f'stl/stage_wedge-{d}-clamps.stl', 'stage_wedge', 'clamps', v))
        out.append(Job(f'cut/stage_wedge-{d}-filter.dxf', 'stage_wedge', 'filter', v))
        out.append(Job(f'cut/stage_wedge-{d}-filter.svg', 'stage_wedge', 'filter', v))
    stage_views = {
        'assembly': ('assembly', 'ht16k33_12', cam((340, -290, 260), (71, 54, 45))),
        'tm1637_056-assembly': ('assembly', 'tm1637_056', cam((340, -290, 260), (71, 54, 45))),
        'rear': ('assembly', 'ht16k33_12', cam((-202, 387, 257), (71, 54, 45))),
        'cutaway': ('cutaway', 'ht16k33_12', cam((380, -230, 220), (65, 54, 30))),
        'exploded': ('exploded', 'ht16k33_12', cam((660, -420, 320), (71, 60, 112))),
        'print': ('print_layout', 'ht16k33_12', cam((-260, -480, 380), (150, -48, 20))),
    }
    for name, (part, d, camera) in stage_views.items():
        out.append(Job(f'renders/stage_wedge-{name}.png', 'stage_wedge', part, {'display': d},
                       camera=camera))
    return out


def scad_value(v):
    return f'"{v}"' if isinstance(v, str) else str(v)


def command(job, target, image_size):
    args = ['openscad', '-o', str(target), '-D', f'part={scad_value(job.part)}']
    for k, v in job.variables.items():
        args += ['-D', f'{k}={scad_value(v)}']
    if target.suffix == '.stl':
        args += ['--export-format', 'binstl']
    elif target.suffix == '.png':
        args += ['--camera=' + ','.join(str(c) for c in job.camera),
                 '--imgsize={},{}'.format(*image_size),
                 '--colorscheme=Tomorrow', '--projection=p']
    return args + [str(HERE / f'{job.scad}.scad')]


def run(job, out_dir, image_size):
    target = Path(out_dir) / job.path
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.stem + '.tmp' + target.suffix)
    t0 = time.time()
    proc = subprocess.run(command(job, tmp, image_size), capture_output=True, text=True)
    if proc.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        return job, False, proc.stderr.strip()[-1500:]
    # the enclosure files assert on warnings they care about; surface the rest
    warnings = [line for line in proc.stderr.splitlines() if line.startswith('WARNING')]
    os.replace(tmp, target)
    info = f'{time.time() - t0:5.1f} s  {target.stat().st_size / 1024:7.1f} KB'
    return job, True, info + ('\n      ' + '\n      '.join(warnings) if warnings else '')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--no-png', action='store_true', help='skip the PNG renders')
    ap.add_argument('--only', action='append', metavar='PATTERN',
                    help='only outputs matching this glob, e.g. "stl/stage*" (repeatable)')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 2)
    ap.add_argument('--out', default=str(HERE), help='output directory (default: %(default)s)')
    ap.add_argument('--size', default='{},{}'.format(*IMAGE_SIZE), help='PNG size W,H')
    args = ap.parse_args()

    if shutil.which('openscad') is None:
        sys.exit('openscad not found - install OpenSCAD 2021.01 or newer')
    todo = [j for j in jobs()
            if not (args.no_png and j.path.endswith('.png'))
            and (not args.only or any(fnmatch.fnmatch(j.path, p) for p in args.only))]
    if not todo:
        sys.exit('nothing to build')

    wants_x = any(j.path.endswith('.png') for j in todo)
    if (wants_x and sys.platform.startswith('linux') and not os.environ.get('DISPLAY')
            and not os.environ.get('NN_BUILD_UNDER_XVFB')):
        if shutil.which('xvfb-run'):
            os.environ['NN_BUILD_UNDER_XVFB'] = '1'
            os.execvp('xvfb-run', ['xvfb-run', '-a', '-s', '-screen 0 1920x1080x24',
                                   sys.executable] + sys.argv)
        print('warning: no X display and no xvfb-run; PNG export will probably fail')

    image_size = tuple(int(x) for x in args.size.split(','))
    failed = []
    print(f'building {len(todo)} files into {args.out} with {args.jobs} jobs')
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for job, ok, info in pool.map(lambda j: run(j, args.out, image_size), todo):
            print(f"  {'ok  ' if ok else 'FAIL'} {job.path:<44} {info}")
            if not ok:
                failed.append(job.path)
    if failed:
        print('\nFAILED:\n  ' + '\n  '.join(failed))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
