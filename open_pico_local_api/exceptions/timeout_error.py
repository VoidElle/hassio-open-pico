from .pico_device_error import PicoDeviceError


class TimeoutError(PicoDeviceError):
    """Raised when operation times out"""
    pass