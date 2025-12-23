from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mti.analysis.types import SignalCandidate


@dataclass(frozen=True)
class TrustResult:
    score: int
    confidence_low: int
    confidence_high: int
    max_trust_cap: int
    status: str
    contradictions: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    provenance_summary: dict[str, Any]


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _clip100(x: float) -> int:
    return int(max(0, min(100, round(x))))


def _get_signal(signals: list[SignalCandidate], signal_id: str) -> SignalCandidate | None:
    for s in signals:
        if s.signal_id == signal_id:
            return s
    return None


def compute_trust(signals: list[SignalCandidate]) -> TrustResult:
    """
    Evidence-first scoring.
    - Provenance verification can cap or sharply reduce trust.
    - Other signals adjust within the cap.
    - Uncertainty is explicit via confidence bands (derived from effective reliability and contradictions).
    """
    contradictions: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    sig_valid = _get_signal(signals, "prov.manifest.signature_valid")
    sha_bind = _get_signal(signals, "prov.manifest.sha256_binding")
    manifest_present = _get_signal(signals, "prov.manifest.present")

    provenance_verified = bool(sig_valid and sig_valid.finding == "valid" and sha_bind and sha_bind.finding == "match")
    provenance_invalid = bool(sig_valid and sig_valid.finding == "invalid") or bool(
        sha_bind and sha_bind.finding == "mismatch"
    )
    provenance_absent = bool(manifest_present and manifest_present.finding == "absent") or (
        sig_valid is None and sha_bind is None
    )

    # Upper bound based on provenance.
    if provenance_verified:
        max_cap = 100
    elif provenance_invalid:
        max_cap = 25
    elif provenance_absent:
        max_cap = 70
    else:
        max_cap = 70

    # Start with a neutral prior inside cap.
    base = 0.65 if provenance_verified else 0.5
    score = base * max_cap

    # Aggregate non-provenance signals as weak/medium evidence.
    # Map each signal's value to a delta around neutral 0.5, scaled by reliability and pillar weight.
    pillar_weights: dict[str, float] = {
        "forensics": 0.9,
        "watermark": 0.6,
        "consistency": 0.7,
        "provenance": 1.0,
    }

    eff_rel = 0.0
    rel_weight_sum = 0.0

    for s in signals:
        w = pillar_weights.get(s.pillar, 0.5)
        r = _clip01(s.reliability)
        rel_weight_sum += w
        eff_rel += w * r

        # Skip provenance signals here; already handled with cap.
        if s.pillar == "provenance":
            continue

        # Convert [0,1] to [-1,1] around 0.5
        centered = (float(s.value) - 0.5) * 2.0
        # A conservative adjustment: at most +/- 20% of cap per fully reliable signal.
        score += centered * (0.2 * max_cap) * (w * r)

    if rel_weight_sum > 0:
        eff_rel = eff_rel / rel_weight_sum
    else:
        eff_rel = 0.0

    # Contradiction detection: provenance verified but strong forensics implausible, or provenance invalid but high others.
    impl = _get_signal(signals, "img.encoding.plausibility")
    if provenance_verified and impl and impl.finding == "implausible" and impl.reliability >= 0.6:
        contradictions.append(
            {
                "type": "provenance_vs_forensics",
                "detail": "Provenance verified but encoding plausibility is implausible.",
                "signals": ["prov.manifest.signature_valid", "img.encoding.plausibility"],
            }
        )
    if provenance_invalid:
        recommendations.append(
            {
                "type": "escalate_human_review",
                "reason": "cryptographic_integrity_failed_or_mismatched",
            }
        )
    if provenance_absent:
        recommendations.append(
            {
                "type": "request_authenticated_recapture",
                "reason": "origin_unverifiable",
            }
        )

    # Apply cap and contradictions.
    score = max(0.0, min(float(max_cap), score))
    if contradictions:
        # Conservative: reduce score and widen uncertainty.
        score *= 0.75

    trust_score = _clip100(score)

    # Confidence band: derived from effective reliability and contradictions.
    # eff_rel near 1 => narrow band; near 0 => wide band.
    width = 8 + int(round((1.0 - eff_rel) * 35))
    if provenance_absent:
        width += 8
    if contradictions:
        width += 12
    low = max(0, trust_score - width)
    high = min(100, trust_score + width)

    if provenance_verified and not contradictions:
        status = "verified"
    elif provenance_invalid:
        status = "contradicted"
    elif provenance_absent:
        status = "unverified"
    else:
        status = "inconclusive"

    provenance_summary = {
        "manifest_provided": not provenance_absent,
        "verified": provenance_verified,
        "integrity_failed": provenance_invalid,
    }

    return TrustResult(
        score=trust_score,
        confidence_low=low,
        confidence_high=high,
        max_trust_cap=max_cap,
        status=status,
        contradictions=contradictions,
        recommendations=recommendations,
        provenance_summary=provenance_summary,
    )

