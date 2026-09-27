"""Wiring data for the Nashville Numbers v2 builds.

This module transcribes hardware/SPEC.md section 3 (pin map, per-display
wiring, controls) into data.  It is used by:

* tools/pinout.py        - draws pinout.svg (which pin is used by which build)
* tools/check_wiring.py  - checks every WireViz harness (*.yml) against this
                           data and regenerates the pin tables in README.md

If SPEC.md changes, change this file, the matching *.yml harness and run
tools/build.sh; the checker fails until all three agree.

Pin numbers are physical header pins; GPIO numbers are BCM.
Standard library only.
"""

# ---------------------------------------------------------------------------
# Raspberry Pi 40-pin header (Pi 5, Pi 4 and Pi 3B+ share it).
# Pin label as used in the WireViz harnesses and in the pinout drawing.
# ---------------------------------------------------------------------------
HEADER = {
    1: "3V3",          2: "5V",
    3: "GPIO2 SDA",    4: "5V",
    5: "GPIO3 SCL",    6: "GND",
    7: "GPIO4",        8: "GPIO14 TXD",
    9: "GND",          10: "GPIO15 RXD",
    11: "GPIO17",      12: "GPIO18",
    13: "GPIO27",      14: "GND",
    15: "GPIO22",      16: "GPIO23",
    17: "3V3",         18: "GPIO24",
    19: "GPIO10 MOSI", 20: "GND",
    21: "GPIO9 MISO",  22: "GPIO25",
    23: "GPIO11 SCLK", 24: "GPIO8 CE0",
    25: "GND",         26: "GPIO7 CE1",
    27: "GPIO0 ID_SD", 28: "GPIO1 ID_SC",
    29: "GPIO5",       30: "GND",
    31: "GPIO6",       32: "GPIO12",
    33: "GPIO13",      34: "GND",
    35: "GPIO19",      36: "GPIO16",
    37: "GPIO26",      38: "GPIO20",
    39: "GND",         40: "GPIO21",
}

POWER_PINS = {"3V3": (1, 17), "5V": (2, 4), "GND": (6, 9, 14, 20, 25, 30, 34, 39)}

# SPEC.md section 3.1 pin map: header pin -> function key (see COLOURS).
# A build may only use these pins, and only for this function.
SPEC_PIN_MAP = {
    1: "3v3", 17: "3v3",
    2: "5v", 4: "5v",
    **{p: "gnd" for p in POWER_PINS["GND"]},
    3: "sda",           # GPIO2  I2C1 SDA: LCD (via level shifter), HT16K33
    5: "scl",           # GPIO3  I2C1 SCL
    11: "button",       # GPIO17 panel button to GND (pin 9)
    13: "footswitch",   # GPIO27 footswitch tip via 1 kOhm, sleeve to GND (pin 14)
    16: "clk",          # GPIO23 TM1637 CLK
    18: "data",         # GPIO24 TM1637 DIO
    19: "data",         # GPIO10 SPI0 MOSI -> 74AHCT125 -> MAX7219 DIN
    23: "clk",          # GPIO11 SPI0 SCLK -> 74AHCT125 -> MAX7219 CLK
    24: "cs",           # GPIO8  SPI0 CE0  -> 74AHCT125 -> MAX7219 CS
}

# 74AHCT125 quad buffer (DIP-14 / SOIC-14), pins 1..14. OE is active low.
AHCT125_PINS = ["1OE", "1A", "1Y", "2OE", "2A", "2Y", "GND",
                "3Y", "3A", "3OE", "4Y", "4A", "4OE", "VCC"]

# ---------------------------------------------------------------------------
# Wire colour scheme.  One colour per signal, the same in every build.
# The ten colours are exactly those of a standard 40-way "rainbow" Dupont
# jumper ribbon (4 of each colour), so every build can be wired from one
# ribbon.  code = WireViz colour code (WireViz prints VT as "violet").
# hex/ink = fill and text colour used in pinout.svg.
# ---------------------------------------------------------------------------
def _colour(code, name, short, long, hex_, ink):
    return {"code": code, "name": name, "short": short, "long": long,
            "hex": hex_, "ink": ink}


