from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Literal

MediaType = Literal["image", "video", "audio", "unknown"]


@dataclasses.dataclass(frozen=True)
class ArtifactContext:
    artifact_id: str
    file_path: Path
    manifest_path: Path | None
    filename: str
    content_type: str
    media_type: MediaType
    sha256: str
    size_bytes: int
    derived: dict[str, Any]


@dataclasses.dataclass(frozen=True)
class SignalCandidate:
    pillar: str
    signal_id: str
    finding: str
    value: float  # [0,1]
    reliability: float  # [0,1]
    evidence_refs: dict[str, Any]
    raw: dict[str, Any]

