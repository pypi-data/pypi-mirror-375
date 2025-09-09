"""
Secrecy
=======

A simple CLI utility for file en-/decryption.

"""

from .main import (
    DATA_DIR,
    ENCRYPTION_DIR,
    DECRYPTION_DIR,
    generate_key,
    cli,
    encrypt,
    decrypt
)


# ─── package metadata ───────────────────────────────────────────────────────────── ✦ ─
#
#
__author__ = "Caleb Rice"
__email__ = "hyletic@proton.me"
__version__ = "0.1.0-dev0"


# ─── package-level exports ──────────────────────────────────────────────────────── ✦ ─
#
__all__ = [
    "DATA_DIR",
    "ENCRYPTION_DIR",
    "DECRYPTION_DIR",
    "generate_key",
    "cli",
    "encrypt",
    "decrypt",
]
