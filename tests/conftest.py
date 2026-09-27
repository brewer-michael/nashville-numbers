import numpy as np
import pytest


@pytest.fixture
def rng():
    return np.random.default_rng(1234)


@pytest.fixture(autouse=True)
def mock_gpio(monkeypatch):
    """Never touch real GPIO in tests: gpiozero uses its mock pin factory."""
    monkeypatch.setenv('GPIOZERO_PIN_FACTORY', 'mock')
    try:
        from gpiozero import Device
    except ImportError:  # gpiozero is optional
        yield
        return
    Device.pin_factory = None
    yield
    if Device.pin_factory is not None:
        Device.pin_factory.reset()
    Device.pin_factory = None
