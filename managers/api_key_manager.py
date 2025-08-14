import base64

from msp_integration_101_intermediate.const import API_KEY_FALLBACK_EMAIL, API_KEY_PASSWORD

# Function to retrieve the Api key that will be sent in the headers
def retrieve_api_key(email: str | None = None) -> str:
    username = email or API_KEY_FALLBACK_EMAIL
    credentials = f"{username}:{API_KEY_PASSWORD}"
    return f"Basic {base64.b64encode(credentials.encode('utf-8')).decode('utf-8')}"