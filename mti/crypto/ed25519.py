from __future__ import annotations

import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat


def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def generate_keypair() -> tuple[bytes, bytes]:
    priv = Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_bytes = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return priv_bytes, pub_bytes


def sign(priv_raw: bytes, message: bytes) -> bytes:
    priv = Ed25519PrivateKey.from_private_bytes(priv_raw)
    return priv.sign(message)


def verify(pub_raw: bytes, message: bytes, signature: bytes) -> bool:
    pub = Ed25519PublicKey.from_public_bytes(pub_raw)
    try:
        pub.verify(signature, message)
        return True
    except Exception:  # noqa: BLE001
        return False