COLOURS = {
    "5v":         _colour("RD", "red", "5 V", "5 V supply", "#e03131", "#ffffff"),
    "3v3":        _colour("OG", "orange", "3.3 V", "3.3 V supply", "#f59f00", "#212529"),
    "gnd":        _colour("BK", "black", "GND", "ground", "#212529", "#ffffff"),
    "sda":        _colour("BU", "blue", "I2C SDA", "I2C data (GPIO2), both sides of the level shifter",
                          "#1971c2", "#ffffff"),
    "scl":        _colour("YE", "yellow", "I2C SCL", "I2C clock (GPIO3), both sides of the level shifter",
                          "#fcc419", "#212529"),
    "button":     _colour("GN", "green", "Button", "panel button (GPIO17)", "#2b8a3e", "#ffffff"),
    "footswitch": _colour("WH", "white", "Footswitch", "footswitch (GPIO27), from the header to the R1/C1 splice",
                          "#ffffff", "#212529"),
    "clk":        _colour("VT", "purple", "Clock", "TM1637 CLK (GPIO23); SPI SCLK (GPIO11) to MAX7219 CLK",
                          "#7048e8", "#ffffff"),
    "data":       _colour("GY", "grey", "Data", "TM1637 DIO (GPIO24); SPI MOSI (GPIO10) to MAX7219 DIN",
                          "#6c757d", "#ffffff"),
    "cs":         _colour("BN", "brown", "Chip select", "SPI CE0 (GPIO8) to MAX7219 CS",
                          "#8b5a2b", "#ffffff"),
}
COLOUR_ORDER = ["5v", "3v3", "gnd", "sda", "scl", "button", "footswitch", "clk", "data", "cs"]
CODE_TO_FUNCTION = {v["code"]: k for k, v in COLOURS.items()}
COLOUR_NAME = {v["code"]: v["name"] for v in COLOURS.values()}

# ---------------------------------------------------------------------------
# Wire kinds.  Every cable (bundle) in a harness is one of these.
# ---------------------------------------------------------------------------
JUMPER_LENGTH_CM = 20
KINDS = {
    "ff":     "Dupont jumper F-F",                       # both housings kept
    "ff_cut": "Dupont jumper F-F, far housing cut off",  # soldered/screwed end
    "mf":     "Dupont jumper M-F",                       # breadboard builds
    "link":   "22 AWG solid-core breadboard link",
}
# what you buy for each kind (ff and ff_cut are the same purchased jumper)
PURCHASE = {
    "ff": "Dupont jumper wire F-F 2.54 mm, 20 cm",
    "ff_cut": "Dupont jumper wire F-F 2.54 mm, 20 cm",
    "mf": "Dupont jumper wire M-F 2.54 mm, 20 cm",
    "link": "Breadboard link wire, 22 AWG solid core",
}


def _c(cable, src, dst, colour, dst_text, note="", src_text=None, role=None):
    """One wire.  src/dst are 'DESIGNATOR:pin-or-label' as in the harness.
    role: short text for the pin-usage tables (defaults to dst_text)."""
    if src_text is None:
        name, pin = src.split(":")
        assert name == "PI", src
        src_text = f"Pi pin {pin} ({HEADER[int(pin)]})"
    return {"cable": cable, "src": src, "dst": dst, "colour": colour,
            "src_text": src_text, "dst_text": dst_text, "note": note,
            "role": role or dst_text}


def _button(cable):
    return [
        _c(cable, "PI:9", "BUTTON:C", "BK", "Panel button, terminal C",
           "either terminal; solder lug or screw terminal", role="Panel button (GND side)"),
        _c(cable, "PI:11", "BUTTON:NO", "GN", "Panel button, terminal NO",
           "internal pull-up, pressed = low", role="Panel button"),
    ]


