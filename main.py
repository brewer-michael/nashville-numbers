#!/usr/bin/env python3
"""
Nashville Numbers - Real-Time Chord Detection System
Main application for running the chord detection and display system.
"""

import sys
import time
import argparse
import signal

# Add src to path
sys.path.insert(0, 'src')

from nashville_numbers.audio.audio_input import AudioInput, AudioMonitor
from nashville_numbers.audio.processor import AudioProcessor
from nashville_numbers.chord_detection.detector import ChordDetector
from nashville_numbers.chord_detection.key_detector import KeyDetector
from nashville_numbers.chord_detection.nashville import NashvilleConverter
from nashville_numbers.displays.lcd_display import LCDDisplay
from nashville_numbers.displays.led_display import LEDDisplay
from nashville_numbers.utils.config import Config


class NashvilleNumbersApp:
    """
    Main application class for Nashville Numbers system.

    Integrates audio input, chord detection, key detection,
    and display output.
    """

    def __init__(self, config_file=None):
        """
        Initialize application.

        Args:
            config_file (str): Path to configuration file (optional)
        """
        # Load configuration
        self.config = Config(config_file)

        # Initialize components
        self.audio_input = None
        self.audio_processor = None
        self.chord_detector = None
        self.key_detector = None
        self.nashville_converter = None
        self.display = None

        # State
        self.is_running = False
        self.current_chord = None
        self.current_nashville = None
        self.current_key = None

    def initialize(self):
        """Initialize all system components."""
        print("Initializing Nashville Numbers system...")

        # Audio configuration
        audio_config = self.config.get_audio_config()
        self.audio_input = AudioInput(
            sample_rate=audio_config['sample_rate'],
            chunk_size=audio_config['chunk_size'],
            channels=audio_config['channels'],
            device_index=audio_config['device_index']
        )

        self.audio_processor = AudioProcessor(
            sample_rate=audio_config['sample_rate']
        )

        # Detection configuration
        detection_config = self.config.get_detection_config()
        self.chord_detector = ChordDetector(
            min_confidence=detection_config['min_chord_confidence']
        )

        self.key_detector = KeyDetector(
            history_length=detection_config['key_detection_history']
        )

        self.nashville_converter = NashvilleConverter()

        # Display configuration
        display_config = self.config.get_display_config()
        system_config = self.config.get_system_config()

        if display_config['type'] == 'lcd':
            lcd_config = display_config['lcd']
            self.display = LCDDisplay(
                i2c_address=lcd_config['i2c_address'],
                rows=lcd_config['rows'],
                cols=lcd_config['cols'],
                use_simulation=system_config['simulation_mode']
            )
        else:  # LED
            led_config = display_config['led']
            self.display = LEDDisplay(
                display_type=led_config['display_type'],
                clk_pin=led_config['clk_pin'],
                dio_pin=led_config['dio_pin'],
                cs_pin=led_config['cs_pin'],
                brightness=led_config['brightness'],
                use_simulation=system_config['simulation_mode']
            )

        # Initialize display
        self.display.initialize()

        print("System initialized successfully!")
        return True

    def run(self):
        """Run the main detection loop."""
        if not self.audio_input or not self.display:
            print("Error: System not initialized. Call initialize() first.")
            return

        print("\nStarting Nashville Numbers detection...")
        print("Listening for chords... (Press Ctrl+C to stop)\n")

        # Start audio input
        self.audio_input.start()
        self.is_running = True

        # Get configuration
        detection_config = self.config.get_detection_config()
        system_config = self.config.get_system_config()
        update_interval = system_config['update_interval']
        min_rms = detection_config['min_rms_threshold']
        verbose = system_config['verbose']

        try:
            # Show initial message
            if hasattr(self.display, 'display_chord'):
                self.display.display_chord(None, None, None, 'major', 0.0)
            else:
                self.display.display_nashville(None)

            # Main loop
            while self.is_running:
                # Read audio
                audio_data = self.audio_input.read_buffer(num_chunks=2)

                if audio_data is None:
                    time.sleep(update_interval)
                    continue

                # Extract audio features
                features = self.audio_processor.get_audio_features(audio_data)

                # Check if there's actual audio signal
                if not features['has_signal'] or features['rms'] < min_rms:
                    time.sleep(update_interval)
                    continue

                # Detect chord
                chord_result = self.chord_detector.detect_chord(
                    features['chroma'],
                    use_smoothing=detection_config['chord_smoothing']
                )

                if verbose:
                    print(f"RMS: {features['rms']:.4f}, "
                          f"Chord: {chord_result['chord']}, "
                          f"Confidence: {chord_result['confidence']:.2f}")

                # Update key detector
                if chord_result['chord'] is not None:
                    self.key_detector.add_chord(
                        chord_result['chord'],
                        chord_result['root'],
                        chord_result['quality']
                    )

                # Detect key
                key_result = self.key_detector.detect_key_from_chords()

                # Update Nashville converter
                if key_result['key'] is not None:
                    self.nashville_converter.set_key(
                        key_result['key'],
                        key_result['quality']
                    )
                    self.current_key = key_result

                # Convert to Nashville number
                nashville_number = None
                if chord_result['chord'] is not None and key_result['key'] is not None:
                    nashville_number = self.nashville_converter.chord_to_nashville(
                        chord_result['root'],
                        chord_result['quality']
                    )

                # Update display
                if hasattr(self.display, 'display_chord'):
                    # LCD display
                    self.display.display_chord(
                        nashville_number,
                        chord_result['chord'],
                        key_result['key'],
                        key_result['quality'],
                        key_result['confidence']
                    )
                else:
                    # LED display
                    if nashville_number:
                        self.display.display_nashville(nashville_number)

                # Store current state
                self.current_chord = chord_result['chord']
                self.current_nashville = nashville_number

                # Wait before next update
                time.sleep(update_interval)

        except KeyboardInterrupt:
            print("\n\nStopping...")

        finally:
            self.stop()

    def stop(self):
        """Stop the system and cleanup."""
        self.is_running = False

        if self.audio_input:
            self.audio_input.stop()
            self.audio_input.close()

        if self.display:
            self.display.close()

        print("System stopped.")

    def test_audio(self, duration=10):
        """
        Test audio input and show levels.

        Args:
            duration (float): Test duration in seconds
        """
        print("Testing audio input...")

        if not self.audio_input:
            self.initialize()

        self.audio_input.start()

        monitor = AudioMonitor(self.audio_input)
        monitor.start_monitoring(duration=duration)

        self.audio_input.stop()
        print("Audio test complete")

    def list_audio_devices(self):
        """List available audio input devices."""
        if not self.audio_input:
            audio_config = self.config.get_audio_config()
            self.audio_input = AudioInput(
                sample_rate=audio_config['sample_rate']
            )

        devices = self.audio_input.list_devices()

        print("\nAvailable audio input devices:")
        print("-" * 60)
        for idx, name, rate in devices:
            print(f"{idx:2d}: {name} ({rate} Hz)")
        print("-" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Nashville Numbers - Real-Time Chord Detection System"
    )

    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='Configuration file (JSON)'
    )

    parser.add_argument(
        '--display', '-d',
        type=str,
        choices=['lcd', 'led'],
        default=None,
        help='Display type (overrides config)'
    )

    parser.add_argument(
        '--simulate', '-s',
        action='store_true',
        help='Use simulated displays (no hardware required)'
    )

    parser.add_argument(
        '--test-audio', '-t',
        action='store_true',
        help='Test audio input and show levels'
    )

    parser.add_argument(
        '--list-devices', '-l',
        action='store_true',
        help='List available audio input devices'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--create-config',
        type=str,
        default=None,
        help='Create default configuration file'
    )

    args = parser.parse_args()

    # Create default config if requested
    if args.create_config:
        Config.create_default_config(args.create_config)
        return 0

    # Create application
    app = NashvilleNumbersApp(config_file=args.config)

    # Override config with command-line args
    if args.display:
        app.config.set('display.type', args.display)

    if args.simulate:
        app.config.set('system.simulation_mode', True)

    if args.verbose:
        app.config.set('system.verbose', True)

    # Handle different modes
    if args.list_devices:
        app.list_audio_devices()
        return 0

    if args.test_audio:
        app.initialize()
        app.test_audio(duration=10)
        return 0

    # Normal operation
    try:
        app.initialize()

        # Setup signal handler for clean shutdown
        def signal_handler(sig, frame):
            print("\n\nReceived interrupt signal...")
            app.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run main loop
        app.run()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
