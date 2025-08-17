# Function to retrieve the command to set ON / OFF to a device
def get_on_off_command(new_value: bool, device_pin: str):
    return {
        "on_off": 1 if new_value else 2,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": 2 if new_value else 1,
        "pin": device_pin
    }

# Function to retrieve the command to change the mode to a device
def get_change_mode_command(new_mode: int, device_pin: str):
    return {
        "mod": new_mode,
        "on_off": 1,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": 1,
        "pin": device_pin
    }

# Function to retrieve the command to change the speed of the device
def get_change_speed_command(percentage: int, device_pin: str):
    return {
        "spd_row": percentage,
        "speed": 0,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": 1,
        "pin": device_pin
    }