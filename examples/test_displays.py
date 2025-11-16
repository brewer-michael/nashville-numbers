#!/usr/bin/env python3
"""
Example: Test LCD and LED displays in simulation mode.
Useful for testing display logic without hardware.
"""

import sys
sys.path.insert(0, '../src')

import time
from nashville_numbers.displays.lcd_display import LCDDisplay
from nashville_numbers.displays.led_display import LEDDisplay


def test_lcd_display():
    """Test LCD display with various messages."""
    print("\n" + "=" * 60)
    print("Testing LCD Display (16x2)")
    print("=" * 60 + "\n")

    with LCDDisplay(use_simulation=True) as lcd:
        # Test 1: Welcome message
        print("Test 1: Welcome message")
        lcd.display_message("Nashville Numbers", "Version 1.0")
        time.sleep(2)

        # Test 2: Chord detection simulation
        print("\nTest 2: Chord progression in C major")
        test_chords = [
            ('1', 'C', 'C', 'major', 0.95),
            ('4', 'F', 'C', 'major', 0.92),
            ('5', 'G', 'C', 'major', 0.88),
            ('6m', 'Am', 'C', 'major', 0.91),
            ('4', 'F', 'C', 'major', 0.93),
            ('5', 'G', 'C', 'major', 0.90),
            ('1', 'C', 'C', 'major', 0.94),
        ]

        for nash, chord, key, quality, conf in test_chords:
            lcd.display_chord(nash, chord, key, quality, conf)
            print(f"  Showing: {chord} ({nash}) in key of {key} {quality}")
            time.sleep(1.5)

        # Test 3: Different key
        print("\nTest 3: Progression in G major")
        test_chords_g = [
            ('1', 'G', 'G', 'major', 0.96),
            ('4', 'C', 'G', 'major', 0.91),
            ('5', 'D', 'G', 'major', 0.89),
            ('6m', 'Em', 'G', 'major', 0.93),
        ]

        for nash, chord, key, quality, conf in test_chords_g:
            lcd.display_chord(nash, chord, key, quality, conf)
            print(f"  Showing: {chord} ({nash}) in key of {key} {quality}")
            time.sleep(1.5)

        # Test 4: Listening state
        print("\nTest 4: Listening state")
        lcd.display_chord(None, None, None, 'major', 0.0)
        time.sleep(2)

        print("\nLCD test complete!")


def test_led_display_tm1637():
    """Test TM1637 LED display."""
    print("\n" + "=" * 60)
    print("Testing TM1637 LED Display (4-digit)")
    print("=" * 60 + "\n")

    with LEDDisplay(display_type='TM1637', use_simulation=True) as led:
        # Test 1: Numbers
        print("Test 1: Numbers 0-7")
        for i in range(8):
            led.display_nashville(str(i))
            print(f"  Displaying: {i}")
            time.sleep(0.8)

        # Test 2: Nashville numbers with qualities
        print("\nTest 2: Nashville numbers with qualities")
        test_numbers = ['1', '2m', '3m', '4', '5', '6m', '7°']

        for number in test_numbers:
            led.display_nashville(number)
            print(f"  Displaying: {number}")
            time.sleep(1.2)

        # Test 3: Extended chords
        print("\nTest 3: Extended chords")
        extended = ['1', '7', 'M7', 'm7']

        for number in extended:
            led.display_nashville(number)
            print(f"  Displaying: {number}")
            time.sleep(1.2)

        # Test 4: Flash effect
        print("\nTest 4: Flash effect on chord change")
        led.flash('1', times=2, duration=0.3)
        time.sleep(0.5)
        led.flash('5', times=2, duration=0.3)

        # Test 5: Scroll text
        print("\nTest 5: Scroll text")
        led.scroll_text("NASHVILLE", delay=0.3)

        print("\nTM1637 test complete!")


def test_led_display_max7219():
    """Test MAX7219 LED display."""
    print("\n" + "=" * 60)
    print("Testing MAX7219 LED Display (8-digit)")
    print("=" * 60 + "\n")

    with LEDDisplay(display_type='MAX7219', use_simulation=True) as led:
        # Test 1: Nashville numbers
        print("Test 1: Nashville progression")
        progression = ['1', '4', '5', '6m', '2m', '5', '1']

        for number in progression:
            led.display_nashville(number)
            print(f"  Displaying: {number}")
            time.sleep(1.5)

        # Test 2: Brightness levels
        print("\nTest 2: Brightness test")
        for brightness in [3, 7, 10, 15]:
            led.set_brightness(brightness)
            led.display_nashville('1')
            print(f"  Brightness: {brightness}")
            time.sleep(1)

        # Test 3: Show chord and key together (8 digits)
        print("\nTest 3: Chord + Key display")
        led.show_text("1  C Maj")
        print("  Displaying: '1  C Maj'")
        time.sleep(2)

        led.show_text("5  G Maj")
        print("  Displaying: '5  G Maj'")
        time.sleep(2)

        print("\nMAX7219 test complete!")


def compare_displays():
    """Compare LCD vs LED displays."""
    print("\n" + "=" * 60)
    print("Comparing Display Types")
    print("=" * 60 + "\n")

    print("Initializing both displays...")
    lcd = LCDDisplay(use_simulation=True)
    led = LEDDisplay(display_type='TM1637', use_simulation=True)

    lcd.initialize()
    led.initialize()

    # Show same progression on both
    print("\nShowing same progression on both displays:")
    progression = [
        ('1', 'C', 'C', 'major', 0.95),
        ('4', 'F', 'C', 'major', 0.92),
        ('5', 'G', 'C', 'major', 0.88),
    ]

    for nash, chord, key, quality, conf in progression:
        print(f"\nChord: {chord} (Nashville: {nash})")

        print("\nLCD Display:")
        lcd.display_chord(nash, chord, key, quality, conf)

        print("\nLED Display:")
        led.display_nashville(nash)

        time.sleep(2)

    lcd.close()
    led.close()

    print("\n" + "=" * 60)
    print("Comparison complete!")
    print("\nSummary:")
    print("  LCD: Shows chord, Nashville number, key, and confidence")
    print("  LED: Shows only Nashville number in large digits")
    print("  LCD: Best for practice/learning")
    print("  LED: Best for stage visibility")
    print("=" * 60)


def main():
    """Run all display tests."""
    print("\n" + "=" * 70)
    print(" " * 15 + "Nashville Numbers - Display Tests")
    print("=" * 70)

    try:
        test_lcd_display()
        test_led_display_tm1637()
        test_led_display_max7219()
        compare_displays()

        print("\n" + "=" * 70)
        print("All display tests complete!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")


if __name__ == '__main__':
    main()
