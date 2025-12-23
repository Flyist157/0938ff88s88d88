from __future__ import annotations

import datetime as dt
from typing import Any, Literal

from pydantic import BaseModel, Field


MediaType = Literal["image", "video", "audio", "unknown"]
JobStatus = Literal["queued", "running", "succeeded", "failed"]


class ArtifactCreateResponse(BaseModel):
    artifact_id: str
    job_id: str


class ArtifactOut(BaseModel):
    id: str
    filename: str
    media_type: MediaType
    content_type: str
    sha256: str
    size_bytes: int
    created_at: dt.datetime


class JobOut(BaseModel):
    id: str
    artifact_id: str
    status: JobStatus
    created_at: dt.datetime
    started_at: dt.datetime | None
    completed_at: dt.datetime | None
    analysis_version: str
    error: str | None


class SignalOut(BaseModel):
    pillar: str
    signal_id: str
    finding: str
    value: float = Field(ge=0.0, le=1.0)
    reliability: float = Field(ge=0.0, le=1.0)
    evidence_refs: dict[str, Any] = Field(default_factory=dict)


class TrustOut(BaseModel):
    score: int = Field(ge=0, le=100)
    confidence_band_90: tuple[int, int] = Field(
        description="90% confidence interval [low, high] in 0..100"
    )
    max_trust_cap: int = Field(ge=0, le=100)
    status: Literal["verified", "unverified", "inconclusive", "contradicted"]


class TrustReportOut(BaseModel):
    artifact_id: str
    input_fingerprint: dict[str, Any]
    provenance: dict[str, Any]
    trust: TrustOut
    signals: list[SignalOut]
    contradictions: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    audit: dict[str, Any]


class PolicyEvaluateRequest(BaseModel):
    artifact_id: str
    policy_id: str
    context: dict[str, Any] = Field(default_factory=dict)


class PolicyEvaluateResponse(BaseModel):
    policy_id: str
    policy_version: str
    artifact_id: str
    decision: str
    actions: list[dict[str, Any]] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)


class PolicyOut(BaseModel):
    id: str
    version: str
    description: str

