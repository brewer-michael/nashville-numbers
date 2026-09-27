# Installation

This guide covers installing Nashville Numbers on a Raspberry Pi and trying
it on any computer first. For parts and wiring see
[`hardware/`](../hardware/README.md).

## Try it without any hardware

Any Linux, macOS or Windows machine with Python 3.9+:

```bash
git clone https://github.com/brewer-michael/nashville-numbers.git
cd nashville-numbers
pip install .
nashville-numbers --simulate --demo                      # synthesised "1 5 6m 4" in G
nashville-numbers --simulate --demo "2m7 57 1maj7" --demo-key Bb
```

`--simulate` prints to the terminal instead of driving display hardware;
`--demo` synthesises a looping chord progression instead of listening. To
listen to your computer's microphone or audio interface instead, install the
audio extra and drop `--demo`:

```bash
pip install ".[audio]"           # sounddevice; Linux also needs libportaudio2
nashville-numbers --list-devices
nashville-numbers --simulate --device "USB"
```

To analyse a recording (16/24/32-bit WAV):

```bash
nashville-numbers --analyze song.wav
```

## Raspberry Pi

### 1. Operating system

Use **Raspberry Pi OS Lite (64-bit)**, Bookworm or Trixie. Lite has no
desktop audio server (PipeWire) competing for the audio interface, boots
faster and leaves more memory free. In Raspberry Pi Imager, set a hostname,
your user name and password, Wi-Fi if needed, and enable SSH.

Supported boards: Pi 5 and Pi 4 (1 GB is plenty), Pi 3B+. On a Pi 5
use the official 27 W power supply: with a 3 A supply the Pi 5 limits all USB
ports to 600 mA total, which a USB audio interface shares.

### 2. Install

Wire and plug in your display and audio interface first (see
[`hardware/wiring/`](../hardware/wiring/README.md)), then:

```bash
sudo apt install -y git
git clone https://github.com/brewer-michael/nashville-numbers.git
cd nashville-numbers
./deploy/install.sh --build desktop      # or: stage | budget | console
sudo reboot                              # once, so I2C/SPI and groups take effect
```

`install.sh`:

* installs the system packages (NumPy, gpiozero + lgpio, smbus2, spidev,
  PortAudio, i2c-tools);
* enables I2C and SPI and adds you to the `audio`, `gpio`, `i2c`, `spi` groups;
* creates a virtualenv in `.venv` and installs the package with its audio and
  Raspberry Pi extras;
* writes `~/.config/nashville-numbers/config.json` from
  `examples/config.<build>.json` (an existing file is never overwritten);
* installs and starts the `nashville-numbers` systemd service, and a sudo rule
  that only allows `systemctl poweroff`, so the panel button can shut the Pi
  down cleanly.

Use `--no-service` if you only want to run it by hand.

### 3. Check each part

```bash
cd ~/nashville-numbers
.venv/bin/nashville-numbers --list-devices     # is the audio interface there?
.venv/bin/nashville-numbers --test-audio       # level meter, detected chord, tuning
.venv/bin/nashville-numbers --test-display     # cycles example numbers on the display
sudo i2cdetect -y 1                            # LCD: 27 or 3f, HT16K33: 70
```

`--test-audio` shows the input level in dBFS. Set the interface's gain so
that strumming peaks around −20 to −10 dBFS and silence stays below the gate
(−50 dBFS by default). The meter shows `ON` while the gate is open.

Stop the service first if it is using the display or audio interface:
`sudo systemctl stop nashville-numbers`.

### 4. The service

```bash
sudo systemctl status nashville-numbers
journalctl -u nashville-numbers -f        # live log: key changes, errors
sudo systemctl restart nashville-numbers  # after editing the config
sudo systemctl disable --now nashville-numbers
```

The service waits for the audio interface if it isn't plugged in yet, and
reopens it if it is unplugged and plugged back in. If the display stops
responding it logs the error, keeps analysing, and retries every 5 seconds.

### 5. Configuration

`~/.config/nashville-numbers/config.json` only needs the settings you change;
everything else uses the defaults. `nashville-numbers --write-config
full.json` writes every setting with its current value. See the
[User Guide](USER_GUIDE.md#settings) for what each one does, and
`examples/` for ready-made configs. Version 1 config files still load (they
are converted automatically, with a warning).

### 6. Make it gig-proof (optional, recommended for stage use)

Pulling the power from a Raspberry Pi can corrupt its SD card. For a device
that gets unplugged at the end of every gig, make the SD card read-only once
everything works:

```bash
sudo raspi-config        # Performance Options -> Overlay File System -> enable, reboot
```

Changes to files are then lost at reboot. To change the config later,
disable the overlay again in `raspi-config`, edit, and re-enable it.
Alternatively, hold the panel button for 6 seconds before unplugging: the
display shows `OFF` and the Pi shuts down cleanly.

### Updating

```bash
cd ~/nashville-numbers
git pull
.venv/bin/pip install ".[audio,pi]"
sudo systemctl restart nashville-numbers
```

### Uninstalling

```bash
sudo systemctl disable --now nashville-numbers
sudo rm /etc/systemd/system/nashville-numbers.service /etc/sudoers.d/nashville-numbers
rm -rf ~/nashville-numbers ~/.config/nashville-numbers
```

## Troubleshooting

| Symptom | Check |
|---|---|
| `No audio input` on the display | `--list-devices`; set `audio.device` to part of the device's name; USB cable; on a Pi 5, the 27 W supply |
| Display blank, log says `No LCD at I2C address` | `sudo i2cdetect -y 1`; set `display.lcd.address` to what it shows; check the level shifter wiring |
| `TM1637 ... did not acknowledge` | CLK/DIO swapped or loose; module VCC must be on 3.3 V (pin 17) |
| LCD backlight on but no text | turn the blue contrast trimmer on the backpack |
| LCD shows wrong symbols for ° | set `display.lcd.charmap` to `A02` (some modules use the European ROM) |
| Chords flicker | raise `analysis.chord_hold_seconds` (e.g. 0.8); use a direct line/DI signal rather than a room mic |
| Key takes long to appear | normal for the first 4 chords; lower `key.min_events` to 3 for faster (less certain) keys |
| Nothing happens when playing | `--test-audio`: if the meter stays below the gate, raise the interface gain or lower `analysis.gate_open_dbfs` |
| `externally-managed-environment` from pip | use the virtualenv (`deploy/install.sh` does this); don't `sudo pip install` on Bookworm/Trixie |