def _m(src, dst, src_text, dst_text, note=""):
    """A direct joint without a wire (component lead or leg; dashed in the diagram)."""
    return {"src": src, "dst": dst, "src_text": src_text, "dst_text": dst_text, "note": note}


# Footswitch (SPEC.md 3.5): tip -> R1 1 kOhm -> GPIO27, sleeve -> GND, and C1 100 nF
# from the GPIO27 side of R1 to GND, soldered at the jack.  The white lead ends in a
# splice with one lead of R1 and one lead of C1; R1's other lead goes to the TIP lug,
# C1's other lead to the SLEEVE lug together with the black lead.
def _footswitch(cable):
    return [
        _c(cable, "PI:13", "SPLICE:1", "WH", "Splice with R1 and C1, at the jack",
           "white lead ends here; 3.2 mm heat-shrink", role="Footswitch tip"),
        _c(cable, "PI:14", "JACK:S", "BK", "Footswitch jack, sleeve lug",
           "shares the lug with C1", role="Footswitch sleeve"),
    ]


def _footswitch_mates():
    return [
        _m("SPLICE:1", "R1:1", "Splice (white lead)", "R1 (1 kΩ), first lead",
           "soldered together in the splice"),
        _m("R1:1", "JACK:T", "R1 (1 kΩ), second lead", "Footswitch jack, tip lug",
           "resistor lead soldered into the lug"),
        _m("SPLICE:1", "C1:1", "Splice (white lead)", "C1 (100 nF), first lead",
           "soldered together in the splice"),
        _m("C1:1", "JACK:S", "C1 (100 nF), second lead", "Footswitch jack, sleeve lug",
           "capacitor lead soldered into the lug with the black lead"),
    ]


