from __future__ import annotations

"""Utilities for computing SSH public key fingerprints.

Centralizes MD5 (legacy colon-delimited) and SHA256 (OpenSSH) fingerprints so
CLI, wizards, and provider code use consistent implementations.
"""

import base64
import hashlib


def md5_fingerprint_from_public_key(public_key: str) -> str | None:
    """Return MD5 fingerprint (colon-delimited) of an SSH public key string.

    Args:
        public_key: SSH public key content in authorized_keys format

    Returns:
        Fingerprint like "aa:bb:..." or None if parsing fails.
    """
    try:
        parts = (public_key or "").strip().split()
        if len(parts) >= 2:
            b64 = parts[1]
            # Tolerate missing padding commonly seen in SSH public keys
            pad_len = (-len(b64)) % 4
            if pad_len:
                b64 = b64 + ("=" * pad_len)
            decoded = base64.b64decode(b64.encode())
            md5_hex = hashlib.md5(decoded).hexdigest()  # nosec - fingerprint only
            return ":".join(md5_hex[i : i + 2] for i in range(0, len(md5_hex), 2))
    except Exception:
        return None
    return None


def sha256_fingerprint_from_public_key(public_key: str) -> str | None:
    """Return OpenSSH SHA256 fingerprint (base64) for a public key string.

    Args:
        public_key: SSH public key content in authorized_keys format

    Returns:
        Fingerprint like "SHA256:abc..." or None if parsing fails.
    """
    try:
        parts = (public_key or "").strip().split()
        if len(parts) >= 2:
            b64 = parts[1]
            pad_len = (-len(b64)) % 4
            if pad_len:
                b64 = b64 + ("=" * pad_len)
            decoded = base64.b64decode(b64.encode())
            sha256 = hashlib.sha256(decoded).digest()
            b64 = base64.b64encode(sha256).decode("utf-8").rstrip("=")
            return f"SHA256:{b64}"
    except Exception:
        return None
    return None
