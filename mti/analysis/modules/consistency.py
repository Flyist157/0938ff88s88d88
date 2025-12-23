from __future__ import annotations

from mti.analysis.modules.base import SignalModule
from mti.analysis.types import ArtifactContext, SignalCandidate


class ConsistencyModule(SignalModule):
    name = "consistency"

    async def analyze(self, ctx: ArtifactContext) -> list[SignalCandidate]:
        # Reference implementation: minimal checks; production would do temporal/physical constraints.
        # Here we only emit an explicit "not assessed" with low reliability to avoid false certainty.
        return [
            SignalCandidate(
                pillar="consistency",
                signal_id="consistency.assessment",
                finding="not_assessed",
                value=0.5,
                reliability=0.1,
                evidence_refs={},
                raw={"note": "consistency analysis not implemented in reference build"},
            )
        ]

