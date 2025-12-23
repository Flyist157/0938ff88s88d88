from __future__ import annotations

import datetime as dt
import hashlib
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mti.config import settings
from mti.crypto.ed25519 import b64e, sign
from mti.crypto.keys import ensure_keypair
from mti.models.db_models import AuditLog
from mti.util.ids import new_ulid


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def append_audit_event(
    session: AsyncSession,
    *,
    event_type: str,
    artifact_id: str | None = None,
    job_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> AuditLog:
    payload = payload or {}

    priv_raw, pub_raw = ensure_keypair(settings.signing_key_path, settings.signing_pubkey_path)
    pub_b64 = b64e(pub_raw)

    # Get previous entry hash for a simple global hash chain.
    prev_hash: str | None = None
    last = (await session.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1))).scalar_one_or_none()
    if last is not None:
        prev_hash = last.entry_hash

    entry = {
        "created_at": dt.datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "artifact_id": artifact_id,
        "job_id": job_id,
        "payload": payload,
        "prev_hash": prev_hash,
        "analysis_version": settings.analysis_version,
    }
    entry_hash = _sha256_hex(_canonical_json(entry))
    sig = sign(priv_raw, entry_hash.encode("ascii"))

    row = AuditLog(
        id=new_ulid("mt:audit"),
        event_type=event_type,
        artifact_id=artifact_id,
        job_id=job_id,
        payload=payload,
        prev_hash=prev_hash,
        entry_hash=entry_hash,
        signature_b64=b64e(sig),
        signer_pubkey_b64=pub_b64,
    )
    session.add(row)
    await session.commit()
    return row