# ---------------------------------------------------------------------------
# The four builds.  'wires' lists every conductor drawn in the harness;
# 'mates' lists direct solder joints without a wire (dashed in the diagram).
# ---------------------------------------------------------------------------
BUILDS = {
    "desktop_lcd": {
        "name": "Desktop",
        "letter": "D",
        "display": "16x2 LCD, PCF8574 I2C backpack, via BSS138 level shifter",
        "bus": "I2C",
        "cables": {
            "W1": ("ff", "Pi to level shifter"),
            "W2": ("ff", "to LCD backpack"),
            "W3": ("ff_cut", "Pi to panel button"),
        },
        "wires": [
            _c("W1", "PI:3", "LS:LV1", "BU", "Level shifter LV1", "I2C data, 3.3 V side"),
            _c("W1", "PI:5", "LS:LV2", "YE", "Level shifter LV2", "I2C clock, 3.3 V side"),
            _c("W1", "PI:1", "LS:LV", "OG", "Level shifter LV",
               "low-side supply: 3.3 V, never 5 V"),
            _c("W1", "PI:25", "LS:GND (LV)", "BK", "Level shifter GND (LV side)"),
            _c("W1", "PI:4", "LS:HV", "RD", "Level shifter HV", "high-side supply: 5 V"),
            _c("W1", "PI:30", "LS:GND (HV)", "BK", "Level shifter GND (HV side)"),
            _c("W2", "PI:6", "LCD:GND", "BK", "LCD backpack GND"),
            _c("W2", "PI:2", "LCD:VCC", "RD", "LCD backpack VCC",
               "5 V for contrast and backlight"),
            _c("W2", "LS:HV1", "LCD:SDA", "BU", "LCD backpack SDA", "I2C data, 5 V side",
               src_text="Level shifter HV1"),
            _c("W2", "LS:HV2", "LCD:SCL", "YE", "LCD backpack SCL", "I2C clock, 5 V side",
               src_text="Level shifter HV2"),
        ] + _button("W3"),
        "mates": [],
    },
    "stage_ht16k33": {
        "name": "Stage",
        "letter": "S",
        "display": 'Adafruit 1.2" 7-segment, HT16K33 I2C backpack',
        "bus": "I2C",
        "cables": {
            "W1": ("ff", "Pi to HT16K33 backpack"),
            "W2": ("ff_cut", "Pi to panel button"),
            "W3": ("ff_cut", "Pi to footswitch jack"),
        },
        "wires": [
            _c("W1", "PI:1", "HT16K33:IO", "OG", "HT16K33 backpack IO",
               "sets the I2C pull-up level: 3.3 V only"),
            _c("W1", "PI:4", "HT16K33:+", "RD", "HT16K33 backpack +", "LED power, 5 V"),
            _c("W1", "PI:6", "HT16K33:−", "BK", "HT16K33 backpack −"),
            _c("W1", "PI:3", "HT16K33:D", "BU", "HT16K33 backpack D", "I2C data"),
            _c("W1", "PI:5", "HT16K33:C", "YE", "HT16K33 backpack C", "I2C clock"),
        ] + _button("W2") + _footswitch("W3"),
        "mates": _footswitch_mates(),
    },
    "budget_tm1637": {
        "name": "Budget",
        "letter": "B",
        "display": "TM1637 4-digit 7-segment module (red)",
        "bus": "GPIO (bit-banged)",
        "cables": {
            "W1": ("ff", "Pi to TM1637 module"),
            "W2": ("ff_cut", "Pi to panel button"),
            "W3": ("ff_cut", "Pi to footswitch jack (optional)"),
        },
        # SPEC.md 1: the footswitch is optional on the Budget build
        "optional_cables": {"W3"},
        "optional_parts": {"SPLICE", "R1", "C1", "JACK"},
        "optional_note": "optional footswitch",
        "wires": [
            _c("W1", "PI:16", "TM1637:CLK", "VT", "TM1637 CLK", "clock"),
            _c("W1", "PI:18", "TM1637:DIO", "GY", "TM1637 DIO",
               "data, open-drain emulation in software"),
            _c("W1", "PI:17", "TM1637:VCC", "OG", "TM1637 VCC",
               "3.3 V only: its pull-ups go to VCC"),
            _c("W1", "PI:20", "TM1637:GND", "BK", "TM1637 GND"),
        ] + _button("W2") + _footswitch("W3"),
        "mates": _footswitch_mates(),
    },
    "legacy_max7219": {
        "name": "Legacy",
        "letter": "L",
        "display": "MAX7219 8-digit 7-segment module via 74AHCT125 buffer",
        "bus": "SPI0",
        "cables": {
            "W1": ("mf", "Pi to breadboard (74AHCT125)"),
            "W2": ("mf", "breadboard to MAX7219"),
            "L1": ("link", "breadboard links to the GND rail"),
            "W3": ("ff_cut", "Pi to panel button"),
        },
        "wires": [
            _c("W1", "PI:2", "U1:14", "RD", "U1 pin 14 (VCC) row", "5 V for U1 and the MAX7219",
               role="5 V to U1 and MAX7219"),
            _c("W1", "PI:6", "U1:7", "BK", "U1 pin 7 (GND) row", role="GND to U1 and MAX7219"),
            _c("W1", "PI:19", "U1:2", "GY", "U1 pin 2 (1A)", "SPI data in",
               role="U1 1A, then MAX7219 DIN"),
            _c("W1", "PI:23", "U1:5", "VT", "U1 pin 5 (2A)", "SPI clock in",
               role="U1 2A, then MAX7219 CLK"),
            _c("W1", "PI:24", "U1:9", "BN", "U1 pin 9 (3A)", "chip select in",
               role="U1 3A, then MAX7219 CS"),
            _c("W2", "U1:14", "MAX7219:VCC", "RD", "MAX7219 VCC", src_text="U1 pin 14 (VCC) row"),
            _c("W2", "U1:7", "MAX7219:GND", "BK", "MAX7219 GND", src_text="U1 pin 7 (GND) row"),
            _c("W2", "U1:3", "MAX7219:DIN", "GY", "MAX7219 DIN", "buffered MOSI, 5 V",
               src_text="U1 pin 3 (1Y)"),
            _c("W2", "U1:8", "MAX7219:CS", "BN", "MAX7219 CS", "buffered CE0, 5 V",
               src_text="U1 pin 8 (3Y)"),
            _c("W2", "U1:6", "MAX7219:CLK", "VT", "MAX7219 CLK", "buffered SCLK, 5 V",
               src_text="U1 pin 6 (2Y)"),
            _c("L1", "U1:7", "RAIL:1", "BK", "Breadboard GND (−) rail", "puts GND on the rail",
               src_text="U1 pin 7 (GND) row"),
            _c("L1", "U1:1", "RAIL:1", "BK", "Breadboard GND (−) rail", "1OE low = enabled",
               src_text="U1 pin 1 (1OE)"),
            _c("L1", "U1:4", "RAIL:1", "BK", "Breadboard GND (−) rail", "2OE low = enabled",
               src_text="U1 pin 4 (2OE)"),
            _c("L1", "U1:10", "RAIL:1", "BK", "Breadboard GND (−) rail", "3OE low = enabled",
               src_text="U1 pin 10 (3OE)"),
            _c("L1", "U1:12", "RAIL:1", "BK", "Breadboard GND (−) rail",
               "unused input must not float", src_text="U1 pin 12 (4A)"),
            _c("L1", "U1:13", "RAIL:1", "BK", "Breadboard GND (−) rail", "4OE low (SPEC: all OE low)",
               src_text="U1 pin 13 (4OE)"),
        ] + _button("W3"),
        # SPEC.md 3.4: 100 nF across U1 VCC and GND (pins 14 and 7); its legs sit in the
        # breadboard rows of those two pins.
        "mates": [
            _m("U1:14", "C2:2", "U1 pin 14 (VCC) row", "C2 (100 nF), one leg",
               "decoupling; the leg plugs into this breadboard row"),
            _m("U1:7", "C2:1", "U1 pin 7 (GND) row", "C2 (100 nF), other leg",
               "decoupling; the leg plugs into this breadboard row"),
        ],
    },
}

