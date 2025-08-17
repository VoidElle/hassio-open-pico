import base64
import hashlib
import logging
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

from ..const import CYPHER_SALT, CYPHER_DEVICE_ID, STARTING_TOKEN

_LOGGER = logging.getLogger(__name__)

class GlobalTokenRepository:
    """Simple token repository"""
    token: Optional[str] = None


class TokenManager:
    """Python implementation of AESCrypt class for AES encryption/decryption"""

    def __init__(self, ref):
        self.ref = ref

        # The key string is the first 8 characters of the device ID + the cypher salt
        key_str = CYPHER_DEVICE_ID[:8] + CYPHER_SALT

        # Create SHA-256 hash and take only first 32 bytes, matching Java implementation
        key_bytes_full = hashlib.sha256(key_str.encode('utf-8')).digest()
        self.key = key_bytes_full[:32]  # Take first 32 bytes

        # IV with 16 zero bytes (matching Uint8List(16))
        self.iv = b'\x00' * 16

    def encrypt_text(self, plain_text: str) -> str:
        """Encrypts the given plain text using AES encryption"""
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(self.iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()

            # Apply PKCS7 padding
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plain_text.encode('utf-8'))
            padded_data += padder.finalize()

            # Encrypt
            encrypted = encryptor.update(padded_data) + encryptor.finalize()

            # Return base64 encoded
            return base64.b64encode(encrypted).decode('utf-8')

        except Exception as e:
            _LOGGER.error(f"Error encrypting text: {e}")
            raise

    def decrypt_text(self, base64_text: str) -> str:
        """Decrypts the given base64 text using AES decryption"""
        try:
            # Decode base64
            encrypted_data = base64.b64decode(base64_text)

            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(self.iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # Decrypt
            padded_plain_text = decryptor.update(encrypted_data) + decryptor.finalize()

            # Remove PKCS7 padding
            unpadder = padding.PKCS7(128).unpadder()
            plain_text = unpadder.update(padded_plain_text)
            plain_text += unpadder.finalize()

            return plain_text.decode('utf-8')

        except Exception as e:
            _LOGGER.error(f"Error decrypting text: {e}")
            raise

    def retrieve_new_token(self) -> Optional[str]:
        """
        This function retrieves a new token by incrementing the last part of the decrypted token
        WARNING: Every time an API call is done, a new token needs to be generated with this function
        """
        try:
            old_token = GlobalTokenRepository.token or ''

            try:
                decrypted_token = self.decrypt_text(old_token)
            except Exception as e:
                _LOGGER.error(f'Error decrypting token: {e}')
                return None

            split_token = decrypted_token.split("_")
            if len(split_token) == 2:
                try:
                    # Parse the integer and increment it
                    parsed_int = int(split_token[1]) + 1

                    new_token_plain = f"{split_token[0]}_{parsed_int}"
                    new_token = self.encrypt_text(new_token_plain)

                    # Remove carriage returns and newlines
                    new_token = new_token.replace("\r", "").replace("\n", "")

                    _LOGGER.debug(f'Old token: {old_token}')
                    _LOGGER.debug(f'Decrypted: {decrypted_token}')
                    _LOGGER.debug(f'New token plain: {new_token_plain}')
                    _LOGGER.debug(f'New token encrypted: {new_token}')

                    # Set the new token
                    GlobalTokenRepository.token = new_token

                    return new_token

                except Exception as e:
                    _LOGGER.error(f'Error parsing or encrypting: {e}')

        except Exception as e:
            _LOGGER.error(f'General error in retrieve_new_token: {e}')

        return None