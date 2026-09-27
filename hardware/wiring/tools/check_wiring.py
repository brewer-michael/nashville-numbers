#!/usr/bin/env python3
"""Check the WireViz harnesses against tools/wiring_data.py.

For every build (desktop_lcd, stage_ht16k33, budget_tm1637, legacy_max7219)
this parses <build>.yml with WireViz's own parser and fails if

* a wire, its colour or its cable differs from wiring_data.BUILDS,
* a direct solder joint (dashed "mate" line) differs,
* the Pi header pin labels differ from wiring_data.HEADER,
* a header pin is used for anything but its SPEC.md section 3.1 function,
  or its wire colour is not the scheme colour for that function,
* a cable's type does not match its kind (F-F, F-F cut, M-F, link),
* the jumper counts in additional_bom_items differ from the wires drawn.

It also generates the pin-by-pin tables and jumper counts in README.md
(between "<!-- BEGIN GENERATED: ... -->" / "<!-- END GENERATED: ... -->").
Without --update-readme a stale README is an error.

Usage:  python3 tools/check_wiring.py [--update-readme]
Needs:  wireviz 0.4.1 (and its dependency PyYAML).
"""

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIRING = HERE.parent
sys.path.insert(0, str(HERE))

import wiring_data as wd  # noqa: E402

try:
    import yaml
    from wireviz import wireviz as wv
except ImportError as exc:  # pragma: no cover
    sys.exit(f"check_wiring: {exc}. Install WireViz 0.4.1: pip install wireviz==0.4.1")

KIND_TYPE = {  # the cable 'type' each kind must use in the harness
    "ff": "Dupont jumper F-F",
    "ff_cut": "Dupont jumper F-F, far housing cut off",
    "mf": "Dupont jumper M-F",
    "link": "Breadboard link, 22 AWG solid core",
}

errors = []


def err(build, msg):
    errors.append(f"{build}: {msg}")


def resolve(harness, ref):
    """'NAME:pin-or-label' -> (NAME, pin id), the way WireViz resolves it."""
    name, token = ref.split(":", 1)
    if name not in harness.connectors:
        raise KeyError(f"{ref}: part {name} is not in the harness")
    conn = harness.connectors[name]
    if token in conn.pins:
        return name, token
    if token.isdigit() and int(token) in conn.pins:
        return name, int(token)
    if token in conn.pinlabels:
        return name, conn.pins[conn.pinlabels.index(token)]
    raise KeyError(f"{ref}: no such pin or label")


def fmt(ends):
    return " <-> ".join(sorted(f"{n}:{p}" for n, p in ends))


