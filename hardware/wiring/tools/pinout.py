#!/usr/bin/env python3
"""Draw pinout.svg: the Raspberry Pi 40-pin header with the pins used by the
Nashville Numbers v2 builds colour-coded by function (= wire colour).

Pure Python (standard library only); data comes from wiring_data.py, the same
data tools/check_wiring.py checks the WireViz harnesses against.  PNG export
is done by tools/build.sh (rsvg-convert or cairosvg).

Usage:  python3 tools/pinout.py [-o pinout.svg]
"""

import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiring_data as wd  # noqa: E402

# cairosvg uses only the first family; browsers fall back to Verdana (same metrics).
FONT = "DejaVu Sans, Verdana, Arial, sans-serif"
INK = "#212529"
MUTED = "#868e96"
LINE = "#ced4da"

W, H = 1200, 1500
ROW0, PITCH = 222, 30          # y of the pin 1/2 row, row pitch
ODD_X, EVEN_X, PAD_R = 420, 460, 11
PILL_W, PILL_H = 136, 22
BADGE, BADGE_GAP = 18, 4


class Svg:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=14, anchor="start", weight="normal", fill=INK,
             italic=False, rotate=None):
        extra = ' font-style="italic"' if italic else ""
        if rotate is not None:
            extra += f' transform="rotate({rotate} {x} {y})"'
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" fill="{fill}"{extra}>{escape(s)}</text>')

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, rx=0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill, stroke="none", sw=1):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}"/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{d}/>')

    def polygon(self, pts, fill):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f'<polygon points="{p}" fill="{fill}"/>')

    def render(self):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                f'viewBox="0 0 {W} {H}" font-family="{FONT}">\n'
                '<title>Raspberry Pi 40-pin header: Nashville Numbers v2 pin usage</title>\n'
                f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>\n')
        return head + "\n".join(self.parts) + "\n</svg>\n"


def pin_xy(pin):
    """Centre of a pad in the main drawing (odd pins left, even pins right)."""
    row = (pin - 1) // 2
    return (ODD_X if pin % 2 else EVEN_X), ROW0 + row * PITCH


def text_y(cy, size):
    return round(cy + size * 0.36, 1)  # baseline for vertically centred text


def draw_header(svg, usage):
    top, bottom = ROW0 - 24, ROW0 + 19 * PITCH + 24
    svg.text((ODD_X + EVEN_X) / 2, top - 62, "▲ microSD-card end", 14, "middle", "bold")
    svg.text((ODD_X + EVEN_X) / 2, top - 44, "pin 1 = square pad", 12, "middle", fill="#495057")
    svg.text((ODD_X + EVEN_X) / 2, bottom + 26, "▼ USB / Ethernet end", 14, "middle", "bold")

    odd_pill_x = ODD_X - 28 - PILL_W
    even_pill_x = EVEN_X + 28
    odd_badge_x = odd_pill_x - 12 - (4 * BADGE + 3 * BADGE_GAP)
    even_badge_x = even_pill_x + PILL_W + 12
    cap_y = top - 16
    svg.text(odd_pill_x + PILL_W / 2, cap_y - 16, "odd pins", 13, "middle", "bold")
    svg.text(odd_pill_x + PILL_W / 2, cap_y, "inner row", 12, "middle", fill=MUTED)
    svg.text(even_pill_x + PILL_W / 2, cap_y - 16, "even pins", 13, "middle", "bold")
    svg.text(even_pill_x + PILL_W / 2, cap_y, "outer row, board edge", 12, "middle", fill=MUTED)
    for bx in (odd_badge_x, even_badge_x):
        for i, b in enumerate(wd.BUILD_ORDER):
            svg.text(bx + i * (BADGE + BADGE_GAP) + BADGE / 2, cap_y, wd.BUILDS[b]["letter"],
                     12, "middle", "bold")
        svg.text(bx + (4 * BADGE + 3 * BADGE_GAP) / 2, cap_y - 16, "builds", 12, "middle",
                 fill=MUTED)

    # plastic header body
    svg.rect(ODD_X - 21, top, EVEN_X - ODD_X + 42, bottom - top, fill="#343a40", rx=6)

    for pin in range(1, 41):
        x, y = pin_xy(pin)
        name = wd.HEADER[pin]
        used = pin in usage
        if used:
            c = wd.COLOURS[wd.pin_function(pin)]
            fill, ink, stroke = c["hex"], c["ink"], "#000000"
        else:
            fill, ink, stroke = "#dee2e6", "#495057", "#adb5bd"
        if pin == 1:
            svg.rect(x - PAD_R, y - PAD_R, 2 * PAD_R, 2 * PAD_R, fill=fill, stroke=stroke, sw=1.5)
        else:
            svg.circle(x, y, PAD_R, fill, stroke, 1.5 if used else 1)
        svg.text(x, text_y(y, 11), str(pin), 11, "middle", "bold", ink)

        pill_x = odd_pill_x if pin % 2 else even_pill_x
        if used:
            svg.rect(pill_x, y - PILL_H / 2, PILL_W, PILL_H, fill=c["hex"], stroke="#000000",
                     sw=1, rx=PILL_H / 2)
            svg.text(pill_x + PILL_W / 2, text_y(y, 13), name, 13, "middle", "bold", c["ink"])
            badge_x = odd_badge_x if pin % 2 else even_badge_x
            for i, b in enumerate(wd.BUILD_ORDER):
                draw_badge(svg, badge_x + i * (BADGE + BADGE_GAP), y, b,
                           badge_state(usage[pin].get(b)))
        else:
            anchor, tx = ("end", pill_x + PILL_W - 10) if pin % 2 else ("start", pill_x + 10)
            svg.text(tx, text_y(y, 13), name, 13, anchor, fill=MUTED)

    return bottom


