from __future__ import annotations

import datetime as dt

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from mti.models.db_models import Artifact, Job, SignalResult, TrustReport
from mti.util.ids import new_ulid


async def create_artifact(
    session: AsyncSession,
    *,
    artifact_id: str,
    filename: str,
    media_type: str,
    content_type: str,
    sha256: str,
    size_bytes: int,
    object_path: str,
    manifest_object_path: str | None,
) -> Artifact:
    artifact = Artifact(
        id=artifact_id,
        filename=filename,
        media_type=media_type,
        content_type=content_type,
        sha256=sha256,
        size_bytes=size_bytes,
        object_path=object_path,
        manifest_object_path=manifest_object_path,
    )
    session.add(artifact)
    await session.commit()
    return artifact


async def get_artifact(session: AsyncSession, artifact_id: str) -> Artifact | None:
    return (
        await session.execute(select(Artifact).where(Artifact.id == artifact_id))
    ).scalar_one_or_none()


async def create_job(session: AsyncSession, *, artifact_id: str, analysis_version: str) -> Job:
    job = Job(
        id=new_ulid("mt:job"),
        artifact_id=artifact_id,
        status="queued",
        analysis_version=analysis_version,
    )
    session.add(job)
    await session.commit()
    return job


async def get_job(session: AsyncSession, job_id: str) -> Job | None:
    return (await session.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()


async def claim_next_job(session: AsyncSession) -> Job | None:
    # SQLite doesn't support SKIP LOCKED; we do a best-effort claim.
    job = (
        await session.execute(
            select(Job).where(Job.status == "queued").order_by(Job.created_at).limit(1)
        )
    ).scalar_one_or_none()
    if job is None:
        return None
    job.status = "running"
    job.started_at = dt.datetime.now(dt.UTC)
    await session.commit()
    return job


async def mark_job_succeeded(session: AsyncSession, job: Job) -> None:
    job.status = "succeeded"
    job.completed_at = dt.datetime.now(dt.UTC)
    await session.commit()


async def mark_job_failed(session: AsyncSession, job: Job, error: str) -> None:
    job.status = "failed"
    job.error = error
    job.completed_at = dt.datetime.now(dt.UTC)
    await session.commit()


async def replace_signals(
    session: AsyncSession,
    artifact_id: str,
    signals: list[SignalResult],
) -> None:
    await session.execute(delete(SignalResult).where(SignalResult.artifact_id == artifact_id))
    for s in signals:
        session.add(s)
    await session.commit()


async def upsert_report(session: AsyncSession, report: TrustReport) -> None:
    existing = (
        await session.execute(
            select(TrustReport).where(TrustReport.artifact_id == report.artifact_id)
        )
    ).scalar_one_or_none()
    if existing is None:
        session.add(report)
    else:
        # Replace fields.
        for k, v in report.__dict__.items():
            if k.startswith("_"):
                continue
            setattr(existing, k, v)
    await session.commit()


async def list_policies_stub() -> list[dict[str, str]]:
    # The policy engine itself is pure code; this is used for the API list endpoint.
    return [
        {
            "id": "court_evidence",
            "version": "2025.12",
            "description": "Conservative evidence handling",
        },
        {
            "id": "insurance_claim",
            "version": "2025.12",
            "description": "Fraud-aware, low-friction triage",
        },
        {
            "id": "social_moderation",
            "version": "2025.12",
            "description": "Scale moderation without defamatory claims",
        },
        {
            "id": "dating_verification",
            "version": "2025.12",
            "description": "Identity trust and liveness escalation",
        },
        {
            "id": "employment_screening",
            "version": "2025.12",
            "description": "Assistive verification; avoid auto-rejection",
        },
    ]

