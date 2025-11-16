"""
Nashville Numbers - Real-Time Chord Detection and Display System

A library for detecting musical chords in real-time and displaying them
using the Nashville Number System on various display types.
"""

__version__ = "1.0.0"
__author__ = "Nashville Numbers Project"

from .chord_detection.detector import ChordDetector
from .chord_detection.key_detector import KeyDetector
from .chord_detection.nashville import NashvilleConverter
from .displays.lcd_display import LCDDisplay
from .displays.led_display import LEDDisplay

__all__ = [
    'ChordDetector',
    'KeyDetector',
    'NashvilleConverter',
    'LCDDisplay',
    'LEDDisplay',
]
