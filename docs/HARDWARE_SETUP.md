# Hardware Setup Guide

This guide covers the hardware components and wiring needed for the Nashville Numbers chord detection system.

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Raspberry Pi Setup](#raspberry-pi-setup)
3. [Audio Input Options](#audio-input-options)
4. [LCD Display Setup](#lcd-display-setup)
5. [LED Display Setup](#led-display-setup)
6. [Wiring Diagrams](#wiring-diagrams)
7. [Power Considerations](#power-considerations)
8. [Troubleshooting](#troubleshooting)

## Hardware Requirements

### Core Components

#### Raspberry Pi
- **Recommended**: Raspberry Pi 4 Model B (2GB or more)
- **Minimum**: Raspberry Pi 3B+
- **OS**: Raspberry Pi OS (Debian-based)

**Why not Arduino?**
Real-time chord detection requires significant processing power for FFT analysis and pattern matching. Arduino boards lack the CPU and memory needed for this task. Raspberry Pi provides:
- Sufficient CPU for real-time audio processing
- USB audio support
- Easy Python development
- GPIO for displays

#### microSD Card
- 16GB minimum, 32GB recommended
- Class 10 or better for good performance

#### Power Supply
- Official Raspberry Pi power supply (5V, 3A for Pi 4)
- Or quality USB-C/Micro-USB power adapter

### Audio Input (Choose One)

#### Option 1: USB Audio Interface (Recommended)
- **Behringer U-Control UCA202** (~$30)
- **Behringer UFO202** (~$40)
- **Focusrite Scarlett Solo** (~$110, professional option)

**Advantages**: Better audio quality, line-level inputs, low latency

#### Option 2: USB Microphone
- **Blue Snowball** (~$50)
- **Samson Meteor** (~$70)
- **Audio-Technica ATR2100** (~$100)

**Advantages**: Simple setup, all-in-one solution

#### Option 3: Raspberry Pi Audio HAT
- **HiFiBerry DAC+ ADC** (~$45)
- **Justboom Audio Zero** (~$25)

**Advantages**: Clean integration, good quality, no USB needed

### Display Options

You need ONE of the following displays:

#### Option 1: LCD Display (16x2 with I2C)
- **Part**: HD44780 16x2 LCD with I2C backpack (PCF8574)
- **Cost**: ~$8-15
- **Vendors**: Amazon, Adafruit, SparkFun
- **Connections**: 4 wires (VCC, GND, SDA, SCL)

**Best for**: Practice rooms, desktop use, detailed information

#### Option 2: TM1637 LED Display (Stage-Friendly)
- **Part**: TM1637 4-digit 7-segment display (red)
- **Cost**: ~$3-8
- **Vendors**: Amazon, AliExpress
- **Size options**: 0.36", 0.56" (larger is better for stage)
- **Connections**: 4 wires (VCC, GND, CLK, DIO)

**Best for**: Stage use, high visibility, low light conditions

#### Option 3: MAX7219 LED Display (Professional)
- **Part**: MAX7219 8-digit 7-segment display
- **Cost**: ~$8-12
- **Vendors**: Amazon, AliExpress
- **Connections**: 5 wires (VCC, GND, DIN, CS, CLK)

**Best for**: Large stages, more display space, brighter output

### Optional Components

- Breadboard and jumper wires (for prototyping)
- Case for Raspberry Pi
- Microphone stand mount
- Extension cables for display placement

## Raspberry Pi Setup

### Initial Configuration

1. **Install Raspberry Pi OS**
   - Download from [raspberrypi.com](https://www.raspberrypi.com/software/)
   - Use Raspberry Pi Imager to write to SD card
   - Choose "Raspberry Pi OS (32-bit)" or "Raspberry Pi OS Lite"

2. **Enable I2C (for LCD displays)**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options > I2C > Enable
   sudo reboot
   ```

3. **Enable SPI (for MAX7219 displays)**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options > SPI > Enable
   sudo reboot
   ```

4. **Update System**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

### Install System Dependencies

```bash
# Audio libraries
sudo apt install -y portaudio19-dev python3-pyaudio

# I2C tools (for LCD)
sudo apt install -y i2c-tools python3-smbus

# Python development
sudo apt install -y python3-pip python3-dev python3-numpy python3-scipy

# GPIO and display libraries
sudo apt install -y python3-rpi.gpio
```

## Audio Input Options

### USB Audio Interface Setup

1. **Connect the interface**
   - Plug USB cable into Raspberry Pi
   - Connect instrument/microphone to interface input
   - Set input gain appropriately (start at 50%)

2. **Verify detection**
   ```bash
   arecord -l
   # Should show your USB audio device
   ```

3. **Test recording**
   ```bash
   arecord -D plughw:1,0 -d 5 -f cd test.wav
   aplay test.wav
   ```

4. **Find device index**
   ```bash
   python3 -c "import pyaudio; p=pyaudio.PyAudio(); \
   [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') \
   for i in range(p.get_device_count())]"
   ```

### USB Microphone Setup

1. **Connect microphone**
   - Plug directly into Raspberry Pi USB port
   - Position 1-2 feet from instrument/amp

2. **Adjust gain** (if available)
   - Use alsamixer: `alsamixer`
   - Select USB device (F6)
   - Adjust capture level

### Raspberry Pi Audio HAT Setup

Refer to manufacturer documentation for your specific HAT:
- HiFiBerry: [hifiberry.com/docs](https://www.hifiberry.com/docs/)
- JustBoom: [justboom.co/guides](https://www.justboom.co/)

## LCD Display Setup

### 16x2 I2C LCD

#### Components
- HD44780 16x2 LCD with I2C backpack
- 4 female-to-female jumper wires

#### Wiring

| LCD Pin | Raspberry Pi Pin | BCM Pin | Description |
|---------|------------------|---------|-------------|
| VCC     | Pin 2            | 5V      | Power       |
| GND     | Pin 6            | GND     | Ground      |
| SDA     | Pin 3            | GPIO 2  | I2C Data    |
| SCL     | Pin 5            | GPIO 3  | I2C Clock   |

#### Find I2C Address

```bash
sudo i2cdetect -y 1
```

Common addresses:
- 0x27 (most common)
- 0x3F (alternative)

Update `config.json` with your address:
```json
"display": {
    "lcd": {
        "i2c_address": 39  // 0x27 in decimal
    }
}
```

#### Test LCD

```python
python3 << EOF
from RPLCD.i2c import CharLCD
lcd = CharLCD('PCF8574', 0x27)
lcd.write_string('Nashville\nNumbers!')
EOF
```

## LED Display Setup

### Option 1: TM1637 4-Digit Display

#### Components
- TM1637 LED display module
- 4 female-to-female jumper wires

#### Wiring

| TM1637 Pin | Raspberry Pi Pin | BCM Pin | Description |
|------------|------------------|---------|-------------|
| VCC        | Pin 1            | 3.3V    | Power       |
| GND        | Pin 6            | GND     | Ground      |
| CLK        | Pin 16           | GPIO 23 | Clock       |
| DIO        | Pin 18           | GPIO 24 | Data        |

**Note**: Some TM1637 modules may require 5V. Check your module specifications.

#### Configuration

Edit `config.json`:
```json
"display": {
    "type": "led",
    "led": {
        "display_type": "TM1637",
        "clk_pin": 23,
        "dio_pin": 24,
        "brightness": 7
    }
}
```

#### Test TM1637

```python
python3 << EOF
from tm1637 import TM1637
display = TM1637(clk=23, dio=24)
display.brightness(7)
display.write([1, 2, 3, 4])
EOF
```

### Option 2: MAX7219 8-Digit Display

#### Components
- MAX7219 LED matrix module
- 5 female-to-female jumper wires

#### Wiring (SPI Connection)

| MAX7219 Pin | Raspberry Pi Pin | BCM Pin  | Description |
|-------------|------------------|----------|-------------|
| VCC         | Pin 2            | 5V       | Power       |
| GND         | Pin 6            | GND      | Ground      |
| DIN         | Pin 19           | GPIO 10  | SPI MOSI    |
| CS          | Pin 24           | GPIO 8   | SPI CE0     |
| CLK         | Pin 23           | GPIO 11  | SPI CLK     |

#### Configuration

Edit `config.json`:
```json
"display": {
    "type": "led",
    "led": {
        "display_type": "MAX7219",
        "brightness": 7
    }
}
```

## Wiring Diagrams

### Complete System with LCD Display

```
┌─────────────────────────────────────┐
│      Raspberry Pi 4/3B+             │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ GPIO Header (Top View)       │  │
│  │                              │  │
│  │  3.3V  [1] [2]  5V  ────────┼──┼─── LCD VCC
│  │   SDA  [3] [4]  5V           │  │
│  │   SCL  [5] [6]  GND ─────────┼──┼─── LCD GND
│  │        ...     ...            │  │
│  │        [15][16] GPIO23 ───────   │
│  │        [17][18] GPIO24           │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────┐              │
│  │  USB Audio       │              │
│  │  Interface       │              │
│  └──────────────────┘              │
│                                     │
└─────────────────────────────────────┘
         │
         SDA ───── LCD SDA
         SCL ───── LCD SCL

    [Instrument/Mic] ──→ [USB Audio] ──→ [Raspberry Pi]
                                              │
                                              ↓
                                          [LCD Display]
                                       "Chord: 1    C"
                                       "Key: C Maj 95%"
```

### Complete System with TM1637 LED Display

```
┌─────────────────────────────────────┐
│      Raspberry Pi 4/3B+             │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ GPIO Header                  │  │
│  │                              │  │
│  │  3.3V  [1] [2]  5V           │  │
│  │        [3] [4]  5V           │  │
│  │        [5] [6]  GND ─────────┼──┼─── LED GND
│  │        ...     ...            │  │
│  │        [15][16] GPIO23 ───────┼──┼─── LED CLK
│  │        [17][18] GPIO24 ───────┼──┼─── LED DIO
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘

    ┌──────────────────────┐
    │  TM1637 LED Display  │
    │                      │
    │  ┌────────────────┐  │
    │  │  [  1  ]       │  │  ← Large red 7-segment digits
    │  └────────────────┘  │
    │                      │
    │ CLK DIO VCC GND      │
    └──────────────────────┘
```

## Power Considerations

### Current Requirements

- **Raspberry Pi 4**: Up to 3A (under load)
- **Raspberry Pi 3B+**: Up to 2.5A
- **LCD Display**: ~20mA
- **TM1637 Display**: ~80mA (all segments on)
- **MAX7219 Display**: ~300mA (all segments on, max brightness)
- **USB Audio Interface**: ~100-500mA

### Power Supply Recommendations

#### Desktop/Practice Room Use
- Use official Raspberry Pi power supply
- Connect displays to GPIO (powered by Pi)
- Total: One power adapter needed

#### Stage Use (with bright LED display)
- Consider separate 5V power supply for MAX7219
- Reduces load on Raspberry Pi
- Improves stability during performances

#### Portable/Battery Operation
- Use USB power bank (10000mAh+)
- Look for 2.4A+ output
- Runtime: 3-5 hours typical

## Troubleshooting

### Audio Issues

**No audio detected**
1. Check USB connection
2. Verify device with `arecord -l`
3. Test with `arecord -D plughw:1,0 -f cd test.wav`
4. Check input gain settings

**Poor detection accuracy**
1. Increase input gain
2. Position mic closer to sound source
3. Reduce background noise
4. Check for clipping (distortion)

### LCD Display Issues

**Display not found (I2C error)**
1. Check wiring connections
2. Verify I2C is enabled: `sudo raspi-config`
3. Scan for device: `sudo i2cdetect -y 1`
4. Try alternative address (0x27 or 0x3F)
5. Check solder joints on I2C backpack

**Garbled text**
1. Check I2C address in config
2. Verify VCC is connected to 5V
3. Add pull-up resistors (4.7kΩ) if using long cables

**Backlight on, no text**
1. Adjust contrast potentiometer on I2C backpack
2. Check library installation: `pip3 install RPLCD`

### LED Display Issues

**TM1637 not responding**
1. Check wiring (CLK and DIO)
2. Some modules need 5V instead of 3.3V
3. Test with example code
4. Verify GPIO pins in config match wiring

**MAX7219 not responding**
1. Verify SPI is enabled
2. Check VCC is connected to 5V
3. Test SPI: `ls /dev/spi*`
4. Check library: `pip3 install luma.led-matrix`

**Display too dim/bright**
1. Adjust brightness in config (0-7 or 0-15)
2. Check power supply capacity
3. For stage use, max brightness recommended

### General Issues

**System lag**
1. Close unnecessary programs
2. Reduce update_interval in config
3. Use Raspberry Pi 4 for better performance
4. Disable desktop environment (use Lite OS)

**Auto-start not working**
See INSTALLATION.md for systemd service setup

## Next Steps

- [Installation Guide](INSTALLATION.md) - Software installation and configuration
- [User Guide](USER_GUIDE.md) - Operating instructions and tips
- [Wiring Reference](WIRING_REFERENCE.md) - Quick pin reference charts
