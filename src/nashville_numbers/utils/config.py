"""
Configuration management for Nashville Numbers system.
"""

import json
import os


class Config:
    """
    Configuration manager for Nashville Numbers system.

    Handles loading and saving configuration from JSON files.
    """

    DEFAULT_CONFIG = {
        # Audio settings
        'audio': {
            'sample_rate': 44100,
            'chunk_size': 4096,
            'channels': 1,
            'device_index': None,  # None = default device
        },

        # Detection settings
        'detection': {
            'min_chord_confidence': 0.3,
            'min_key_confidence': 0.4,
            'key_detection_history': 8,
            'chord_smoothing': True,
            'min_rms_threshold': 0.01,
        },

        # Display settings
        'display': {
            'type': 'lcd',  # 'lcd' or 'led'
            'lcd': {
                'i2c_address': 0x27,
                'rows': 2,
                'cols': 16,
            },
            'led': {
                'display_type': 'TM1637',  # 'TM1637' or 'MAX7219'
                'clk_pin': 23,
                'dio_pin': 24,
                'cs_pin': None,  # For MAX7219
                'brightness': 7,
            },
        },

        # System settings
        'system': {
            'update_interval': 0.2,  # Update display every 200ms
            'simulation_mode': False,  # Use simulated displays
            'verbose': False,
        }
    }

    def __init__(self, config_file=None):
        """
        Initialize configuration.

        Args:
            config_file (str): Path to JSON config file (optional)
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()

        if config_file and os.path.exists(config_file):
            self.load(config_file)

    def load(self, config_file):
        """
        Load configuration from JSON file.

        Args:
            config_file (str): Path to JSON config file
        """
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)

            # Merge with defaults (keep structure)
            self._merge_config(self.config, loaded_config)

            print(f"Configuration loaded from {config_file}")
            return True

        except Exception as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration")
            return False

    def save(self, config_file=None):
        """
        Save configuration to JSON file.

        Args:
            config_file (str): Path to save config (uses loaded file if None)
        """
        if config_file is None:
            config_file = self.config_file

        if config_file is None:
            print("No config file specified")
            return False

        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)

            print(f"Configuration saved to {config_file}")
            return True

        except Exception as e:
            print(f"Error saving config file: {e}")
            return False

    def _merge_config(self, base, override):
        """
        Recursively merge override config into base config.

        Args:
            base (dict): Base configuration
            override (dict): Override values
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, path, default=None):
        """
        Get configuration value by dot-separated path.

        Args:
            path (str): Dot-separated path (e.g., 'audio.sample_rate')
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, path, value):
        """
        Set configuration value by dot-separated path.

        Args:
            path (str): Dot-separated path (e.g., 'audio.sample_rate')
            value: Value to set
        """
        keys = path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def get_audio_config(self):
        """Get audio configuration."""
        return self.config['audio']

    def get_detection_config(self):
        """Get detection configuration."""
        return self.config['detection']

    def get_display_config(self):
        """Get display configuration."""
        return self.config['display']

    def get_system_config(self):
        """Get system configuration."""
        return self.config['system']

    @staticmethod
    def create_default_config(config_file='config.json'):
        """
        Create a default configuration file.

        Args:
            config_file (str): Path for config file
        """
        config = Config()
        config.save(config_file)
        print(f"Default configuration created: {config_file}")
