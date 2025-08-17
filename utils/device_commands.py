# Function to retrieve the command to set ON / OFF to a device
def get_on_off_command(is_device_on: bool, device_pin: str):
    return {
        "on_off": 1 if is_device_on else 2,
        "cmd": "upd_pico",
        "frm": "mqtt",
        "idp": 2 if is_device_on else 1,
        "pin": device_pin
    }
    return f"{{\"on_off\":{1 if is_device_on else 2},\"cmd\":\"upd_pico\",\"frm\":\"mqtt\",\"idp\":{2 if is_device_on else 1},\"pin\":\"{device_pin}\"}}"