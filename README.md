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
- Optional: Breadboard and jumper wires for prototyping

### Audio Input
- USB audio interface with microphone/line input
- OR USB microphone
- OR Raspberry Pi audio HAT (e.g., HiFiBerry)

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
