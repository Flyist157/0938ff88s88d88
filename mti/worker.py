from __future__ import annotations

import asyncio
from pathlib import Path

from mti.analysis.pipeline import AnalysisPipeline
from mti.analysis.types import ArtifactContext
from mti.audit import append_audit_event
from mti.db import get_sessionmaker, init_db
from mti.models.db_models import SignalResult, TrustReport
from mti.repo import (
    claim_next_job,
    get_artifact,
    mark_job_failed,
    mark_job_succeeded,
    replace_signals,
    upsert_report,
)
from mti.reporting import build_report_json, sign_report
from mti.scoring import compute_trust
from mti.util.ids import new_ulid


def _guess_media_type(content_type: str, filename: str) -> str:
    ct = (content_type or "").lower()
    fn = (filename or "").lower()
    if ct.startswith("image/") or fn.endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff")
    ):
        return "image"
    if ct.startswith("video/") or fn.endswith((".mp4", ".mov", ".mkv", ".webm")):
        return "video"
    if ct.startswith("audio/") or fn.endswith((".wav", ".mp3", ".m4a", ".flac", ".ogg")):
        return "audio"
    return "unknown"


async def process_one(session) -> bool:
    job = await claim_next_job(session)
    if job is None:
        return False
    artifact = await get_artifact(session, job.artifact_id)
    if artifact is None:
        await mark_job_failed(session, job, "artifact_not_found")
        return True

    await append_audit_event(
        session,
        event_type="job.started",
        artifact_id=artifact.id,
        job_id=job.id,
        payload={"analysis_version": job.analysis_version},
    )

    try:
        media_type = artifact.media_type or _guess_media_type(
            artifact.content_type, artifact.filename
        )
        file_path = Path(artifact.object_path)
        manifest_path = (
            Path(artifact.manifest_object_path)
            if artifact.manifest_object_path
            else None
        )
        ctx = ArtifactContext(
            artifact_id=artifact.id,
            file_path=file_path,
            manifest_path=manifest_path,
            filename=artifact.filename,
            content_type=artifact.content_type,
            media_type=media_type,  # type: ignore[arg-type]
            sha256=artifact.sha256,
            size_bytes=artifact.size_bytes,
            derived={},
        )

        pipeline = AnalysisPipeline()
        candidates, meta = await pipeline.run(ctx)
        trust_res = compute_trust(candidates)

        trust_obj = {
            "score": trust_res.score,
            "confidence_band_90": (trust_res.confidence_low, trust_res.confidence_high),
            "max_trust_cap": trust_res.max_trust_cap,
            "status": trust_res.status,
            "contradictions": trust_res.contradictions,
            "recommendations": trust_res.recommendations,
        }
        report_json = build_report_json(
            ctx=ctx,
            signals=candidates,
            trust=trust_obj,
            provenance=trust_res.provenance_summary,
            meta=meta,
        )
        report_sig_b64, signer_pub_b64 = sign_report(report_json)

        # Persist signals
        db_signals: list[SignalResult] = []
        for s in candidates:
            db_signals.append(
                SignalResult(
                    id=new_ulid("mt:sig"),
                    artifact_id=artifact.id,
                    pillar=s.pillar,
                    signal_id=s.signal_id,
                    finding=s.finding,
                    value=float(s.value),
                    reliability=float(s.reliability),
                    evidence_refs=s.evidence_refs,
                    raw=s.raw,
                )
            )
        await replace_signals(session, artifact.id, db_signals)

        # Persist report
        await upsert_report(
            session,
            TrustReport(
                artifact_id=artifact.id,
                trust_score=trust_res.score,
                confidence_low=trust_res.confidence_low,
                confidence_high=trust_res.confidence_high,
                max_trust_cap=trust_res.max_trust_cap,
                status=trust_res.status,
                contradictions={"items": trust_res.contradictions},
                recommendations={"items": trust_res.recommendations},
                report_json=report_json,
                report_signature_b64=report_sig_b64,
                signer_pubkey_b64=signer_pub_b64,
            ),
        )

        await mark_job_succeeded(session, job)
        await append_audit_event(
            session,
            event_type="job.succeeded",
            artifact_id=artifact.id,
            job_id=job.id,
            payload={"trust_score": trust_res.score, "status": trust_res.status},
        )
        return True
    except Exception as e:  # noqa: BLE001
        await mark_job_failed(session, job, str(e))
        await append_audit_event(
            session,
            event_type="job.failed",
            artifact_id=artifact.id,
            job_id=job.id,
            payload={"error": str(e)},
        )
        return True


async def worker_loop(poll_interval_s: float = 0.5) -> None:
    await init_db()
    while True:
        async with get_sessionmaker()() as session:
            did = await process_one(session)
        if not did:
            await asyncio.sleep(poll_interval_s)


def main() -> None:
    asyncio.run(worker_loop())

