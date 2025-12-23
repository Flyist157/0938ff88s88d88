from __future__ import annotations

from mti.analysis.modules.base import SignalModule
from mti.analysis.types import ArtifactContext, SignalCandidate


class WatermarkModule(SignalModule):
    name = "watermark"

    async def analyze(self, ctx: ArtifactContext) -> list[SignalCandidate]:
        # Production design: would integrate verifiable watermark schemes and vendor detectors.
        # This reference implementation reports "no reliable watermark evidence" explicitly.
        return [
            SignalCandidate(
                pillar="watermark",
                signal_id="wm.detect",
                finding="no_reliable_evidence",
                value=0.5,
                reliability=0.15,
                evidence_refs={},
                raw={
                    "note": (
                        "watermark detection not implemented in reference build; "
                        "absence is not evidence"
                    ),
                    "media_type": ctx.media_type,
                },
            )
        ]

