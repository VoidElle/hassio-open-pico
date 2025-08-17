# Function to retrieve the command to set ON / OFF to a device
def get_on_off_command(new_value: bool, device_pin: str):
    return {
        "on_off": 1 if new_value else 2,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": 2 if new_value else 1,
        "pin": device_pin
    }