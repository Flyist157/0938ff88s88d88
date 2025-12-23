from __future__ import annotations

from pathlib import Path

from mti.crypto.ed25519 import generate_keypair


def ensure_keypair(private_key_path: Path, public_key_path: Path) -> tuple[bytes, bytes]:
    """
    Ensure an Ed25519 keypair exists on disk (raw 32-byte keys).
    Returns (private_raw, public_raw).
    """
    if private_key_path.exists() and public_key_path.exists():
        return private_key_path.read_bytes(), public_key_path.read_bytes()

    private_key_path.parent.mkdir(parents=True, exist_ok=True)
    public_key_path.parent.mkdir(parents=True, exist_ok=True)

    priv, pub = generate_keypair()
    private_key_path.write_bytes(priv)
    public_key_path.write_bytes(pub)
    return priv, pub

