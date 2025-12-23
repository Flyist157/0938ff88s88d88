from __future__ import annotations

import datetime as dt
from typing import Any

from mti.analysis.types import ArtifactContext, SignalCandidate
from mti.config import settings
from mti.crypto.ed25519 import b64e, sign
from mti.crypto.keys import ensure_keypair
from mti.util.jsoncanon import canonical_json_bytes


def build_report_json(
    *,
    ctx: ArtifactContext,
    signals: list[SignalCandidate],
    trust: dict[str, Any],
    provenance: dict[str, Any],
    meta: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_id": ctx.artifact_id,
        "input_fingerprint": {
            "sha256": ctx.sha256,
            "size_bytes": ctx.size_bytes,
            "filename": ctx.filename,
            "content_type": ctx.content_type,
            "media_type": ctx.media_type,
        },
        "provenance": provenance,
        "trust": trust,
        "signals": [
            {
                "pillar": s.pillar,
                "signal_id": s.signal_id,
                "finding": s.finding,
                "value": float(s.value),
                "reliability": float(s.reliability),
                "evidence_refs": s.evidence_refs,
            }
            for s in signals
        ],
        "contradictions": trust.get("contradictions", []),
        "recommendations": trust.get("recommendations", []),
        "audit": {
            "analysis_version": settings.analysis_version,
            "generated_at": dt.datetime.now(dt.UTC).isoformat(),
            "pipeline": meta,
        },
    }


def sign_report(report_json: dict[str, Any]) -> tuple[str, str]:
    """
    Returns (report_signature_b64, signer_pubkey_b64).
    Signature covers canonical JSON of report_json.
    """
    priv_raw, pub_raw = ensure_keypair(settings.signing_key_path, settings.signing_pubkey_path)
    msg = canonical_json_bytes(report_json)
    sig = sign(priv_raw, msg)
    return b64e(sig), b64e(pub_raw)

