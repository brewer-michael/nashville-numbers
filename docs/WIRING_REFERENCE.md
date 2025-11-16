# Wiring Reference - Quick Guide

Quick reference for connecting displays to Raspberry Pi GPIO.

## Raspberry Pi GPIO Pinout (40-pin header)

```
    3.3V  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
    3.3V (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

## LCD Display (I2C) - 4 Wires

### Connection Table

| LCD Module | Pin # | GPIO # | Wire Color (typical) |
|------------|-------|--------|----------------------|
| VCC        | 2     | 5V     | Red                  |
| GND        | 6     | GND    | Black                |
| SDA        | 3     | GPIO2  | Blue/Green           |
| SCL        | 5     | GPIO3  | Yellow/White         |

### Visual Diagram

```
LCD Module          Raspberry Pi
┌────────┐          ┌─────────────┐
│        │          │  [1] [2]    │
│  16x2  │          │  3V  5V ←───┼─── VCC (Red)
│  LCD   │          │  [3] [4]    │
│        │  SDA ────┼─→ SDA 5V    │
│        │          │  [5] [6]    │
│        │  SCL ────┼─→ SCL GND ←─┼─── GND (Black)
│        │          │      ...    │
└────────┘          └─────────────┘
VCC GND SDA SCL
```

### I2C Address Detection

```bash
sudo i2cdetect -y 1
```

Common addresses:
- `0x27` (39 decimal) - Most common
- `0x3F` (63 decimal) - Alternative

## TM1637 LED Display - 4 Wires

### Connection Table

| TM1637 Pin | Pin # | GPIO # | Wire Color (typical) |
|------------|-------|--------|----------------------|
| VCC        | 1     | 3.3V   | Red                  |
| GND        | 6     | GND    | Black                |
| CLK        | 16    | GPIO23 | Yellow               |
| DIO        | 18    | GPIO24 | Green                |

**Note**: Some TM1637 modules require 5V instead of 3.3V. Check your module specs!

### Visual Diagram

```
TM1637 Module       Raspberry Pi
┌────────────┐      ┌─────────────┐
│            │      │  [1] [2]    │
│ ┌────────┐ │      │  3V3 5V     │
│ │ 8 8 8 8│ │      │  [3] [4]    │
│ └────────┘ │      │      5V     │
│  4-Digit   │      │  [5] [6]    │
│   7-Seg    │      │      GND ←──┼─── GND (Black)
│            │      │      ...    │
└────────────┘      │ [15][16]    │
                    │     GPIO23 ←┼─── CLK (Yellow)
VCC GND CLK DIO     │ [17][18]    │
 │   │   │   │      │     GPIO24 ←┼─── DIO (Green)
 │   │   │   └──────┼→            │
 │   │   └──────────┼→            │
 │   └──────────────┼→            │
 └──────────────────┼→ (1)        │
                    └─────────────┘
```

### Configuration

Default GPIO pins (can be changed in config.json):
```json
"clk_pin": 23,
"dio_pin": 24
```

## MAX7219 LED Display - 5 Wires (SPI)

### Connection Table

| MAX7219 Pin | Pin # | GPIO #  | SPI Function | Wire Color (typical) |
|-------------|-------|---------|--------------|----------------------|
| VCC         | 2     | 5V      | Power        | Red                  |
| GND         | 6     | GND     | Ground       | Black                |
| DIN         | 19    | GPIO10  | MOSI         | Blue                 |
| CS          | 24    | GPIO8   | CE0          | Green                |
| CLK         | 23    | GPIO11  | SCLK         | Yellow               |

### Visual Diagram

```
MAX7219 Module           Raspberry Pi
┌──────────────────┐     ┌─────────────┐
│                  │     │  [1] [2]    │
│ ┌──────────────┐ │     │  3V3 5V ←───┼─── VCC (Red)
│ │ 8 8 8 8 8 8  │ │     │  [3] [4]    │
│ └──────────────┘ │     │      5V     │
│   8-Digit LED    │     │  [5] [6]    │
│                  │     │      GND ←──┼─── GND (Black)
└──────────────────┘     │      ...    │
                         │ [19][20]    │
VCC GND DIN CS CLK       │ DIN  GND    │
 │   │   │   │   │       │ [21][22]    │
 │   │   │   │   │       │      ...    │
 │   │   │   │   └───────┼→[23][24]    │
 │   │   │   │           │ CLK  CS ←───┼─── CS (Green)
 │   │   │   └───────────┼→            │
 │   │   └───────────────┼→            │
 │   └───────────────────┼→            │
 └───────────────────────┼→ (2)        │
                         └─────────────┘
