import asyncio
import threading


class EncryptionBackend:
    """
    Base class for encryption backend for self-implemented

    Examples:
    ```py
    class MyEncryptionBackend(EncryptionBackend):
        def encrypt(self, data: dict) -> str:
            # encrypt data method for sync implementation
            return data

        async def encrypt_async(self, data: dict) -> str:
            # encrypt data method for async implementation
            return data

        def setup(self):
            # call on first encrypt call for sync implementation if needed
            pass

        async def setup_async(self):
            # call on first encrypt call for async implementation if needed
            pass
    ```
    """

    def __init__(self):
        self.is_setup_sync = False
        self.is_setup_async = False
        self._setup_lock = threading.Lock()
        self._async_setup_lock: asyncio.Lock | None = None

    @property
    def async_setup_lock(self) -> asyncio.Lock:
        """Lazy initialization of async lock to avoid event loop issues"""
        if self._async_setup_lock is None:
            self._async_setup_lock = asyncio.Lock()
        return self._async_setup_lock

    async def _encrypt_async(self, content: dict) -> str:
        if not self.is_setup_async:
            async with self.async_setup_lock:
                if not self.is_setup_async:
                    await self.setup_async()
                    self.is_setup_async = True
        return await self.encrypt_async(content)

    def _encrypt(self, content: dict) -> str:
        if not self.is_setup_sync:
            with self._setup_lock:
                if not self.is_setup_sync:
                    self.setup()
                    self.is_setup_sync = True
        return self.encrypt(content)

    def setup(self):
        """
        Setup if needed for sync implementation, this will be called before login and can be used to prepare any data needed for encryption.
        """

    async def setup_async(self):
        """
        Async setup if needed for async implementation, this will be called before login and can be used to prepare any data needed for encryption.
        """

    async def encrypt_async(self, data: dict) -> str:
        """
        Encrypt data method for async implementation, this will be called to encrypt data before sending to api.

        Args:
            data (dict): data to encrypt
        returns:
            success (str): encrypted data
        """
        raise NotImplementedError("encrypt_async is not implemented")

    def encrypt(self, data: dict) -> str:
        """
        Encrypt data method for sync implementation, this will be called to encrypt data before sending to api.

        Args:
            data (dict): data to encrypt
        returns:
            success (str): encrypted data
        """
        raise NotImplementedError("encrypt is not implemented")


__all__ = ["EncryptionBackend"]