def badge_state(wire):
    """'used', 'optional' or 'unused' for one build's use of a header pin."""
    if wire is None:
        return "unused"
    return "optional" if wire["optional"] else "used"


def draw_badge(svg, x, cy, build, state):
    letter = wd.BUILDS[build]["letter"]
    if state == "used":
        svg.rect(x, cy - BADGE / 2, BADGE, BADGE, fill=INK, stroke=INK, rx=3)
        svg.text(x + BADGE / 2, text_y(cy, 11), letter, 11, "middle", "bold", "#ffffff")
    elif state == "optional":
        svg.rect(x + 0.75, cy - BADGE / 2 + 0.75, BADGE - 1.5, BADGE - 1.5, fill="#ffffff",
                 stroke=INK, sw=1.5, rx=3, dash="3,2")
        svg.text(x + BADGE / 2, text_y(cy, 11), letter, 11, "middle", "bold", INK)
    else:
        svg.rect(x, cy - BADGE / 2, BADGE, BADGE, fill="#ffffff", stroke=LINE, rx=3)
        svg.text(x + BADGE / 2, text_y(cy, 11), letter, 11, "middle", "bold", LINE)


def draw_board_inset(svg, x0, y0, s=2.6):
    """Pi 4/5 outline turned 90° clockwise so it matches the main drawing:
    microSD end up, GPIO header on the right, USB/Ethernet down.
    Board coordinates (SPEC.md 2): u = board y, v = board x."""
    bw, bh = 56 * s, 85 * s
    svg.text(x0 + bw / 2, y0 - 34, "Where the header is (Pi 4 / Pi 5, top view)", 13, "middle", "bold")
    # connectors that stick out
    svg.rect(x0 + (28 - 6) * s, y0 - 2.5 * s, 12 * s, 3 * s, fill="#adb5bd", stroke=INK)   # microSD
    svg.text(x0 + bw / 2, y0 - 12, "microSD", 11, "middle", fill="#495057")
    for u0, u1 in ((2, 17), (20, 35), (38, 54)):                                           # USB/Ethernet
        svg.rect(x0 + u0 * s, y0 + bh - 20 * s + 3 * s, (u1 - u0) * s, 20 * s, fill="#ced4da",
                 stroke=INK)
    svg.text(x0 + bw / 2, y0 + bh + 3 * s + 16, "USB / Ethernet", 11, "middle", fill="#495057")
    svg.text(x0 - 14, y0 + 25 * s, "USB-C power, micro-HDMI", 11, "middle", fill="#495057",
             rotate=-90)
    # board
    svg.rect(x0, y0, bw, bh, fill="#d3f9d8", stroke="#2b8a3e", sw=1.5, rx=3 * s)
    for v, w_ in ((11.2, 9), (26.0, 7), (39.5, 7)):                                        # USB-C, HDMI
        svg.rect(x0 - 2 * s, y0 + (v - w_ / 2) * s, 7.5 * s, w_ * s, fill="#adb5bd", stroke=INK)
    for u, v in ((3.5, 3.5), (52.5, 3.5), (3.5, 61.5), (52.5, 61.5)):                       # holes
        svg.circle(x0 + u * s, y0 + v * s, 1.35 * s, "#ffffff", "#2b8a3e")
    # re-draw the USB/Ethernet bodies over the board edge
    for u0, u1 in ((2, 17), (20, 35), (38, 54)):
        svg.rect(x0 + u0 * s, y0 + bh - 20 * s + 3 * s, (u1 - u0) * s, 20 * s, fill="#ced4da",
                 stroke=INK)
    # GPIO header: odd row u = 51.23, even row u = 53.77, pin 1 at v = 8.37
    svg.rect(x0 + 49.9 * s, y0 + 7.0 * s, 5.2 * s, 51.0 * s, fill="#343a40", rx=2)
    for pin in range(1, 41):
        u = 51.23 if pin % 2 else 53.77
        v = 8.37 + ((pin - 1) // 2) * 2.54
        if pin == 1:
            svg.rect(x0 + u * s - 3, y0 + v * s - 3, 6, 6, fill="#fcc419", stroke="#000000")
        else:
            svg.circle(x0 + u * s, y0 + v * s, 2.2, "#adb5bd")
    px, py = x0 + 51.23 * s, y0 + 8.37 * s
    svg.line(px + 12, py - 14, x0 + bw + 30, py - 14, INK, 1)
    svg.line(px + 3, py - 3, px + 12, py - 14, INK, 1)
    svg.text(x0 + bw + 34, text_y(py - 14, 12), "pin 1", 12, "start", "bold")
    svg.text(x0 + bw + 8, text_y(y0 + 36 * s, 12), "GPIO header", 12, "start")
    svg.text(x0 + bw + 8, text_y(y0 + 36 * s + 16, 11), "(this drawing,", 11, "start", fill=MUTED)
    svg.text(x0 + bw + 8, text_y(y0 + 36 * s + 30, 11), "same orientation)", 11, "start", fill=MUTED)
    return y0 + bh + 3 * s + 16


def draw_legends(svg, x0, y0):
    svg.text(x0, y0, "Wire colour = function (all builds)", 14, "start", "bold")
    y = y0 + 12
    for key in wd.COLOUR_ORDER:
        c = wd.COLOURS[key]
        y += 24
        svg.rect(x0, y - 9, 34, 18, fill=c["hex"], stroke="#000000", rx=9)
        name = "purple (violet)" if key == "clk" else c["name"]
        svg.text(x0 + 44, text_y(y, 13), f"{name}: {LEGEND_TEXT[key]}", 13, "start", "bold")
    y += 38
    svg.text(x0, y, "Builds", 14, "start", "bold")
    for b in wd.BUILD_ORDER:
        y += 24
        draw_badge(svg, x0 + 8, y, b, "used")
        svg.text(x0 + 44, text_y(y, 13), f"{wd.BUILDS[b]['name']}: {short_display(b)}", 13)
    y += 28
    draw_badge(svg, x0 + 8, y, "budget_tm1637", "optional")
    svg.text(x0 + 44, text_y(y, 13), "dashed: optional in that build", 13)
    return y


LEGEND_TEXT = {"5v": "5 V", "3v3": "3.3 V", "gnd": "GND", "sda": "I2C SDA (GPIO2)",
               "scl": "I2C SCL (GPIO3)", "button": "panel button (GPIO17)",
               "footswitch": "footswitch (GPIO27)", "clk": "clock (CLK, SCLK)",
               "data": "data (DIO, MOSI)", "cs": "chip select (CE0)"}


def short_display(build):
    return {"desktop_lcd": "16x2 LCD + level shifter",
            "stage_ht16k33": "HT16K33 1.2-inch + footswitch",
            "budget_tm1637": "TM1637 module, optional footswitch",
            "legacy_max7219": "MAX7219 + 74AHCT125"}[build]


def draw_warning(svg, y):
    svg.rect(40, y, W - 80, 58, fill="#fff5f5", stroke="#c92a2a", sw=2, rx=6)
    svg.text(58, y + 24, "5 V pins 2 and 4 sit right next to pin 1 (3V3) and pin 3 (GPIO2).", 14,
             "start", "bold", "#c92a2a")
    svg.text(58, y + 45, "The GPIO pins are 3.3 V only: 5 V on any of them can destroy the Pi. "
             "Power off before wiring, count pins twice, check with a meter.", 13, "start",
             fill="#c92a2a")
    return y + 58


def draw_usage_table(svg, y0, usage):
    cols = [("Pin", 40, 46), ("Name", 86, 126), ("Function", 212, 150)]
    x = 362
    for b in wd.BUILD_ORDER:
        cols.append((f"{wd.BUILDS[b]['letter']}  {wd.BUILDS[b]['name']}", x, 200))
        x += 200
    svg.text(40, y0, "Which build uses which pin", 16, "start", "bold")
    y = y0 + 16
    svg.rect(40, y, W - 80 - 2, 26, fill="#f1f3f5")
    for title, cx, _ in cols:
        svg.text(cx + 6, text_y(y + 13, 13), title, 13, "start", "bold")
    y += 26
    for i, pin in enumerate(sorted(usage)):
        c = wd.COLOURS[wd.pin_function(pin)]
        if i % 2:
            svg.rect(40, y, W - 80 - 2, 24, fill="#f8f9fa")
        cy = y + 12
        svg.text(40 + 40, text_y(cy, 13), str(pin), 13, "end", "bold")
        svg.text(86 + 6, text_y(cy, 13), wd.HEADER[pin], 13)
        svg.rect(212 + 6, cy - 7, 26, 14, fill=c["hex"], stroke="#000000", rx=7)
        svg.text(212 + 40, text_y(cy, 13), c["short"], 13)
        for j, b in enumerate(wd.BUILD_ORDER):
            wire = usage[pin].get(b)
            if wire is None:
                svg.text(cols[3 + j][1] + 6, text_y(cy, 12), "–", 12, fill=LINE)
            else:
                svg.text(cols[3 + j][1] + 6, text_y(cy, 12),
                         wire["role"] + (" (optional)" if wire["optional"] else ""), 12,
                         italic=wire["optional"])
        y += 24
    svg.line(40, y, W - 42, y, LINE)
    return y


def build_svg():
    usage = wd.pin_usage()
    svg = Svg()
    svg.text(40, 46, "Raspberry Pi 40-pin GPIO header: Nashville Numbers v2 pin usage", 26,
             "start", "bold")
    svg.text(40, 74, "Pi 5 and Pi 4 (same header). Numbers are physical pins, GPIO names are BCM. "
             "Board seen from above, turned so the microSD end is at the top.", 14, fill="#495057")
    bottom = draw_header(svg, usage)
    inset_bottom = draw_board_inset(svg, 830, 180)
    legend_bottom = draw_legends(svg, 790, inset_bottom + 48)
    y = max(bottom + 26, legend_bottom) + 34
    y = draw_warning(svg, y)
    y = draw_usage_table(svg, y + 44, usage)
    svg.text(40, y + 26, "Source: hardware/SPEC.md section 3.1 via tools/wiring_data.py. "
             "Generated by tools/pinout.py; do not edit the SVG by hand.", 12, fill=MUTED)
    return svg.render(), y + 44


def main():
    global H
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("-o", "--output", default=str(Path(__file__).resolve().parent.parent / "pinout.svg"))
    args = ap.parse_args()
    _, needed = build_svg()          # first pass: measure the height
    H = int(needed)
    out, _ = build_svg()
    Path(args.output).write_text(out, encoding="utf-8")
    print(f"pinout: wrote {args.output} ({W}x{H})")


if __name__ == "__main__":
    main()
