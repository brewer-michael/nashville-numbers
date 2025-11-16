"""
Audio input handler for capturing real-time audio from microphone or line-in.
Uses PyAudio for cross-platform audio capture.
"""

import pyaudio
import numpy as np
from collections import deque
import threading
import time


class AudioInput:
    """
    Handles real-time audio input from USB microphone or audio interface.

    Attributes:
        sample_rate (int): Audio sample rate in Hz (default: 44100)
        chunk_size (int): Number of samples per buffer (default: 4096)
        channels (int): Number of audio channels (default: 1 - mono)
    """

    def __init__(self, sample_rate=44100, chunk_size=4096, channels=1, device_index=None):
        """
        Initialize audio input.

        Args:
            sample_rate (int): Sample rate in Hz
            chunk_size (int): Buffer size in samples
            channels (int): Number of audio channels (1=mono, 2=stereo)
            device_index (int): Specific audio device index (None for default)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.device_index = device_index

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False

        # Buffer to store recent audio data
        self.buffer = deque(maxlen=10)  # Keep last 10 chunks
        self.lock = threading.Lock()

        # For callback-based streaming
        self._callback_thread = None

    def list_devices(self):
        """
        List all available audio input devices.

        Returns:
            list: List of tuples (device_index, device_name, sample_rate)
        """
        devices = []
        for i in range(self.audio.get_device_count()):
            dev_info = self.audio.get_device_info_by_index(i)
            if dev_info['maxInputChannels'] > 0:
                devices.append((
                    i,
                    dev_info['name'],
                    int(dev_info['defaultSampleRate'])
                ))
        return devices

    def start(self):
        """Start audio input stream."""
        if self.is_running:
            return

        try:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )

            self.is_running = True
            self.stream.start_stream()
            print(f"Audio input started: {self.sample_rate}Hz, chunk size: {self.chunk_size}")

        except Exception as e:
            print(f"Error starting audio input: {e}")
            raise

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        Internal callback for audio stream.

        Args:
            in_data: Raw audio data from stream
            frame_count: Number of frames
            time_info: Timestamp information
            status: Stream status flags

        Returns:
            tuple: (None, pyaudio.paContinue)
        """
        if status:
            print(f"Audio stream status: {status}")

        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)

        # Store in buffer
        with self.lock:
            self.buffer.append(audio_data.copy())

        return (None, pyaudio.paContinue)

    def read_chunk(self):
        """
        Read the most recent audio chunk.

        Returns:
            numpy.ndarray: Audio data as float32 array, or None if no data
        """
        with self.lock:
            if len(self.buffer) > 0:
                return self.buffer[-1].copy()
            return None

    def read_buffer(self, num_chunks=1):
        """
        Read multiple recent chunks from buffer.

        Args:
            num_chunks (int): Number of chunks to read

        Returns:
            numpy.ndarray: Concatenated audio data, or None if insufficient data
        """
        with self.lock:
            if len(self.buffer) < num_chunks:
                return None

            # Get last num_chunks
            chunks = list(self.buffer)[-num_chunks:]
            return np.concatenate(chunks)

    def get_rms_level(self):
        """
        Get the RMS (Root Mean Square) level of recent audio.
        Useful for detecting if audio is actually present.

        Returns:
            float: RMS level (0.0 to 1.0), or 0.0 if no data
        """
        chunk = self.read_chunk()
        if chunk is None or len(chunk) == 0:
            return 0.0

        return np.sqrt(np.mean(chunk ** 2))

    def stop(self):
        """Stop audio input stream."""
        if not self.is_running:
            return

        self.is_running = False

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        print("Audio input stopped")

    def close(self):
        """Close audio input and release resources."""
        self.stop()

        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


class AudioMonitor:
    """Simple audio level monitor for testing and calibration."""

    def __init__(self, audio_input):
        """
        Initialize monitor with an AudioInput instance.

        Args:
            audio_input (AudioInput): Audio input instance to monitor
        """
        self.audio_input = audio_input
        self.is_monitoring = False
        self._monitor_thread = None

    def start_monitoring(self, duration=10, update_interval=0.1):
        """
        Start monitoring audio levels.

        Args:
            duration (float): Monitoring duration in seconds (0 for infinite)
            update_interval (float): Update interval in seconds
        """
        self.is_monitoring = True
        start_time = time.time()

        print("Monitoring audio levels (Ctrl+C to stop)...")
        print("RMS Level | " + "=" * 50)

        try:
            while self.is_monitoring:
                if duration > 0 and (time.time() - start_time) > duration:
                    break

                rms = self.audio_input.get_rms_level()
                bar_length = int(rms * 50)
                bar = "#" * bar_length + " " * (50 - bar_length)

                print(f"\r{rms:6.4f}    | {bar}", end="", flush=True)

                time.sleep(update_interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")

        self.is_monitoring = False
        print("\nMonitoring complete")

    def stop_monitoring(self):
        """Stop monitoring."""
        self.is_monitoring = False
