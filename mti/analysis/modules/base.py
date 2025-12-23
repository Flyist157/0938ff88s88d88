from __future__ import annotations

import abc

from mti.analysis.types import ArtifactContext, SignalCandidate


class SignalModule(abc.ABC):
    name: str

    @abc.abstractmethod
    async def analyze(self, ctx: ArtifactContext) -> list[SignalCandidate]:
        raise NotImplementedError

