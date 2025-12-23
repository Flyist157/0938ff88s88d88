from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    media_type: Mapped[str] = mapped_column(String(64), nullable=False)  # image|video|audio|unknown
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)

    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    object_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    manifest_object_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)

    jobs: Mapped[list["Job"]] = relationship(back_populates="artifact", cascade="all, delete-orphan")
    signals: Mapped[list["SignalResult"]] = relationship(
        back_populates="artifact", cascade="all, delete-orphan"
    )
    report: Mapped["TrustReport | None"] = relationship(
        back_populates="artifact", cascade="all, delete-orphan", uselist=False
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # queued|running|succeeded|failed

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    analysis_version: Mapped[str] = mapped_column(String(64), nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    artifact: Mapped["Artifact"] = relationship(back_populates="jobs")


class SignalResult(Base):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id"), index=True)

    pillar: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    signal_id: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    finding: Mapped[str] = mapped_column(String(128), nullable=False)

    value: Mapped[float] = mapped_column(nullable=False)  # normalized [0,1]
    reliability: Mapped[float] = mapped_column(nullable=False)  # normalized [0,1]

    evidence_refs: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    raw: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)

    artifact: Mapped["Artifact"] = relationship(back_populates="signals")


class TrustReport(Base):
    __tablename__ = "trust_reports"

    artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id"), primary_key=True)

    trust_score: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_low: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_high: Mapped[int] = mapped_column(Integer, nullable=False)
    max_trust_cap: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)  # verified|unverified|inconclusive|contradicted

    contradictions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    recommendations: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    report_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    report_signature_b64: Mapped[str] = mapped_column(Text, nullable=False)
    signer_pubkey_b64: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)

    artifact: Mapped["Artifact"] = relationship(back_populates="report")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)

    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    artifact_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    job_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    prev_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    signature_b64: Mapped[str] = mapped_column(Text, nullable=False)
    signer_pubkey_b64: Mapped[str] = mapped_column(Text, nullable=False)

