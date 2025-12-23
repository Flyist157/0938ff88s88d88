from __future__ import annotations

import datetime as dt
from typing import Any

from mti.analysis.modules.consistency import ConsistencyModule
from mti.analysis.modules.forensics import ForensicsModule
from mti.analysis.modules.provenance import ProvenanceModule
from mti.analysis.modules.watermark import WatermarkModule
from mti.analysis.types import ArtifactContext, SignalCandidate


class AnalysisPipeline:
    def __init__(self) -> None:
        self.modules = [
            ProvenanceModule(),
            WatermarkModule(),
            ForensicsModule(),
            ConsistencyModule(),
        ]

    async def run(self, ctx: ArtifactContext) -> tuple[list[SignalCandidate], dict[str, Any]]:
        signals: list[SignalCandidate] = []
        for module in self.modules:
            out = await module.analyze(ctx)
            signals.extend(out)
        meta = {
            "analyzed_at": dt.datetime.now(dt.UTC).isoformat(),
            "module_count": len(self.modules),
        }
        return signals, meta

