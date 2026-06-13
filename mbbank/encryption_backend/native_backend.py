import asyncio
import base64
import hashlib
import hmac
import json
import os
import struct
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .base import EncryptionBackend


class NativeBackend(EncryptionBackend):
    """
    Native encryption backend using AES-GCM and TOTP.
    """

    TOTP_KEY = b"77f567425cc9064fc899dc35ad1d912481565a8b9273fcc2216d245d403e6fab"
    TOTP_PERIOD = 30
    TOTP_DIGITS = 8

    def totp_code(self) -> bytes:
        # RFC 6238 / RFC 4226 TOTP
        timestamp = time.time()
        counter = int(timestamp // self.TOTP_PERIOD)
        msg = struct.pack(">Q", counter)
        digest = hmac.new(self.TOTP_KEY, msg, hashlib.sha256).digest()
        offset = digest[-1] & 0x0F
        code = (
            ((digest[offset] & 0x7F) << 24)
            | (digest[offset + 1] << 16)
            | (digest[offset + 2] << 8)
            | digest[offset + 3]
        )
        code_str = str(code % (10**self.TOTP_DIGITS))
        code_filled = code_str.zfill(self.TOTP_DIGITS)
        return code_filled.encode()

    def encrypt(self, data: dict) -> str:
        raw_content = json.dumps(data).encode("utf-8")
        random_prefix = os.urandom(12)
        random_suffix = os.urandom(12)
        nonce = os.urandom(12)
        totp = self.totp_code()
        key = random_prefix + totp + random_suffix

        prefix = random_prefix + random_suffix + nonce

        cipher = AESGCM(key)
        encrypted_content = cipher.encrypt(nonce, raw_content, None)
        sha1_tail = hashlib.sha1(raw_content).digest()

        raw = bytes(prefix) + encrypted_content + sha1_tail
        return base64.b64encode(raw).decode("ascii")

    async def encrypt_async(self, data: dict) -> str:
        return await asyncio.to_thread(self.encrypt, data)
