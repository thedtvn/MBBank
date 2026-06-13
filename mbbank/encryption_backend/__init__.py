import contextlib

from .base import EncryptionBackend
from .native_backend import NativeBackend

# Try to import the optional WASM backend. If it's not available, don't expose it
# in __all__ so that `from mbbank.encryption_backend import *` doesn't list it.
WASM_BACKEND_AVAILABLE = False
with contextlib.suppress(ImportError):
    from .wasm_backend import WASMBackend

    WASM_BACKEND_AVAILABLE = True


# Prevent direct attribute access to WASMBackend when it's not installed.
def __getattr__(name: str):
    if name == "WASMBackend" and not WASM_BACKEND_AVAILABLE:
        raise ImportError("WASMBackend is not installed, please install it with `pip install mbbank-lib[wasm]`")
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "EncryptionBackend",
    "NativeBackend",
    "WASMBackend",
]  # use for auto-complete and type hinting

__all__ = (
    ["EncryptionBackend", "NativeBackend", "WASMBackend"]
    if WASM_BACKEND_AVAILABLE
    else ["EncryptionBackend", "NativeBackend"]
)  # use for import *