def check_build(build):
    spec = wd.BUILDS[build]
    path = WIRING / f"{build}.yml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    harness = wv.parse(path, return_types="harness")

    # --- Pi header labels -------------------------------------------------
    pi = harness.connectors["PI"]
    if pi.pins != list(range(1, 41)):
        err(build, "PI must define pins 1..40")
    want = [wd.HEADER[p] for p in range(1, 41)]
    for p, (got, exp) in enumerate(zip(pi.pinlabels, want), 1):
        if got != exp:
            err(build, f"PI pin {p} label {got!r}, expected {exp!r}")
    if "U1" in harness.connectors and harness.connectors["U1"].pinlabels != wd.AHCT125_PINS:
        err(build, "U1 pin labels do not match the 74AHCT125 pinout")

    # --- cables: kinds and types ------------------------------------------
    if set(harness.cables) != set(spec["cables"]):
        err(build, f"cables {sorted(harness.cables)} != {sorted(spec['cables'])}")
    for name, (kind, _) in spec["cables"].items():
        cable = harness.cables.get(name)
        if cable is not None and cable.type != KIND_TYPE[kind]:
            err(build, f"{name} type {cable.type!r}, expected {KIND_TYPE[kind]!r}")

    # --- wires drawn vs. expected -------------------------------------------
    drawn = Counter()
    for cname, cable in harness.cables.items():
        ends = defaultdict(set)
        for con in cable.connections:
            for n, p in ((con.from_name, con.from_pin), (con.to_name, con.to_pin)):
                if n is not None:
                    ends[con.via_port].add((n, p))
        for wire in range(1, cable.wirecount + 1):
            if len(ends[wire]) != 2:
                err(build, f"{cname} wire {wire} has {len(ends[wire])} ends (expected 2)")
                continue
            drawn[(cname, cable.colors[wire - 1], frozenset(ends[wire]))] += 1
    expected = Counter()
    for w in spec["wires"]:
        try:
            ends = frozenset((resolve(harness, w["src"]), resolve(harness, w["dst"])))
        except KeyError as exc:
            err(build, str(exc))
            continue
        expected[(w["cable"], w["colour"], ends)] += 1
    for key in expected - drawn:
        err(build, f"missing wire {key[0]} {key[1]} {fmt(key[2])}")
    for key in drawn - expected:
        err(build, f"unexpected wire {key[0]} {key[1]} {fmt(key[2])}")

    # --- direct joints (mates) ----------------------------------------------
    got = {frozenset(((m.from_name, m.from_pin), (m.to_name, m.to_pin))) for m in harness.mates}
    want = set()
    for m in spec["mates"]:
        try:
            want.add(frozenset((resolve(harness, m["src"]), resolve(harness, m["dst"]))))
        except KeyError as exc:
            err(build, f"missing direct joint {m['src']} <-> {m['dst']} ({exc.args[0]})")
    for m in want - got:
        err(build, f"missing direct joint {fmt(m)}")
    for m in got - want:
        err(build, f"unexpected direct joint {fmt(m)}")

    # --- header pins: SPEC function and colour ------------------------------
    for pin, w in wd.pi_pins(build).items():
        func = wd.SPEC_PIN_MAP.get(pin)
        if func is None:
            err(build, f"Pi pin {pin} is not in the SPEC.md 3.1 pin map")
        elif w["colour"] != wd.COLOURS[func]["code"]:
            err(build, f"Pi pin {pin} ({func}) wire is {w['colour']}, "
                       f"scheme says {wd.COLOURS[func]['code']}")

    # --- BOM jumper counts ----------------------------------------------------
    want_bom = jumper_counts(build)
    got_bom = {}
    for item in raw.get("additional_bom_items", []):
        desc = item["description"]
        if desc.startswith(("Dupont jumper wire", "Breadboard link wire")):
            got_bom[desc] = (item["qty"], sorted(item.get("designators", [])))
    for desc in sorted(set(want_bom) | set(got_bom)):
        w_ = want_bom.get(desc)
        g_ = got_bom.get(desc)
        w_cmp = (w_["qty"], w_["designators"]) if w_ else None
        if w_cmp != g_:
            err(build, f"BOM item {desc!r}: harness says {g_}, wires need {w_cmp}")


def jumper_counts(build):
    """{BOM description: entry} for the jumpers and links of one build.
    Optional wires get their own BOM line, e.g. '..., black (optional footswitch)'."""
    spec = wd.BUILDS[build]
    out = {}
    for w in spec["wires"]:
        kind = spec["cables"][w["cable"]][0]
        colour = wd.COLOUR_NAME[w["colour"]]
        desc = f"{wd.PURCHASE[kind]}, {colour}"
        if w["optional"]:
            desc += f" ({spec['optional_note']})"
        e = out.setdefault(desc, {"qty": 0, "cut": 0, "designators": set(), "kind": kind,
                                  "item": wd.PURCHASE[kind], "colour": colour,
                                  "optional": w["optional"]})
        e["qty"] += 1
        e["cut"] += kind == "ff_cut"
        e["designators"].add(w["cable"])
    for e in out.values():
        e["designators"] = sorted(e["designators"])
    return out


# ---------------------------------------------------------------------------
# README generation
# ---------------------------------------------------------------------------
def md_wiring_table(build):
    spec = wd.BUILDS[build]
    rows = ["| Cable | From | To | Wire colour | Notes |", "|---|---|---|---|---|"]
    opt = f" ({spec['optional_note']})"
    for w in spec["wires"]:
        cable = f"{w['cable']}{opt if w['optional'] else ''}"
        rows.append(f"| {cable} | {w['src_text']} | {w['dst_text']} | "
                    f"{wd.COLOUR_NAME[w['colour']]} | {w['note']} |")
    for m in spec["mates"]:
        cable = f"none{opt if m['optional'] else ''}"
        rows.append(f"| {cable} | {m['src_text']} | {m['dst_text']} | "
                    f"component lead, no wire | {m['note']} |")
    return "\n".join(rows)


