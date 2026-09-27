#!/usr/bin/env bash
# Nashville Numbers installer for Raspberry Pi OS (Bookworm or Trixie, Lite or
# Desktop) on a Raspberry Pi 5, 4 or 3B+.
#
#   ./deploy/install.sh --build desktop|stage|budget|console [--no-service]
#
# Installs system packages, enables I2C/SPI, creates a virtualenv in .venv,
# writes ~/.config/nashville-numbers/config.json (kept if it already exists)
# and installs + starts the systemd service.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="console"
SERVICE=1
while [[ $# -gt 0 ]]; do
    case "$1" in
        --build) BUILD="${2:?--build needs a value}"; shift 2 ;;
        --no-service) SERVICE=0; shift ;;
        -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done
case "$BUILD" in
    desktop|stage|budget|console) ;;
    *) echo "--build must be desktop, stage, budget or console" >&2; exit 2 ;;
esac

if [[ $EUID -eq 0 ]]; then
    echo "Run this as your normal user (it uses sudo where needed)." >&2
    exit 1
fi
USER_NAME="$(id -un)"
CONFIG_DIR="$HOME/.config/nashville-numbers"
CONFIG="$CONFIG_DIR/config.json"

if ! grep -qi raspberry /proc/device-tree/model 2>/dev/null; then
    echo "Warning: this does not look like a Raspberry Pi; continuing anyway."
fi

echo "==> Installing system packages"
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip python3-numpy python3-cffi \
    python3-gpiozero python3-lgpio python3-smbus2 python3-spidev \
    libportaudio2 i2c-tools alsa-utils

if command -v raspi-config >/dev/null; then
    echo "==> Enabling I2C and SPI"
    sudo raspi-config nonint do_i2c 0
    sudo raspi-config nonint do_spi 0
fi

echo "==> Adding $USER_NAME to the audio, gpio, i2c and spi groups"
for group in audio gpio i2c spi; do
    if getent group "$group" >/dev/null; then
        sudo usermod -aG "$group" "$USER_NAME"
    fi
done

echo "==> Creating the virtualenv in $REPO/.venv"
python3 -m venv --system-site-packages "$REPO/.venv"
"$REPO/.venv/bin/pip" install --upgrade pip
"$REPO/.venv/bin/pip" install "${REPO}[audio,pi]"

mkdir -p "$CONFIG_DIR"
if [[ -f "$CONFIG" ]]; then
    echo "==> Keeping existing $CONFIG"
elif [[ "$BUILD" == "console" ]]; then
    "$REPO/.venv/bin/nashville-numbers" --write-config "$CONFIG"
else
    cp "$REPO/examples/config.$BUILD.json" "$CONFIG"
    echo "==> Wrote $CONFIG for the $BUILD build"
fi

if [[ $SERVICE -eq 1 ]]; then
    echo "==> Installing the systemd service"
    sed -e "s|@USER@|$USER_NAME|g" -e "s|@REPO@|$REPO|g" -e "s|@CONFIG@|$CONFIG|g" \
        "$REPO/deploy/nashville-numbers.service" \
        | sudo tee /etc/systemd/system/nashville-numbers.service >/dev/null
    # Let the panel button's 6-second hold shut the Pi down cleanly.
    echo "$USER_NAME ALL=(root) NOPASSWD: /usr/bin/systemctl poweroff" \
        | sudo tee /etc/sudoers.d/nashville-numbers >/dev/null
    sudo chmod 440 /etc/sudoers.d/nashville-numbers
    sudo visudo -cf /etc/sudoers.d/nashville-numbers >/dev/null
    sudo systemctl daemon-reload
    sudo systemctl enable nashville-numbers.service
    sudo systemctl restart nashville-numbers.service
fi

cat <<MSG

Done.
  Config:   $CONFIG
  Try it:   $REPO/.venv/bin/nashville-numbers --list-devices
            $REPO/.venv/bin/nashville-numbers --test-audio
            $REPO/.venv/bin/nashville-numbers --test-display
  Service:  sudo systemctl status nashville-numbers
  Logs:     journalctl -u nashville-numbers -f

If I2C/SPI or group membership was just enabled, reboot once: sudo reboot
MSG
