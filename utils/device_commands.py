# Function to retrieve the command to set ON / OFF to a device
from ..repositories.global_idp_repository import GlobalIdpRepository


def get_on_off_command(new_value: bool, device_pin: str):
    return {
        "on_off": 1 if new_value else 2,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": GlobalIdpRepository.idpCounter,
        "pin": device_pin
    }

# Function to retrieve the command to change the mode to a device
def get_change_mode_command(new_mode: int, device_pin: str):
    return {
        "mod": new_mode,
        "on_off": 1,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": GlobalIdpRepository.idpCounter,
        "pin": device_pin
    }

# Function to retrieve the command to change the speed of the device
def get_change_speed_command(percentage: int, device_pin: str):
    return {
        "spd_row": percentage,
        "speed": 0,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": GlobalIdpRepository.idpCounter,
        "pin": device_pin
    }

# Function to retrieve the command to send the night mode to a device
def get_set_night_mode_command(enable: bool, device_pin: str):
    return {
        "night_mod": 1 if enable else 2,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": GlobalIdpRepository.idpCounter,
        "pin": device_pin
    }

# Function to retrieve the command to send the status of the LED to a device
def get_set_led_status_command(enable: bool, device_pin: str):
    return {
        "led_on_off_breve": 1 if enable else 2,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": GlobalIdpRepository.idpCounter,
        "pin": device_pin
    }