def md_jumper_table(build):
    rows = ["| Qty | Item | Colour | Cables | Notes |", "|---:|---|---|---|---|"]
    items = [wd.PURCHASE[k] for k in ("ff", "mf", "link")]
    colours = [wd.COLOURS[k]["name"] for k in wd.COLOUR_ORDER]

    def order(e):
        return e["optional"], items.index(e["item"]), colours.index(e["colour"])

    for e in sorted(jumper_counts(build).values(), key=order):
        notes = []
        if e["optional"]:
            notes.append(f"**{wd.BUILDS[build]['optional_note']}**")
        if e["cut"] == e["qty"]:
            notes.append("far housing cut off" if e["qty"] == 1 else "all with the far housing cut off")
        elif e["cut"]:
            notes.append(f"{e['cut']} of them with the far housing cut off")
        rows.append(f"| {e['qty']} | {e['item']} | {e['colour']} | {', '.join(e['designators'])} | "
                    f"{'; '.join(notes)} |")
    return "\n".join(rows)


def md_pin_usage_table():
    names = [wd.BUILDS[b]["name"] for b in wd.BUILD_ORDER]
    rows = ["| Pin | Name | Function (wire colour) | " + " | ".join(names) + " |",
            "|---:|---|---|" + "---|" * len(names)]
    usage = wd.pin_usage()
    for pin in sorted(usage):
        colour = wd.COLOURS[wd.pin_function(pin)]
        cells = [(usage[pin][b]["role"] + (" (optional)" if usage[pin][b]["optional"] else ""))
                 if b in usage[pin] else "" for b in wd.BUILD_ORDER]
        rows.append(f"| {pin} | {wd.HEADER[pin]} | {colour['short']} ({colour['name']}) | "
                    + " | ".join(cells) + " |")
    return "\n".join(rows)


def md_colour_table():
    pins = {}
    for pin in wd.pin_usage():
        pins.setdefault(wd.pin_function(pin), []).append(pin)
    rows = ["| Wire colour | Signal | Header pins | WireViz code |", "|---|---|---|---|"]
    for key in wd.COLOUR_ORDER:
        c = wd.COLOURS[key]
        name = "purple (WireViz prints *violet*)" if key == "clk" else c["name"]
        rows.append(f"| **{name}** | {c['long']} | {', '.join(map(str, sorted(pins.get(key, []))))} "
                    f"| `{c['code']}` |")
    return "\n".join(rows)


def generated_blocks():
    blocks = {"colour scheme": md_colour_table(), "pin usage": md_pin_usage_table()}
    for b in wd.BUILD_ORDER:
        blocks[f"{b} wiring"] = md_wiring_table(b)
        blocks[f"{b} jumpers"] = md_jumper_table(b)
    return blocks


def sync_readme(update):
    readme = WIRING / "README.md"
    text = readme.read_text(encoding="utf-8")
    new = text
    for key, body in generated_blocks().items():
        k = re.escape(key)
        pat = re.compile(rf"(<!-- BEGIN GENERATED: {k} -->\n).*?(<!-- END GENERATED: {k} -->)", re.S)
        if not pat.search(new):
            errors.append(f"README.md: marker block '{key}' not found")
            continue
        new = pat.sub(lambda m, body=body: m.group(1) + body + "\n" + m.group(2), new)
    if new != text:
        if update:
            readme.write_text(new, encoding="utf-8")
            print("check_wiring: README.md tables regenerated")
        else:
            errors.append("README.md tables are stale: run tools/check_wiring.py --update-readme")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--update-readme", action="store_true",
                    help="rewrite the generated tables in README.md")
    args = ap.parse_args()
    for pin in wd.pin_usage():
        wd.pin_function(pin)  # asserts one function per header pin across builds
    for build in wd.BUILD_ORDER:
        check_build(build)
    sync_readme(args.update_readme)
    if errors:
        print("check_wiring: FAILED", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)
        return 1
    n = sum(len(wd.BUILDS[b]["wires"]) for b in wd.BUILD_ORDER)
    print(f"check_wiring: OK ({len(wd.BUILD_ORDER)} harnesses, {n} wires match SPEC data)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