BUILD_ORDER = ["desktop_lcd", "stage_ht16k33", "budget_tm1637", "legacy_max7219"]

# Mark what is optional (only the Budget build's footswitch today).
for _b in BUILDS.values():
    _b.setdefault("optional_cables", set())
    _b.setdefault("optional_parts", set())
    _b.setdefault("optional_note", "optional")
    for _w in _b["wires"]:
        _w["optional"] = _w["cable"] in _b["optional_cables"]
    for _mate in _b["mates"]:
        _mate["optional"] = any(end.split(":")[0] in _b["optional_parts"]
                                for end in (_mate["src"], _mate["dst"]))


def pi_pins(build):
    """{pin: wire} for every Pi header pin used by a build."""
    out = {}
    for w in BUILDS[build]["wires"]:
        for end in (w["src"], w["dst"]):
            name, pin = end.split(":")
            if name == "PI":
                assert int(pin) not in out, f"{build}: pin {pin} used twice"
                out[int(pin)] = w
    return out


def pin_usage():
    """{pin: {build: wire}} over all builds."""
    usage = {}
    for b in BUILD_ORDER:
        for pin, w in pi_pins(b).items():
            usage.setdefault(pin, {})[b] = w
    return usage


def pin_function(pin):
    """Function key (see COLOURS) of a used header pin; must be unique."""
    funcs = {CODE_TO_FUNCTION[w["colour"]] for w in pin_usage()[pin].values()}
    assert len(funcs) == 1, f"pin {pin} has conflicting functions {funcs}"
    return funcs.pop()
