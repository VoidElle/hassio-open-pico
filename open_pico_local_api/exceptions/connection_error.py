from .pico_device_error import PicoDeviceError


class ConnectionError(PicoDeviceError):
    """Raised when connection fails"""
    pass