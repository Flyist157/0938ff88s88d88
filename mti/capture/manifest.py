from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

from mti.crypto.ed25519 import b64e, sign, verify
from mti.util.hashing import sha256_file
from mti.util.jsoncanon import canonical_json_bytes


@dataclass(frozen=True)
class CaptureManifest:
    schema: str
    payload: dict[str, Any]
    signature_b64: str
    public_key_b64: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "payload": self.payload,
            "signature_b64": self.signature_b64,
            "public_key_b64": self.public_key_b64,
        }


def sign_file(
    *,
    file_path,
    private_key_raw: bytes,
    public_key_raw: bytes,
    device_id: str,
    app_id: str,
    capture_mode: str = "offline",
    extra_claims: dict[str, Any] | None = None,
) -> CaptureManifest:
    sha = sha256_file(file_path)
    payload: dict[str, Any] = {
        "artifact_sha256": sha,
        "captured_at": dt.datetime.now(dt.UTC).isoformat(),
        "device_id": device_id,
        "app_id": app_id,
        "capture_mode": capture_mode,
        "chain": [
            {
                "type": "capture",
                "time": dt.datetime.now(dt.UTC).isoformat(),
                "device_id": device_id,
                "app_id": app_id,
                "mode": capture_mode,
            }
        ],
    }
    if extra_claims:
        payload["claims"] = extra_claims

    schema = "mti.capture.v1"
    msg = canonical_json_bytes({"schema": schema, "payload": payload})
    sig = sign(private_key_raw, msg)
    return CaptureManifest(
        schema=schema,
        payload=payload,
        signature_b64=b64e(sig),
        public_key_b64=b64e(public_key_raw),
    )


def verify_manifest(manifest: dict[str, Any], public_key_raw: bytes | None = None) -> bool:
    try:
        schema = manifest["schema"]
        payload = manifest["payload"]
        sig_b64 = manifest["signature_b64"]
        pub_b64 = manifest.get("public_key_b64")
    except Exception:  # noqa: BLE001
        return False

    from mti.crypto.ed25519 import b64d  # local import to avoid cycles

    pub = public_key_raw if public_key_raw is not None else b64d(pub_b64)
    msg = canonical_json_bytes({"schema": schema, "payload": payload})
    return verify(pub, msg, b64d(sig_b64))

