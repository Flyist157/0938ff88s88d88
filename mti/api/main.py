from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mti.audit import append_audit_event
from mti.config import settings
from mti.db import get_session, init_db
from mti.models import db_models
from mti.models.schemas import (
    ArtifactCreateResponse,
    ArtifactOut,
    JobOut,
    PolicyEvaluateRequest,
    PolicyEvaluateResponse,
    PolicyOut,
    TrustReportOut,
)
from mti.policy import evaluate_policy
from mti.repo import create_artifact, create_job, get_artifact, get_job, list_policies_stub
from mti.storage import artifact_dir, save_upload
from mti.util.hashing import sha256_file
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


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Media Trust Infrastructure", version="0.1.0", lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/artifacts", response_model=ArtifactCreateResponse)
async def create_artifact_endpoint(
    file: UploadFile = File(...),
    manifest: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_session),
) -> ArtifactCreateResponse:
    artifact_id = new_ulid("mt:art")
    d = artifact_dir(artifact_id).resolve()

    filename = file.filename or "upload"
    content_type = file.content_type or "application/octet-stream"
    media_type = _guess_media_type(content_type, filename)

    media_path = (d / "media").resolve()
    size_bytes = await save_upload(file, media_path)
    sha = sha256_file(media_path)

    manifest_path_str: str | None = None
    if manifest is not None:
        mp = (d / "manifest.mti.json").resolve()
        await save_upload(manifest, mp)
        manifest_path_str = str(mp)

    artifact = await create_artifact(
        session,
        artifact_id=artifact_id,
        filename=filename,
        media_type=media_type,
        content_type=content_type,
        sha256=sha,
        size_bytes=size_bytes,
        object_path=str(media_path),
        manifest_object_path=manifest_path_str,
    )
    job = await create_job(
        session,
        artifact_id=artifact.id,
        analysis_version=settings.analysis_version,
    )

    await append_audit_event(
        session,
        event_type="artifact.created",
        artifact_id=artifact.id,
        job_id=job.id,
        payload={"filename": filename, "content_type": content_type, "size_bytes": size_bytes},
    )
    await append_audit_event(
        session,
        event_type="job.queued",
        artifact_id=artifact.id,
        job_id=job.id,
        payload={"analysis_version": job.analysis_version},
    )

    return ArtifactCreateResponse(artifact_id=artifact.id, job_id=job.id)


@app.get("/v1/artifacts/{artifact_id}", response_model=ArtifactOut)
async def get_artifact_endpoint(
    artifact_id: str, session: AsyncSession = Depends(get_session)
) -> ArtifactOut:
    artifact = await get_artifact(session, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="artifact_not_found")
    return ArtifactOut(
        id=artifact.id,
        filename=artifact.filename,
        media_type=artifact.media_type,  # type: ignore[arg-type]
        content_type=artifact.content_type,
        sha256=artifact.sha256,
        size_bytes=artifact.size_bytes,
        created_at=artifact.created_at,
    )


@app.get("/v1/jobs/{job_id}", response_model=JobOut)
async def get_job_endpoint(job_id: str, session: AsyncSession = Depends(get_session)) -> JobOut:
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job_not_found")
    return JobOut(
        id=job.id,
        artifact_id=job.artifact_id,
        status=job.status,  # type: ignore[arg-type]
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        analysis_version=job.analysis_version,
        error=job.error,
    )


@app.get("/v1/artifacts/{artifact_id}/report", response_model=TrustReportOut)
async def get_report_endpoint(
    artifact_id: str, session: AsyncSession = Depends(get_session)
) -> TrustReportOut:
    artifact = await get_artifact(session, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="artifact_not_found")

    report = (
        await session.execute(
            select(db_models.TrustReport).where(
                db_models.TrustReport.artifact_id == artifact_id
            )
        )
    ).scalar_one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="report_not_ready")

    # Include persisted signals for client convenience.
    sig_rows = (
        await session.execute(
            select(db_models.SignalResult).where(db_models.SignalResult.artifact_id == artifact_id)
        )
    ).scalars().all()
    signals_out = [
        {
            "pillar": s.pillar,
            "signal_id": s.signal_id,
            "finding": s.finding,
            "value": float(s.value),
            "reliability": float(s.reliability),
            "evidence_refs": s.evidence_refs,
        }
        for s in sig_rows
    ]

    report_json: dict[str, Any] = dict(report.report_json)
    report_json["signals"] = signals_out
    # Ensure trust fields reflect stored values
    report_json["trust"] = {
        "score": report.trust_score,
        "confidence_band_90": (report.confidence_low, report.confidence_high),
        "max_trust_cap": report.max_trust_cap,
        "status": report.status,
    }
    report_json["provenance"] = report_json.get("provenance", {})
    report_json["contradictions"] = report.contradictions.get("items", [])
    report_json["recommendations"] = report.recommendations.get("items", [])
    report_json["report_signature_b64"] = report.report_signature_b64
    report_json["signer_pubkey_b64"] = report.signer_pubkey_b64

    return TrustReportOut(**report_json)


@app.get("/v1/policies", response_model=list[PolicyOut])
async def list_policies() -> list[PolicyOut]:
    return [PolicyOut(**p) for p in await list_policies_stub()]


@app.post("/v1/policy/evaluate", response_model=PolicyEvaluateResponse)
async def policy_evaluate(
    req: PolicyEvaluateRequest, session: AsyncSession = Depends(get_session)
) -> PolicyEvaluateResponse:
    report = (
        await session.execute(
            select(db_models.TrustReport).where(
                db_models.TrustReport.artifact_id == req.artifact_id
            )
        )
    ).scalar_one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="report_not_ready")
    trust = {
        "score": report.trust_score,
        "confidence_band_90": (report.confidence_low, report.confidence_high),
        "max_trust_cap": report.max_trust_cap,
        "status": report.status,
    }
    provenance = dict(report.report_json.get("provenance", {}))
    # Back-compat: if report provenance doesn't include summary, infer from stored status.
    provenance.setdefault("integrity_failed", report.status == "contradicted")
    provenance.setdefault("verified", report.status == "verified")

    decision = evaluate_policy(
        policy_id=req.policy_id,
        artifact_id=req.artifact_id,
        trust=trust,
        provenance=provenance,
        context=req.context,
    )
    return PolicyEvaluateResponse(
        policy_id=decision.policy_id,
        policy_version=decision.policy_version,
        artifact_id=decision.artifact_id,
        decision=decision.decision,
        actions=decision.actions,
        rationale=decision.rationale,
    )


def main() -> None:
    uvicorn.run(
        "mti.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )

