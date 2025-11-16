# Installation Guide

Complete software installation and configuration guide for the Nashville Numbers system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Raspberry Pi OS Setup](#raspberry-pi-os-setup)
3. [Software Installation](#software-installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Auto-Start Setup](#auto-start-setup)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware
- Raspberry Pi 3B+ or newer (Pi 4 recommended)
- 16GB+ microSD card
- USB audio interface or microphone
- LCD or LED display (see [Hardware Setup](HARDWARE_SETUP.md))
- Internet connection (for initial setup)

### Software
- Raspberry Pi OS (Buster or newer)
- Python 3.7 or newer
- Git

## Raspberry Pi OS Setup

### 1. Install Operating System

**Option A: Desktop Version**
```bash
# Download from https://www.raspberrypi.com/software/
# Use Raspberry Pi Imager to write to SD card
# Choose: "Raspberry Pi OS (32-bit)" with desktop
```

**Option B: Lite Version (Recommended for dedicated systems)**
```bash
# Choose: "Raspberry Pi OS Lite (32-bit)"
# Smaller footprint, better performance
# No desktop environment needed
```

### 2. Initial Configuration

```bash
# On first boot, run configuration
sudo raspi-config
```

Configure the following:
1. **System Options** → Hostname (e.g., "nashville-pi")
2. **Interface Options** → I2C → Enable (for LCD)
3. **Interface Options** → SPI → Enable (for MAX7219)
4. **Localisation Options** → Set timezone
5. **Performance Options** → GPU Memory → 16 MB (minimal)

Reboot:
```bash
sudo reboot
```

### 3. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

## Software Installation

### 1. Install System Dependencies

```bash
# Audio libraries
sudo apt install -y portaudio19-dev python3-pyaudio libasound2-dev

# I2C and GPIO tools
sudo apt install -y i2c-tools python3-smbus python3-rpi.gpio

# Python development tools
sudo apt install -y python3-pip python3-dev python3-numpy python3-scipy

# Git (if not already installed)
sudo apt install -y git

# Optional: For advanced audio analysis
# sudo apt install -y libsndfile1-dev
```

### 2. Clone Nashville Numbers Repository

```bash
# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/your-username/nashville-numbers.git
cd nashville-numbers
```

*Or if you have the code on a USB drive:*
```bash
cp -r /media/usb/nashville-numbers ~/
cd ~/nashville-numbers
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip3 install --upgrade pip

# Install requirements
pip3 install -r requirements.txt
```

**Note**: Installation may take 10-20 minutes, especially for NumPy and SciPy on Raspberry Pi 3.

### 4. Verify Installation

```bash
# Check Python version
python3 --version
# Should be 3.7 or newer

# Verify key libraries
python3 -c "import pyaudio; import numpy; import scipy; print('All imports successful')"
```

## Configuration

### 1. Create Configuration File

```bash
# Create from example
cp config.example.json config.json
```

### 2. Configure Audio Device

**Find your audio device:**
```bash
# List audio devices
python3 main.py --list-devices
```

Output example:
```
Available audio input devices:
------------------------------------------------------------
 0: bcm2835 Headphones (48000 Hz)
 1: USB Audio Device (44100 Hz)
 2: Blue Snowball (48000 Hz)
------------------------------------------------------------
```

**Edit config.json:**
```json
{
    "audio": {
        "sample_rate": 44100,
        "chunk_size": 4096,
        "channels": 1,
        "device_index": 1  // Use your USB device index
    }
}
```

### 3. Configure Display

**For LCD Display:**

Find I2C address:
```bash
sudo i2cdetect -y 1
```

Edit `config.json`:
```json
{
    "display": {
        "type": "lcd",
        "lcd": {
            "i2c_address": 39,  // 0x27 in decimal
            "rows": 2,
            "cols": 16
        }
    }
}
```

**For TM1637 LED Display:**

```json
{
    "display": {
        "type": "led",
        "led": {
            "display_type": "TM1637",
            "clk_pin": 23,
            "dio_pin": 24,
            "brightness": 7
        }
    }
}
```

**For MAX7219 LED Display:**

```json
{
    "display": {
        "type": "led",
        "led": {
            "display_type": "MAX7219",
            "brightness": 10
        }
    }
}
```

### 4. Adjust Detection Settings

Edit `config.json` for optimal detection:

```json
{
    "detection": {
        "min_chord_confidence": 0.3,     // Lower = more sensitive
        "min_key_confidence": 0.4,
        "key_detection_history": 8,       // More history = more stable
        "chord_smoothing": true,          // Reduce jitter
        "min_rms_threshold": 0.01        // Minimum volume
    }
}
```

## Testing

### 1. Test Audio Input

```bash
# Test audio levels (10 seconds)
python3 main.py --test-audio

# Should show visual meter:
# RMS Level | ##########
```

Play your instrument and verify the meter responds.

### 2. Test Display (Simulation Mode)

```bash
# Test without hardware
python3 main.py --simulate --display lcd

# Or for LED:
python3 main.py --simulate --display led
```

Verify the simulation output appears correctly.

### 3. Test Complete System

```bash
# Run with your configured display
python3 main.py

# Or with command-line override:
python3 main.py --display lcd
```

**Test procedure:**
1. Play a clear chord (e.g., C major)
2. Wait 2-3 seconds for key detection
3. Verify display shows correct chord and Nashville number
4. Try different chords in the same key
5. Press Ctrl+C to stop

### 4. Troubleshooting Tests

**Audio not detected:**
```bash
# Test system audio recording
arecord -D plughw:1,0 -d 5 -f cd test.wav
aplay test.wav

# Adjust input gain
alsamixer
# Press F6, select USB device, adjust capture level
```

**Display not working:**
```bash
# For LCD:
sudo i2cdetect -y 1  # Should show device at 0x27 or 0x3F

# For TM1637/MAX7219:
# Check wiring and run in simulation mode first
```

## Auto-Start Setup

### Option 1: Systemd Service (Recommended)

Create service file:
```bash
sudo nano /etc/systemd/system/nashville-numbers.service
```

Add content:
```ini
[Unit]
Description=Nashville Numbers Chord Detection
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nashville-numbers
ExecStart=/usr/bin/python3 /home/pi/nashville-numbers/main.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable nashville-numbers.service

# Start service
sudo systemctl start nashville-numbers.service

# Check status
sudo systemctl status nashville-numbers.service
```

View logs:
```bash
# Real-time logs
sudo journalctl -u nashville-numbers.service -f

# Recent logs
sudo journalctl -u nashville-numbers.service -n 50
```

Stop service:
```bash
sudo systemctl stop nashville-numbers.service
```

### Option 2: Cron at Reboot

Edit crontab:
```bash
crontab -e
```

Add line:
```
@reboot sleep 30 && cd /home/pi/nashville-numbers && /usr/bin/python3 main.py >> /home/pi/nashville.log 2>&1
```

### Option 3: Desktop Auto-Start

For Raspberry Pi OS with desktop:

```bash
# Create autostart directory
mkdir -p ~/.config/autostart

# Create desktop entry
nano ~/.config/autostart/nashville-numbers.desktop
```

Add content:
```ini
[Desktop Entry]
Type=Application
Name=Nashville Numbers
Exec=/usr/bin/python3 /home/pi/nashville-numbers/main.py
Terminal=true
```

## Advanced Configuration

### Performance Tuning

For better performance on Raspberry Pi 3:

```json
{
    "audio": {
        "chunk_size": 2048  // Smaller chunks = lower latency
    },
    "system": {
        "update_interval": 0.3  // Slower updates = lower CPU
    }
}
```

For Raspberry Pi 4:
```json
{
    "audio": {
        "chunk_size": 4096  // Better accuracy
    },
    "system": {
        "update_interval": 0.1  // Faster response
    }
}
```

### Disable Unnecessary Services

For dedicated Nashville Numbers system:
```bash
# Disable Bluetooth (if not needed)
sudo systemctl disable bluetooth

# Disable WiFi (if using Ethernet)
sudo systemctl disable wpa_supplicant

# Reduce GPU memory (already in raspi-config)
# Edit /boot/config.txt: gpu_mem=16
```

### Enable Real-Time Priority (Advanced)

For lowest possible latency:

```bash
# Edit limits
sudo nano /etc/security/limits.conf
```

Add:
```
@audio - rtprio 99
@audio - memlock unlimited
pi - rtprio 99
pi - memlock unlimited
```

Add user to audio group:
```bash
sudo usermod -a -G audio pi
```

Reboot:
```bash
sudo reboot
```

## Backup and Updates

### Backup Configuration

```bash
# Backup your config
cp config.json config.json.backup

# Or entire installation
cd ~
tar -czf nashville-backup.tar.gz nashville-numbers/
```

### Update Software

```bash
cd ~/nashville-numbers

# Pull latest changes
git pull

# Update dependencies
pip3 install -r requirements.txt --upgrade

# Restart service if running
sudo systemctl restart nashville-numbers.service
```

## Uninstallation

```bash
# Stop and disable service
sudo systemctl stop nashville-numbers.service
sudo systemctl disable nashville-numbers.service
sudo rm /etc/systemd/system/nashville-numbers.service

# Remove software
rm -rf ~/nashville-numbers

# Remove Python packages (optional)
pip3 uninstall -y -r requirements.txt
```

## Troubleshooting

### Common Issues

**"No module named 'nashville_numbers'"**
- Run from project root: `cd ~/nashville-numbers`
- Or set PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:~/nashville-numbers/src`

**"Permission denied" on GPIO**
- Add user to gpio group: `sudo usermod -a -G gpio pi`
- Reboot

**High CPU usage**
- Increase `update_interval` in config
- Reduce `chunk_size` for lower latency but higher CPU

**Inconsistent detection**
- Increase input gain
- Adjust `min_chord_confidence` (lower = more detections)
- Enable `chord_smoothing`

### Getting Help

1. Check logs: `sudo journalctl -u nashville-numbers.service`
2. Run in verbose mode: `python3 main.py --verbose`
3. Test in simulation: `python3 main.py --simulate`

## Next Steps

- [User Guide](USER_GUIDE.md) - Learn how to use the system
- [Hardware Setup](HARDWARE_SETUP.md) - Hardware details and troubleshooting
- [Wiring Reference](WIRING_REFERENCE.md) - Quick wiring diagrams
