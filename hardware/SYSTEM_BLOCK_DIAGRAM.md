# Nashville Numbers - ESP32-S3 System Architecture

**Visual block diagram showing how everything connects**

---

## Complete System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Nashville Numbers - ESP32-S3 Version                │
│                          Single PCB Design                             │
└────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   USB-C     │
                              │  Connector  │
                              └──────┬──────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
                │ 5V                 │                    │ D+/D-
                ▼                    │                    ▼
        ┌───────────────┐            │            ┌──────────────┐
        │  AMS1117-3.3  │            │            │   CP2102N    │
        │   Regulator   │            │            │ USB-to-UART  │
        └───────┬───────┘            │            └──────┬───────┘
                │                    │                   │
                │ 3.3V               │ 5V                │ Serial (TX/RX)
                │                    │                   │ DTR/RTS
                ▼                    ▼                   ▼
        ┌───────────────────────────────────────────────────────┐
        │                                                       │
        │              ESP32-S3-WROOM-1 Module                  │
        │              (Dual-core 240MHz)                       │
        │                                                       │
        │  ┌─────────────────────────────────────────────┐     │
        │  │  Core 0           Core 1                    │     │
        │  │  ▪ I2S Audio     ▪ FFT Processing           │     │
        │  │  ▪ Display       ▪ Chord Detection          │     │
        │  │  ▪ Main loop     ▪ (Future: WiFi/BT)        │     │
        │  └─────────────────────────────────────────────┘     │
        │                                                       │
        │  Features:                                            │
        │  ▪ 8MB Flash memory                                   │
        │  ▪ 512KB SRAM                                         │
        │  ▪ Hardware FFT acceleration                          │
        │  ▪ I2S audio interface                                │
        │  ▪ WiFi 802.11 b/g/n                                  │
        │  ▪ Bluetooth 5.0 (LE)                                 │
        │                                                       │
        └───┬─────────────────────────┬───────────────────┬─────┘
            │                         │                   │
            │ I2S                     │ 2-wire            │ GPIO
            │ (3 signals)             │ Serial            │ (LEDs, buttons)
            ▼                         ▼                   ▼
    ┌──────────────┐         ┌──────────────┐    ┌──────────────┐
    │   INMP441    │         │   TM1637     │    │   Status     │
    │ I2S MEMS Mic │         │  LED Driver  │    │  Indicators  │
    └──────────────┘         └──────┬───────┘    └──────────────┘
            │                       │                    │
            │                       ▼                    │
     Audio Input            ┌──────────────┐     ┌──────┴───────┐
     (Guitar, vocals,       │  4-Digit LED │     │ Power LED    │
      instruments)          │   Display    │     │ Status LED   │
                            └──────────────┘     └──────────────┘
```

---

## Power Distribution Network

```
USB-C Connector (5V Input)
    │
    ├──────────────┬─────────────┬────────────┐
    │              │             │            │
    │              │             │            │
    ▼              ▼             ▼            ▼
[500mA       [AMS1117-3.3]  [TM1637]   [Protection]
 Polyfuse]        │         Display       [TVS Diode]
                  │         (5V OK)       [optional]
                  │
                  │ 3.3V @ 500mA
                  │
    ┌─────────────┴──────────────────┬──────────────┐
    │                                │              │
    ▼                                ▼              ▼
[ESP32-S3]                      [INMP441]      [CP2102N]
  80-280mA                        1.4mA          10mA
  (depends on WiFi)