```

### SPI Configuration

Enable SPI:
```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

Verify:
```bash
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

## Complete Stage Setup - LED Display

```
┌─────────────────────────────────────────────────────┐
│                 STAGE FLOOR                         │
│                                                     │
│              ┌─────────────────┐                    │
│              │   TM1637 LED    │                    │
│              │  ┌───────────┐  │                    │
│              │  │    1      │  │  ← Large red       │
│              │  └───────────┘  │     digits visible │
│              └─────────────────┘     from stage     │
│                      ▲                              │
│                      │ (extension cable)            │
│                      │                              │
│              ┌───────┴────────┐                     │
│              │  Raspberry Pi  │                     │
│              │     + USB      │                     │
│              │     Audio      │                     │
│              └────────────────┘                     │
│                      ▲                              │
│                      │ (audio cable)                │
│                      │                              │
│              ┌───────┴────────┐                     │
│              │   Microphone   │                     │
│              │   (near amp)   │                     │
│              └────────────────┘                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Practice Room Setup - LCD Display

```
┌─────────────────────────────────────────────┐
│              DESKTOP/TABLE                  │
│                                             │
│  ┌──────────────┐    ┌─────────────────┐   │
│  │  LCD Display │    │  Raspberry Pi   │   │
│  │ ┌──────────┐ │    │   + USB Audio   │   │
│  │ │Chord: 1 C│ │────│                 │   │
│  │ │Key:C Maj │ │    │      ┌─────┐    │   │
│  │ └──────────┘ │    │      │ USB │    │   │
│  └──────────────┘    └──────┴─────┴────┘   │
│                             ▲               │
│                             │ USB cable     │
│                             │               │
│                      ┌──────┴──────┐        │
│                      │   USB Mic   │        │
│                      └─────────────┘        │
│                                             │
└─────────────────────────────────────────────┘
```

## Power Distribution

### Option 1: All powered by Raspberry Pi
```
[Power Supply 5V 3A]
         │
         ▼
  [Raspberry Pi]
    │    │    │
    │    │    └─→ [Display] (via GPIO)
    │    └──────→ [USB Audio Interface]
    └───────────→ System
```

### Option 2: Separate power for bright displays
```
[Power Supply 5V 3A]        [Power Supply 5V 2A]
         │                            │
         ▼                            ▼
  [Raspberry Pi]              [MAX7219 Display]
    │    │                            ▲
    │    └──→ [USB Audio]             │
    │                                 │
    └─→ Signal pins (DIN, CS, CLK) ───┘
        (GND shared)
```

## Cable Length Guidelines

| Connection Type | Maximum Recommended Length | Notes                    |
|----------------|----------------------------|--------------------------|
| I2C (LCD)      | 1 meter (3 feet)           | Add pull-up resistors    |
| TM1637         | 2 meters (6 feet)          | Use shielded cable       |
| MAX7219 (SPI)  | 3 meters (10 feet)         | Better for long runs     |
| USB Audio      | 5 meters (16 feet)         | Use quality USB cable    |

## Troubleshooting Quick Check

### Display not working?

**LCD (I2C)**
1. Check 4 connections: VCC, GND, SDA, SCL
2. Run: `sudo i2cdetect -y 1`
3. Verify I2C address matches config

**TM1637**
1. Check 4 connections: VCC, GND, CLK, DIO
2. Try 5V instead of 3.3V if not working
3. Verify GPIO pins in config: CLK=23, DIO=24

**MAX7219**
1. Check 5 connections: VCC, GND, DIN, CS, CLK
2. Verify SPI enabled: `ls /dev/spi*`
3. Check VCC connected to 5V (not 3.3V)

### Audio not detected?

1. Check USB connection
2. Run: `arecord -l`
3. Test: `arecord -D plughw:1,0 -f cd test.wav`

## Safety Notes

1. **Power off** Raspberry Pi before connecting/disconnecting displays
2. **Double-check** wiring before powering on
3. **Avoid short circuits** between 5V/3.3V and GND
4. **Use proper power supply** - underpowering causes instability
5. **ESD protection** - ground yourself before handling components

## Reference Resources

- [Raspberry Pi Pinout](https://pinout.xyz/)
- [I2C Tools](https://i2c.wiki.kernel.org/index.php/I2C_Tools)
- [SPI Documentation](https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/)
