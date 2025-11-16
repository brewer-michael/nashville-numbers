"""
LCD display driver for 16x2 or 20x4 character displays with I2C interface.
Compatible with PCF8574-based I2C LCD adapters.
"""

import time


class LCDDisplay:
    """
    Driver for I2C LCD displays (16x2 or 20x4).

    Displays chord information in Nashville number format:
    Line 1: Current chord and Nashville number
    Line 2: Current key and confidence

    Example display:
    ```
    Chord: 1     C
    Key: C Maj  90%
    ```
    """

    def __init__(self, i2c_address=0x27, rows=2, cols=16, use_simulation=False):
        """
        Initialize LCD display.

        Args:
            i2c_address (int): I2C address of LCD (typically 0x27 or 0x3F)
            rows (int): Number of rows (2 or 4)
            cols (int): Number of columns (16 or 20)
            use_simulation (bool): Use simulated display for testing without hardware
        """
        self.i2c_address = i2c_address
        self.rows = rows
        self.cols = cols
        self.use_simulation = use_simulation

        self.lcd = None
        self.is_initialized = False

        # Simulation mode buffer
        self.sim_buffer = [''] * rows

    def initialize(self):
        """Initialize LCD hardware or simulation."""
        if self.use_simulation:
            print(f"[LCD Simulation] Initializing {self.cols}x{self.rows} display at I2C 0x{self.i2c_address:02X}")
            self.is_initialized = True
            self.clear()
            return True

        try:
            # Import LCD library (only when actually using hardware)
            from RPLCD.i2c import CharLCD

            # Initialize LCD with I2C
            self.lcd = CharLCD(
                i2c_expander='PCF8574',
                address=self.i2c_address,
                cols=self.cols,
                rows=self.rows,
                dotsize=8,
                auto_linebreaks=True
            )

            self.is_initialized = True
            self.clear()
            self.write_line(0, "Nashville Numbers")
            self.write_line(1, "Initializing...")
            time.sleep(1)
            self.clear()

            print(f"LCD initialized at I2C address 0x{self.i2c_address:02X}")
            return True

        except ImportError:
            print("Warning: RPLCD library not found. Using simulation mode.")
            self.use_simulation = True
            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Error initializing LCD: {e}")
            print("Falling back to simulation mode.")
            self.use_simulation = True
            self.is_initialized = True
            return False

    def clear(self):
        """Clear the display."""
        if not self.is_initialized:
            return

        if self.use_simulation:
            self.sim_buffer = [' ' * self.cols] * self.rows
            self._print_simulation()
        else:
            if self.lcd is not None:
                self.lcd.clear()

    def write_line(self, row, text):
        """
        Write text to a specific row.

        Args:
            row (int): Row number (0-indexed)
            text (str): Text to display (will be truncated to fit)
        """
        if not self.is_initialized or row >= self.rows:
            return

        # Truncate and pad text to column width
        text = text[:self.cols].ljust(self.cols)

        if self.use_simulation:
            self.sim_buffer[row] = text
            self._print_simulation()
        else:
            if self.lcd is not None:
                self.lcd.cursor_pos = (row, 0)
                self.lcd.write_string(text)

    def display_chord(self, nashville_number, chord_name, key_name, key_quality, confidence):
        """
        Display chord information in Nashville format.

        Args:
            nashville_number (str): Nashville number (e.g., '1', '4', '2m')
            chord_name (str): Full chord name (e.g., 'C', 'Am', 'G7')
            key_name (str): Current key root (e.g., 'C', 'G')
            key_quality (str): 'major' or 'minor'
            confidence (float): Detection confidence (0-1)
        """
        if not self.is_initialized:
            return

        # Format line 1: Nashville number and chord name
        if nashville_number and chord_name:
            line1 = f"Chord: {nashville_number:4s} {chord_name}"
        else:
            line1 = "Listening..."

        # Format line 2: Key and confidence
        if key_name:
            key_display = f"{key_name} {'Maj' if key_quality == 'major' else 'Min'}"
            conf_percent = int(confidence * 100)
            line2 = f"Key: {key_display:7s} {conf_percent:2d}%"
        else:
            line2 = "Detecting key..."

        self.write_line(0, line1)
        self.write_line(1, line2)

    def display_message(self, line1, line2="", line3="", line4=""):
        """
        Display custom messages.

        Args:
            line1-4 (str): Text for each line
        """
        if not self.is_initialized:
            return

        lines = [line1, line2, line3, line4]
        for i in range(min(self.rows, len(lines))):
            self.write_line(i, lines[i])

    def _print_simulation(self):
        """Print simulated LCD display to console."""
        print("\n" + "=" * (self.cols + 4))
        for row in self.sim_buffer:
            print(f"| {row} |")
        print("=" * (self.cols + 4) + "\n")

    def set_backlight(self, enabled):
        """
        Enable or disable LCD backlight.

        Args:
            enabled (bool): True to enable, False to disable
        """
        if not self.is_initialized or self.use_simulation:
            return

        if self.lcd is not None:
            try:
                self.lcd.backlight_enabled = enabled
            except AttributeError:
                pass  # Not all LCD drivers support backlight control

    def close(self):
        """Close LCD and release resources."""
        if self.lcd is not None and not self.use_simulation:
            try:
                self.clear()
                self.lcd.close()
            except Exception as e:
                print(f"Error closing LCD: {e}")

        self.is_initialized = False

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


class LCDTest:
    """Test utilities for LCD display."""

    @staticmethod
    def test_display(i2c_address=0x27):
        """
        Test LCD display with sample data.

        Args:
            i2c_address (int): I2C address of LCD
        """
        print("Testing LCD display...")

        with LCDDisplay(i2c_address=i2c_address, use_simulation=True) as lcd:
            # Test 1: Welcome message
            lcd.display_message("Nashville Numbers", "Test Mode")
            time.sleep(2)

            # Test 2: Simulate chord detection
            test_chords = [
                ('1', 'C', 'C', 'major', 0.95),
                ('4', 'F', 'C', 'major', 0.92),
                ('5', 'G', 'C', 'major', 0.88),
                ('6m', 'Am', 'C', 'major', 0.91),
            ]

            for nash, chord, key, quality, conf in test_chords:
                lcd.display_chord(nash, chord, key, quality, conf)
                time.sleep(2)

            # Test 3: Different key
            lcd.display_chord('1', 'G', 'G', 'major', 0.94)
            time.sleep(2)

            lcd.display_message("Test Complete", "")

        print("LCD test complete")