Total Current Budget:
  ▪ ESP32-S3 active (no WiFi):    80-160mA
  ▪ ESP32-S3 with WiFi:           +80-120mA (peak 280mA)
  ▪ INMP441 microphone:           1.4mA
  ▪ CP2102N USB-UART:             10mA
  ▪ TM1637 + Display:             20-80mA (brightness dependent)
  ─────────────────────────────────────────
  Total typical:                  ~120-270mA
  Total maximum:                  ~400mA

  USB 2.0 provides:               500mA (we're safe!)
```

---

## Audio Signal Path

```
Guitar/Instrument
    │
    ▼
┌─────────────────┐
│  Sound Wave     │  Acoustic audio
│  (Analog)       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         INMP441 I2S MEMS Microphone         │
│                                             │
│  ┌──────────┐      ┌──────┐    ┌────────┐  │
│  │  MEMS    │  →   │ ADC  │ →  │  I2S   │  │
│  │ Element  │      │24-bit│    │ Output │  │
│  └──────────┘      └──────┘    └────┬───┘  │
│                                      │      │
│  Sample rate: 44.1kHz or 48kHz      │      │
│  Bit depth: 24-bit                  │      │
│  Format: I2S stereo (using L only)  │      │
└─────────────────────────────────────┼──────┘
                                      │
                    I2S Bus (3 wires) │
                    ┌─────────────────┤
                    │ SD (Data)       │
                    │ WS (Word Sel)   │
                    │ SCK (Bit Clock) │
                    └─────────────────┤
                                      │
                                      ▼
┌──────────────────────────────────────────────┐
│         ESP32-S3 Audio Processing            │
│                                              │
│  1. I2S DMA Buffer (512-2048 samples)        │
│     ↓                                        │
│  2. Windowing (Hamming/Hann)                │
│     ↓                                        │
│  3. FFT (Fast Fourier Transform)            │
│     - Uses ESP-DSP library                   │
│     - Hardware acceleration                  │
│     - 10x faster than original ESP32         │
│     ↓                                        │
│  4. Frequency Analysis                       │
│     - Identify fundamental frequency         │
│     - Detect harmonics                       │
│     ↓                                        │
│  5. Chord Detection Algorithm                │
│     - Match frequency patterns               │
│     - Nashville number conversion            │
│     ↓                                        │
│  6. Display Output                           │
└──────────────┬───────────────────────────────┘
               │
               ▼
       ┌──────────────┐
       │   TM1637     │
       │  4-Digit     │
       │  Display     │
       └──────────────┘
           Shows: 1, 4, 5, etc.
```

---

## I2S Interface Details

```
INMP441 Microphone              ESP32-S3
┌────────────────┐              ┌────────────────┐
│                │              │                │
│  WS (L/R sel)  ├──────────────┤ GPIO5          │
│                │              │ (I2S0_WS)      │
│                │              │                │
│  SCK (clock)   ├──────────────┤ GPIO6          │
│                │              │ (I2S0_SCK)     │
│                │              │                │
│  SD (data)     ├──────────────┤ GPIO4          │
│                │              │ (I2S0_SDI)     │
│                │              │                │
│  L/R ──[GND]   │              │                │
│  (left channel)│              │                │
└────────────────┘              └────────────────┘

Timing Diagram:
         ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐
SCK:  ───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───  (Bit Clock)

WS:   ─────────────┐           ┌─────────────  (Word Select)
                   └───────────┘
      <─ Left Ch ─>←─ Right ──>

SD:   ──X──X──X──X──X──X──X──X──X──X──X──X──  (Data bits)
         MSB              LSB

Configuration:
  ▪ Sample rate: 44100 Hz
  ▪ Bits per sample: 24
  ▪ Channels: Mono (using left)
  ▪ Format: I2S standard (Philips)
  ▪ Clock: 44100 × 24 × 2 = 2.1168 MHz
```

---

## Display Interface

```
ESP32-S3                         TM1637 Driver
┌────────────┐                   ┌──────────────┐
│            │     CLK           │              │
│  GPIO18    ├───────────────────┤ CLK          │
│            │   (10kΩ pull-up)  │              │
│            │                   │              │
│  GPIO19    ├───────────────────┤ DIO          │
│            │   (10kΩ pull-up)  │              │
└────────────┘                   └──────┬───────┘
                                        │
                                        ▼
                            ┌───────────────────┐
                            │  4-Digit 7-Seg    │
                            │  Common Anode     │
                            │                   │
                            │   ┌─┐  ┌─┐  ┌─┐  │
                            │   │1│  │4│  │5│  │
                            │   └─┘  └─┘  └─┘  │
                            └───────────────────┘

TM1637 Protocol (simplified):
  Start → [CMD] → [DATA] → Stop

  Commands:
    0x40: Write data to display
    0x88-0x8F: Display control (brightness)
    0xC0: Set address (digit 0)

  Example: Display "1"
    START → 0x40 → 0xC0 → 0x06 → STOP
            (write) (addr) (seg)

Segment Mapping (7-segment):
       ┌─ a ─┐
       │     │
       f     b
       │     │
       ├─ g ─┤
       │     │
       e     c
       │     │
       └─ d ─┘

  Digit "1" = segments b,c = 0x06
  Digit "4" = segments b,c,f,g = 0x66
  Digit "5" = segments a,c,d,f,g = 0x6D
```

---

## USB Programming Interface

```
USB-C Port          CP2102N Chip           ESP32-S3
┌──────────┐        ┌────────────┐         ┌──────────┐
│          │        │            │         │          │
│  D+  ────┼────────┤ D+         │         │          │
│  D-  ────┼────────┤ D-         │         │          │
│          │        │            │         │          │
│          │        │  TXD ──────┼─────────┤ GPIO44   │
│          │        │            │         │ (RX)     │
│          │        │  RXD ──────┼─────────┤ GPIO43   │
│          │        │            │         │ (TX)     │
│          │        │            │         │          │
│          │        │            │         │          │
│          │        │  DTR ──────┼───┐     │          │
│          │        │            │   │     │          │
└──────────┘        └────────────┘   │     │          │
                                     │     │          │
                        Auto-reset   │     │          │
                        Circuit:     │     │          │
                                     │     │          │
                            ┌────────┴─────┼──────────┤
                            │ 100nF        │          │
                            │              │  GPIO0   │
                            └──────────────┼──────────┤
                                           │          │
                            ┌──────────────┼──────────┤
                            │ 100nF        │          │
                            │              │  EN      │
                            └──────────────┼──────────┤
                                           │          │
                                     ┌─────┴────┐     │
                                     │  10kΩ    │     │
                                     │          │     │
                                    GND        └──────┘

Auto-programming sequence:
  1. CP2102N asserts DTR LOW
     → GPIO0 pulled LOW via capacitor
     → ESP32 enters bootloader mode

  2. CP2102N toggles RTS
     → EN pin pulsed via capacitor
     → ESP32 resets into bootloader

  3. Upload firmware via serial

  4. DTR returns HIGH
     → GPIO0 returns HIGH (via 10kΩ pulldown)
     → Next reset boots normally
```

---

## Memory Map & Storage

```
ESP32-S3 Memory Architecture:

┌────────────────────────────────────────┐
│         External Flash (8MB)           │  ← Code + Data
├────────────────────────────────────────┤
│  Partition Table:                      │
│  ┌──────────────────────────────────┐  │
│  │ Bootloader      (32KB)           │  │
│  ├──────────────────────────────────┤  │
│  │ Partition Table (4KB)            │  │
│  ├──────────────────────────────────┤  │
│  │ App Firmware    (~1-2MB)         │  │
│  │  - Nashville Numbers code        │  │
│  │  - ESP-DSP library               │  │
│  │  - WiFi/BT stack (optional)      │  │
│  ├──────────────────────────────────┤  │
│  │ OTA Update      (1-2MB)          │  │
│  │  (for future updates)            │  │
│  ├──────────────────────────────────┤  │
│  │ NVS Storage     (20KB)           │  │
│  │  - Settings                      │  │
│  │  - Key config                    │  │
│  │  - Calibration data              │  │
│  ├──────────────────────────────────┤  │
│  │ SPIFFS / LittleFS (remaining)    │  │
│  │  - Future: chord patterns        │  │
│  │  - Future: song database         │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│     Internal SRAM (512KB)              │  ← Fast RAM
├────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │ Heap Memory (~400KB)             │  │
│  │  - Audio buffers                 │  │
│  │  - FFT workspace                 │  │
│  │  - Dynamic allocations           │  │
│  ├──────────────────────────────────┤  │
│  │ Stack (~32KB)                    │  │
│  │  - Core 0 stack                  │  │
│  │  - Core 1 stack                  │  │
│  ├──────────────────────────────────┤  │
│  │ DMA Buffers (~64KB)              │  │
│  │  - I2S audio DMA                 │  │
│  │  - Display buffer                │  │
│  ├──────────────────────────────────┤  │
│  │ Static data (~16KB)              │  │
│  │  - Chord lookup tables           │  │
│  │  - Note frequency map            │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

Typical Memory Usage:
  Audio buffer (2048 samples × 4 bytes):  8KB
  FFT output (1024 bins × 8 bytes):       8KB
  Display buffer:                         512B
  WiFi stack (if enabled):                ~60KB
  Total estimated usage:                  ~100KB
  Remaining for heap:                     ~400KB ✓
```

---

## Software Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Main Application                   │
└──────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Audio Task  │  │  Processing  │  │ Display Task │
│  (Core 0)    │  │  Task        │  │  (Core 0)    │
│              │  │  (Core 1)    │  │              │
│ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │
│ │I2S Driver│ │  │ │   FFT    │ │  │ │ TM1637   │ │
│ │          │ │  │ │ (ESP-DSP)│ │  │ │  Driver  │ │
│ └────┬─────┘ │  │ └────┬─────┘ │  │ └────▲─────┘ │
│      │       │  │      │       │  │      │       │
│      ▼       │  │      ▼       │  │      │       │
│ ┌──────────┐ │  │ ┌──────────┐ │  │      │       │
│ │  DMA     │ │  │ │  Chord   │ │  │      │       │
│ │  Buffer  │ │  │ │Detection │ │  │      │       │
│ └────┬─────┘ │  │ └────┬─────┘ │  │      │       │
│      │       │  │      │       │  │      │       │
└──────┼───────┘  └──────┼───────┘  └──────┼───────┘
       │                 │                 │
       │      Queue      │      Queue      │
       └─────────────────┴─────────────────┘

Task Flow:
  1. I2S DMA fills buffer (continuous)
  2. Buffer full → notify Processing Task
  3. Processing runs FFT
  4. Detect chord from frequency data
  5. Send result to Display Task
  6. Display updates TM1637

FreeRTOS Tasks:
  ┌─────────────────┬──────────┬──────────┬───────┐
  │ Task Name       │ Core     │ Priority │ Stack │
  ├─────────────────┼──────────┼──────────┼───────┤
  │ audio_task      │ Core 0   │ 5 (high) │ 4KB   │
  │ process_task    │ Core 1   │ 4        │ 8KB   │
  │ display_task    │ Core 0   │ 3        │ 2KB   │
  │ idle            │ Both     │ 0 (low)  │ 1KB   │
  └─────────────────┴──────────┴──────────┴───────┘

Queues:
  audio_queue:   audio_task → process_task (2048 samples)
  display_queue: process_task → display_task (chord number)
```

---

## Boot Sequence

```
Power On / Reset
    │
    ▼
┌─────────────────────────────────────┐
│   1. ESP32-S3 ROM Bootloader        │
│      - Checks GPIO0 state           │
│      - GPIO0 LOW → UART download    │
│      - GPIO0 HIGH → Boot from flash │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   2. Second-stage Bootloader        │
│      - Read partition table         │
│      - Verify app firmware          │
│      - Set up memory                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   3. ESP-IDF / Arduino Init         │
│      - Initialize hardware          │
│      - Set up FreeRTOS              │
│      - Start scheduler              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   4. Nashville Numbers Init         │
│      - Load settings from NVS       │
│      - Initialize I2S               │
│      - Initialize TM1637            │
│      - Create tasks                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   5. Main Loop                      │
│      - Process audio continuously   │
│      - Detect chords                │
│      - Update display               │
│      - Handle button presses        │
│      - (Optional: WiFi features)    │
└─────────────────────────────────────┘

Total boot time: ~500ms
  - ROM bootloader: 100ms
  - App init: 300ms
  - Ready to detect: 100ms
```

---

## Future Expansion Possibilities

```
Current Design              Future Additions
──────────────              ────────────────

┌──────────────┐            ┌──────────────┐
│  INMP441 Mic │            │ Line Input   │
└──────────────┘            │ (3.5mm jack) │
                            └──────────────┘

┌──────────────┐            ┌──────────────┐
│ TM1637 4-dig │            │ OLED Display │
└──────────────┘            │ (128×64 px)  │
                            └──────────────┘

┌──────────────┐            ┌──────────────┐
│ USB Program  │            │ WiFi MIDI    │
└──────────────┘            │ BLE Control  │
                            └──────────────┘

Available GPIOs:            Expansion Ideas:
  GPIO1, 2, 3, 7            ▪ Footswitch input
  GPIO8, 9, 10, 11          ▪ Key selector knob
  GPIO12, 13, 14, 15        ▪ Tuner mode LED ring
  GPIO16, 17, 21            ▪ Battery power (LiPo)
  GPIO35-37, 40-42          ▪ Audio output (I2S DAC)
  GPIO45-48                 ▪ SD card storage

ESP32-S3 Capabilities       Possible Features:
  ▪ WiFi 802.11n            ▪ setlist sync
  ▪ Bluetooth 5 LE          ▪ wireless MIDI
  ▪ USB OTG                 ▪ USB MIDI device
  ▪ 2nd I2S channel         ▪ Audio playback
  ▪ Touch sensors           ▪ Touch buttons
  ▪ RTC                     ▪ Battery mode
```

---

## PCB Layers Visualization

```
Top Layer (Component Side):
┌─────────────────────────────────────────────┐
│  [USB-C]                    [INMP441]       │
│                                             │
│  [CP2102N]    [ESP32-S3]       [TM1637]    │
│                                             │
│  [AMS1117]    [Caps]  [Res]    [Display]   │
│                                             │
│  [BTN] [BTN]  [LED]   [LED]                │
└─────────────────────────────────────────────┘

Copper Layers:
┌─────────────────────────────────────────────┐
│ Top Copper:                                 │
│  ▪ Signal traces (I2S, display, serial)     │
│  ▪ Power traces (5V, 3.3V)                  │
│  ▪ Ground fill (where space allows)         │
│                                             │
│ Bottom Copper:                              │
│  ▪ Solid ground plane (90% coverage)        │
│  ▪ Return paths for signals                 │
│  ▪ Connected to top ground via vias         │
└─────────────────────────────────────────────┘

Silkscreen:
┌─────────────────────────────────────────────┐
│  Component labels:                          │
│  U1: ESP32-S3, U2: CP2102N, U3: AMS1117    │
│  MIC1: INMP441, U4: TM1637                 │
│                                             │
│  Pin labels:                                │
│  GPIO numbers, power rails, test points     │
│                                             │
│  Project info:                              │
│  "Nashville Numbers v1.0"                   │
│  "github.com/yourname/nashville-numbers"    │
└─────────────────────────────────────────────┘
```

---

## Design Specifications Summary

### Electrical Characteristics
```
Power Supply:
  Input voltage:        5V DC (USB-C)
  Input current:        400mA max, 200mA typical
  Output voltage:       3.3V ±3%
  Ripple:              <50mV p-p

Audio Performance:
  Frequency response:   20Hz - 20kHz
  Sample rate:          44.1kHz or 48kHz
  Bit depth:           24-bit
  SNR:                 >60dB (INMP441 spec)
  THD:                 <1% (at normal levels)

Digital Signals:
  I2S clock:           2.1168 MHz (44.1kHz mode)
  USB speed:           Full-speed (12 Mbps)
  Display clock:       ~500kHz (TM1637)

Environmental:
  Operating temp:      0°C to 50°C
  Storage temp:        -20°C to 70°C
  Humidity:            10% - 90% non-condensing
```

### Physical Specifications
```
PCB:
  Size:                70mm × 50mm
  Thickness:           1.6mm
  Layers:              2 (top + bottom)
  Copper weight:       1oz (35µm)
  Surface finish:      HASL lead-free
  Soldermask:          Green (or custom color)
  Silkscreen:          White

Components:
  SMT parts:           ~25-30 components
  Through-hole:        0 (all SMT for auto-assembly)
  Package sizes:       0805, 1206, QFN-48, SOIC
  Smallest pitch:      0.5mm (ESP32-S3 QFN)

Mounting:
  Holes:               4× M2.5 (optional)
  Standoff height:     5mm recommended
  Enclosure:           70×50×30mm (3D printed)
```

---

## Comparison: Old vs New Design

```
┌─────────────────────────┬──────────────────┬─────────────────┐
│ Feature                 │ Raspberry Pi     │ ESP32-S3 Custom │
├─────────────────────────┼──────────────────┼─────────────────┤
│ Processor               │ BCM2711 (Pi 4)   │ ESP32-S3        │
│ Clock Speed             │ 1.5GHz (4-core)  │ 240MHz (2-core) │
│ RAM                     │ 2GB              │ 512KB           │
│ Storage                 │ 16GB SD card     │ 8MB flash       │
│ Power Consumption       │ 3-5W             │ 0.5-1W          │
│ Boot Time               │ 30-60 seconds    │ <1 second       │
│ Audio Input             │ USB interface    │ I2S built-in    │
│ Display Interface       │ GPIO bit-bang    │ GPIO bit-bang   │
│ WiFi                    │ Yes              │ Yes             │
│ Bluetooth               │ Yes              │ Yes (BLE)       │
│ Form Factor             │ 85×56mm + modules│ 70×50mm all-in  │
│ Assembly                │ Manual           │ Auto PCBA       │
│ Cost per Unit           │ $54-105          │ $10-12          │
│ IDE / Programming       │ Python (easy)    │ C/C++ (medium)  │
│ Real-time Performance   │ Limited (Linux)  │ Excellent       │
│ Community Support       │ Massive          │ Large           │
└─────────────────────────┴──────────────────┴─────────────────┘

Conclusion: ESP32-S3 is perfect for this dedicated application!
```

---

This system architecture provides a complete custom PCB solution for the Nashville Numbers chord detector at a fraction of the cost of the Raspberry Pi version, while maintaining professional performance and reliability.
