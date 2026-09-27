# Hardware Setup

The hardware documentation now lives next to the design files:

* [`hardware/README.md`](../hardware/README.md) - pick a build, build order,
  the electrical rules that matter
* [`hardware/bom/`](../hardware/bom/README.md) - parts lists with quantities
  and prices
* [`hardware/wiring/`](../hardware/wiring/README.md) - wiring diagrams,
  pin-by-pin tables, soldering, bring-up tests
* [`hardware/enclosures/`](../hardware/enclosures/README.md) - 3D printing
  and assembly
* [`hardware/SPEC.md`](../hardware/SPEC.md) - the design spec behind all of
  the above

> **Version 1 wiring was unsafe for some displays.** It wired the 5 V LCD
> backpack's I2C lines straight to the Pi, suggested powering TM1637 modules
> from 5 V, and drove the MAX7219 directly. All three can put 5 V on a 3.3 V
> GPIO pin. If you built a unit from the old instructions, rewire it following
> [`hardware/wiring/`](../hardware/wiring/README.md).
