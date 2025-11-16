# Nashville Numbers - Real-Time Chord Detection System

A Raspberry Pi-based system that listens to live music, detects chords in real-time, determines the musical key, and displays the corresponding Nashville number values on LCD or LED displays.

Perfect for musicians working on improvisation skills!

## Features

- **Real-time chord detection** using advanced audio analysis
- **Automatic key detection** to provide context for Nashville numbers
- **Dual display support**: 16x2 LCD or seven-segment LED displays
- **Low latency** for live performance use
- **Configurable sensitivity** and detection parameters
- **Stage-friendly LED option** with large red digits visible on dark stages

## What are Nashville Numbers?

The Nashville Number System is a method of transcribing music by denoting the scale degree on which a chord is built. It's widely used by professional musicians for quick transposition and communication.

- **1** = Root chord (I)
- **2m** = Second degree minor (ii)
- **3m** = Third degree minor (iii)
- **4** = Fourth degree major (IV)
- **5** = Fifth degree major (V)
- **6m** = Sixth degree minor (vi)
- **7°** = Seventh degree diminished (vii°)

## Hardware Requirements

### Raspberry Pi Version
- Raspberry Pi 3B+ or newer (Pi 4 recommended for better performance)
- USB audio interface or USB microphone
- One of the following displays:
  - 16x2 I2C LCD display
  - TM1637 4-digit seven-segment LED display (red recommended)
  - MAX7219 LED matrix display
- Power supply (5V, 2.5A minimum)
- Optional: 3D printed enclosure (see [3D Printed Enclosures](#3d-printed-enclosures))

### Audio Input
- USB audio interface with microphone/line input
- OR USB microphone
- OR Raspberry Pi audio HAT (e.g., HiFiBerry)

## 3D Printed Enclosures

Professional enclosures available for 3D printing! Choose the one that fits your use case:

### Desktop/Practice Room - LCD Case
<img src="https://via.placeholder.com/300x200?text=LCD+Case" alt="LCD Case" width="300">

- Houses Raspberry Pi + LCD display
- Professional appearance
- Full port access
- [Design Files & Instructions](hardware/enclosures/)

### Stage Performance - LED Display Case
<img src="https://via.placeholder.com/300x200?text=Stage+LED" alt="Stage LED" width="300">

- Floor-mountable with 30° viewing angle
- Rugged PETG construction
- High-visibility LED window
- [Design Files & Instructions](hardware/enclosures/)

### Compact/Pedalboard - All-in-One Case
<img src="https://via.placeholder.com/300x200?text=Compact+Case" alt="Compact Case" width="300">

- Vertical design saves space
- Pi + LED in one unit
- VESA & pedalboard compatible
- [Design Files & Instructions](hardware/enclosures/)

**[→ See all enclosure options and printing guide](hardware/enclosures/)**

All designs are parametric OpenSCAD files that can be customized for your specific needs.

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd nashville-numbers

# Install dependencies
pip install -r requirements.txt

# Run with LCD display
python main.py --display lcd

# Run with LED display
python main.py --display led
```

## Documentation

- [Hardware Setup Guide](docs/HARDWARE_SETUP.md) - Detailed wiring and component information
- [Installation Guide](docs/INSTALLATION.md) - Software setup and configuration
- [User Guide](docs/USER_GUIDE.md) - Operating instructions and tips
- [API Reference](docs/API.md) - For developers extending the system

## Project Structure

```
nashville-numbers/
├── src/nashville_numbers/
│   ├── audio/           # Audio input and processing
│   ├── chord_detection/ # Chord and key detection algorithms
│   ├── displays/        # Display drivers (LCD, LED)
│   └── utils/          # Utility functions
├── hardware/
│   └── enclosures/     # 3D printable enclosures (OpenSCAD)
├── docs/               # Documentation
├── examples/           # Example scripts
└── main.py            # Main application
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

Built for musicians who love to improvise and want real-time harmonic feedback during practice and performance.
