"""Constants for our integration."""

DOMAIN = "msp_integration_101_intermediate"

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 10

RENAME_DEVICE_SERVICE_NAME = "rename_device_service"
RESPONSE_SERVICE_NAME = "response_service"

SET_OFF_TIMER_ENTITY_SERVICE_NAME = "set_off_timer"
CONF_OFF_TIME = "off_time"

# Api key consts
API_KEY_FALLBACK_EMAIL = "UsrProAir"
API_KEY_PASSWORD = "PwdProAir"

# Token to start
STARTING_TOKEN = "Ga5mM61KCm5Bk18lhD5J999jC2Mu0Vaf"

# Push notification
PUSH_NOTIFICATION_PLATFORM = "fcm2"
PUSH_NOTIFICATION_TOKEN = "d5-l8Ok9SequOYXXGVy3X_:APA91bG67RFYtPjfDSlgpzEZqt8mxu78eGkSrnOL3XUn6T1tErpawd5yAfHGID1Z0HcrP7OO0dFtygndvPPy-1G5BdJKdnFB79IQGvczu-qxMcwuWq89Pp8"

# User agent utils
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 16; sdk_gphone64_arm64 Build/BP22.250325.006)"
USER_AGENT_OBJ = "benincapp"

# Result types
RESULT_ERROR = -1
RESULT_OK = 0
RESULT_INCORRECT_PWD_USER = 1
RESULT_USER_TO_ACTIVATE = 2
RESULT_USER_BLOCKED = 3
RESULT_USER_NOT_FOUND = 4
RESULT_DEVICE_NOT_VALID = 5
RESULT_EXPIRED_PWD = 6
RESULT_EXPIRED_TEMPORARY_PWD = 7
RESULT_MORE_DEVICES = 8
RESULT_MAIL_EXISTS = 9
RESULT_NEW_TERM_OF_USE = 10
RESULT_WIFI = 1234

# Cypher
CYPHER_SALT = "ns91wr48"
CYPHER_DEVICE_ID = "c610101212ff9aec"

# Base API constants
HOST = "proair.azurewebsites.net"
BASE_URL = f"https://{HOST}/"

# Specific endpoints
API_LOGIN_URL = f"https://{HOST}/apiTS/v2/Login"

# Specific headers
API_LOGIN_HEADERS = {
    'Accept-Encoding': 'gzip',
    'Connection': 'Keep-Alive',
    'Content-Length': '284',
    'Content-Type': 'application/json',
    'Host': HOST,
    'Token': STARTING_TOKEN,
    'User-Agent': USER_AGENT,
}