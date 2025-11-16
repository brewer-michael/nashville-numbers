"""
LED seven-segment display driver for TM1637 and MAX7219 modules.
Perfect for stage use with large, bright red digits.
"""

import time


class LEDDisplay:
    """
    Driver for LED seven-segment displays.

    Supports:
    - TM1637 4-digit display (common, affordable)
    - MAX7219 8-digit display (brighter, more digits)

    Displays Nashville numbers in large, stage-visible format.
    """

    def __init__(self, display_type='TM1637', clk_pin=None, dio_pin=None,
                 cs_pin=None, brightness=7, use_simulation=False):
        """
        Initialize LED display.

        Args:
            display_type (str): 'TM1637' or 'MAX7219'
            clk_pin (int): GPIO pin for CLK (TM1637 and MAX7219)
            dio_pin (int): GPIO pin for DIO (TM1637 only)
            cs_pin (int): GPIO pin for CS (MAX7219 only)
            brightness (int): Brightness level (0-7 for TM1637, 0-15 for MAX7219)
            use_simulation (bool): Use simulated display for testing
        """
        self.display_type = display_type
        self.clk_pin = clk_pin
        self.dio_pin = dio_pin
        self.cs_pin = cs_pin
        self.brightness = brightness
        self.use_simulation = use_simulation

        self.display = None
        self.is_initialized = False

        # Determine number of digits based on display type
        self.num_digits = 4 if display_type == 'TM1637' else 8

        # Current display content (for simulation)
        self.current_text = ' ' * self.num_digits

    def initialize(self):
        """Initialize LED display hardware or simulation."""
        if self.use_simulation:
            print(f"[LED Simulation] Initializing {self.display_type} display")
            self.is_initialized = True
            self.clear()
            return True

        try:
            if self.display_type == 'TM1637':
                return self._initialize_tm1637()
            elif self.display_type == 'MAX7219':
                return self._initialize_max7219()
            else:
                print(f"Unknown display type: {self.display_type}")
                return False

        except ImportError as e:
            print(f"Warning: Required library not found ({e}). Using simulation mode.")
            self.use_simulation = True
            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Error initializing LED display: {e}")
            print("Falling back to simulation mode.")
            self.use_simulation = True
            self.is_initialized = True
            return False

    def _initialize_tm1637(self):
        """Initialize TM1637 4-digit display."""
        from tm1637 import TM1637

        if self.clk_pin is None or self.dio_pin is None:
            # Default pins for Raspberry Pi
            self.clk_pin = 23  # GPIO 23
            self.dio_pin = 24  # GPIO 24

        self.display = TM1637(clk=self.clk_pin, dio=self.dio_pin)
        self.display.brightness(self.brightness)
        self.is_initialized = True

        # Test pattern
        self.display.write([8, 8, 8, 8])  # All segments on
        time.sleep(0.5)
        self.clear()

        print(f"TM1637 initialized on GPIO CLK={self.clk_pin}, DIO={self.dio_pin}")
        return True

    def _initialize_max7219(self):
        """Initialize MAX7219 8-digit display."""
        from luma.led_matrix.device import max7219
        from luma.core.interface.serial import spi, noop

        if self.clk_pin is None:
            self.clk_pin = 11  # Default SPI CLK

        # Create SPI interface
        serial = spi(port=0, device=0, gpio=noop())
        self.display = max7219(serial)
        self.display.contrast(self.brightness * 16)  # Convert 0-7 to 0-112

        self.is_initialized = True
        self.clear()

        print("MAX7219 initialized on SPI")
        return True

    def clear(self):
        """Clear the display."""
        if not self.is_initialized:
            return

        if self.use_simulation:
            self.current_text = ' ' * self.num_digits
            self._print_simulation()
        else:
            if self.display_type == 'TM1637' and self.display is not None:
                self.display.write([0, 0, 0, 0])
            elif self.display_type == 'MAX7219' and self.display is not None:
                self.display.clear()

    def show_text(self, text, position=0):
        """
        Display text on LED display.

        Args:
            text (str): Text to display (numbers and some letters)
            position (int): Starting position (0-indexed)
        """
        if not self.is_initialized:
            return

        # Truncate to fit display
        text = text[:self.num_digits]

        if self.use_simulation:
            # Update simulation buffer
            self.current_text = text.ljust(self.num_digits)
            self._print_simulation()
        else:
            if self.display_type == 'TM1637':
                self._show_tm1637_text(text, position)
            elif self.display_type == 'MAX7219':
                self._show_max7219_text(text, position)

    def _show_tm1637_text(self, text, position):
        """Display text on TM1637."""
        if self.display is None:
            return

        # Convert text to segments
        segments = []
        for char in text:
            segments.append(self._char_to_segments(char))

        # Pad with blanks
        while len(segments) < 4:
            segments.append(0)

        self.display.write(segments[:4])

    def _show_max7219_text(self, text, position):
        """Display text on MAX7219."""
        if self.display is None:
            return

        from luma.core.render import canvas

        with canvas(self.display) as draw:
            draw.text((position * 8, 0), text, fill="white")

    def _char_to_segments(self, char):
        """
        Convert character to 7-segment encoding for TM1637.

        Args:
            char (str): Single character

        Returns:
            int: Segment encoding
        """
        # TM1637 segment encoding (common cathode)
        char_map = {
            '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66,
            '5': 0x6D, '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F,
            'A': 0x77, 'B': 0x7C, 'C': 0x39, 'D': 0x5E, 'E': 0x79,
            'F': 0x71, 'G': 0x3D, 'H': 0x76, 'I': 0x06, 'J': 0x1E,
            'L': 0x38, 'O': 0x3F, 'P': 0x73, 'S': 0x6D, 'U': 0x3E,
            '-': 0x40, '_': 0x08, ' ': 0x00, '°': 0x63, 'm': 0x54,
        }

        return char_map.get(char.upper(), 0x00)

    def display_nashville(self, nashville_number, show_colon=False):
        """
        Display Nashville number.

        Args:
            nashville_number (str): Nashville number (e.g., '1', '4', '2m', '7°')
            show_colon (bool): Show colon between digits (TM1637 only)
        """
        if not self.is_initialized:
            return

        if nashville_number is None:
            self.show_text("----")
            return

        # Center the number on display
        if len(nashville_number) <= self.num_digits:
            # Pad to center
            padding = (self.num_digits - len(nashville_number)) // 2
            display_text = ' ' * padding + nashville_number
        else:
            display_text = nashville_number

        self.show_text(display_text)

        # Show colon if requested (TM1637 only)
        if show_colon and self.display_type == 'TM1637' and not self.use_simulation:
            if self.display is not None:
                try:
                    self.display.show_colon(True)
                except AttributeError:
                    pass  # Not all TM1637 libraries support colon

    def set_brightness(self, brightness):
        """
        Set display brightness.

        Args:
            brightness (int): Brightness level (0-7 for TM1637, 0-15 for MAX7219)
        """
        if not self.is_initialized or self.use_simulation:
            return

        self.brightness = brightness

        if self.display_type == 'TM1637' and self.display is not None:
            self.display.brightness(brightness)
        elif self.display_type == 'MAX7219' and self.display is not None:
            self.display.contrast(brightness * 16)

    def flash(self, text, times=3, duration=0.3):
        """
        Flash text on display.

        Args:
            text (str): Text to flash
            times (int): Number of flashes
            duration (float): Flash duration in seconds
        """
        for _ in range(times):
            self.show_text(text)
            time.sleep(duration)
            self.clear()
            time.sleep(duration)

    def scroll_text(self, text, delay=0.3):
        """
        Scroll text across display.

        Args:
            text (str): Text to scroll
            delay (float): Delay between scroll steps
        """
        if len(text) <= self.num_digits:
            self.show_text(text)
            return

        # Add padding
        padded_text = ' ' * self.num_digits + text + ' ' * self.num_digits

        for i in range(len(padded_text) - self.num_digits + 1):
            self.show_text(padded_text[i:i + self.num_digits])
            time.sleep(delay)

    def _print_simulation(self):
        """Print simulated LED display to console."""
        digit_width = 9
        total_width = self.num_digits * digit_width

        print("\n" + "=" * total_width)
        print("|" + "|".join([f" {char:^6s} " for char in self.current_text]) + "|")
        print("=" * total_width + "\n")

    def close(self):
        """Close display and release resources."""
        if self.display is not None and not self.use_simulation:
            try:
                self.clear()
                if self.display_type == 'MAX7219':
                    self.display.cleanup()
            except Exception as e:
                print(f"Error closing LED display: {e}")

        self.is_initialized = False

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


class LEDTest:
    """Test utilities for LED display."""

    @staticmethod
    def test_display(display_type='TM1637'):
        """
        Test LED display with sample data.

        Args:
            display_type (str): 'TM1637' or 'MAX7219'
        """
        print(f"Testing {display_type} display...")

        with LEDDisplay(display_type=display_type, use_simulation=True) as led:
            # Test 1: Numbers
            for i in range(8):
                led.display_nashville(str(i))
                time.sleep(0.5)

            # Test 2: Nashville numbers
            test_numbers = ['1', '4', '5', '2m', '6m', '7°']

            for number in test_numbers:
                led.display_nashville(number)
                time.sleep(1)

            # Test 3: Scroll
            led.scroll_text("NASHVILLE NUMBERS")

            # Test 4: Flash
            led.flash('1', times=3)

        print("LED test complete")
