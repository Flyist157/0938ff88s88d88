from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyDecision:
    policy_id: str
    policy_version: str
    artifact_id: str
    decision: str
    actions: list[dict[str, Any]]
    rationale: list[str]


def evaluate_policy(
    *,
    policy_id: str,
    artifact_id: str,
    trust: dict[str, Any],
    provenance: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> PolicyDecision:
    """
    Policy engine is intentionally separate from scoring.
    It maps trust evidence to actions depending on use case.
    """
    context = context or {}
    risk_tolerance = str(context.get("risk_tolerance", "normal")).lower()
    # Risk tolerance adjusts thresholds without touching the trust engine.
    # - strict: higher requirements
    # - normal: defaults
    # - lenient: lower requirements (never used for court evidence)
    if risk_tolerance not in {"strict", "normal", "lenient"}:
        risk_tolerance = "normal"

    score = int(trust["score"])
    low, _high = trust["confidence_band_90"]
    status = trust["status"]
    max_cap = int(trust["max_trust_cap"])
    integrity_failed = bool(provenance.get("integrity_failed"))
    verified = bool(provenance.get("verified"))

    actions: list[dict[str, Any]] = []
    rationale: list[str] = []

    def add(action_type: str, **kwargs: Any) -> None:
        actions.append({"type": action_type, **kwargs})

    if policy_id == "court_evidence":
        version = "2025.12"
        min_low = 80 if risk_tolerance == "strict" else 75
        if integrity_failed:
            decision = "quarantine"
            rationale.append("Cryptographic integrity failed or binding mismatched.")
            add("require_human_review", queue="evidence_integrity")
            add("preserve_original", note="Do not transform input; keep chain-of-custody.")
        elif verified and low >= min_low:
            decision = "accept_high_assurance"
            rationale.append("Verified provenance with high lower-bound confidence.")
            add("generate_admissibility_packet", include="hashes, signatures, audit_chain")
        else:
            decision = "accept_unverified_with_disclosure"
            rationale.append(
                "Origin cannot be fully established; accept with explicit uncertainty."
            )
            add("require_affidavit", fields=["source", "custody", "transformations"])
            add("require_human_review", queue="evidence_triage")
        return PolicyDecision(policy_id, version, artifact_id, decision, actions, rationale)

    if policy_id == "insurance_claim":
        version = "2025.12"
        min_low = 75 if risk_tolerance == "strict" else (65 if risk_tolerance == "lenient" else 70)
        if integrity_failed or status == "contradicted":
            decision = "fraud_queue"
            rationale.append("Integrity failed or strong contradictions detected.")
            add(
                "request_recapture",
                method="authenticated_capture",
                reason="integrity_or_contradiction",
            )
            add("assign_adjuster_review", priority="high")
        elif verified and low >= min_low:
            decision = "fast_track"
            rationale.append("Verified capture and sufficient confidence.")
            add("auto_adjudicate", sampling_rate="low")
        elif score >= 45 and max_cap >= 60:
            decision = "standard_processing"
            rationale.append(
                "No strong red flags, but origin unverified; handle with normal controls."
            )
            add("post_audit_sampling", sampling_rate="medium")
        else:
            decision = "request_more_evidence"
            rationale.append("Uncertainty too high for automated processing.")
            add("request_recapture", method="authenticated_capture", reason="high_uncertainty")
        return PolicyDecision(policy_id, version, artifact_id, decision, actions, rationale)

    if policy_id == "social_moderation":
        version = "2025.12"
        # Social policies avoid defamatory claims.
        if integrity_failed or status == "contradicted":
            decision = "limit_distribution"
            rationale.append("Strong evidence of manipulation or integrity failure.")
            add(
                "apply_label",
                label="origin_or_integrity_failed",
                user_text="Origin/integrity could not be verified.",
            )
            add("reduce_virality", factor=0.2)
            add("queue_human_review", priority="medium")
        elif verified:
            decision = "allow_verified"
            rationale.append("Verified provenance present.")
            add("apply_label", label="provenance_verified", user_text="Provenance verified.")
        else:
            decision = "allow_with_context"
            rationale.append("Provenance absent or inconclusive; do not overclaim.")
            add("apply_label", label="provenance_unverified", user_text="Provenance not verified.")
        return PolicyDecision(policy_id, version, artifact_id, decision, actions, rationale)

    if policy_id == "dating_verification":
        version = "2025.12"
        if integrity_failed:
            decision = "block_and_escalate"
            rationale.append("Integrity failure detected.")
            add("require_liveness", method="guided_video", reason="integrity_failure")
            add("limit_account_features", until="verification_complete")
        elif verified and low >= 80:
            decision = "grant_verified_badge"
            rationale.append("High-assurance verified capture.")
            add("grant_badge", badge="verified_media")
        else:
            decision = "provisional"
            rationale.append("No high-assurance provenance; allow but do not badge.")
            add("offer_verification_capture", method="authenticated_capture")
        return PolicyDecision(policy_id, version, artifact_id, decision, actions, rationale)

    if policy_id == "employment_screening":
        version = "2025.12"
        # Never auto-reject solely based on trust uncertainty.
        if integrity_failed or status == "contradicted":
            decision = "human_review_required"
            rationale.append(
                "Contradiction/integrity failure requires human review; "
                "avoid automated adverse action."
            )
            add(
                "request_secondary_verification",
                methods=["live_interview", "document_verification"],
            )
            add("flag_for_compliance_review")
        elif verified and low >= 75:
            decision = "accept_with_record"
            rationale.append("Verified provenance; store audit record.")
            add("store_audit_record", retention="per_policy")
        else:
            decision = "request_secondary_verification"
            rationale.append("Unverified origin; request alternative verification path.")
            add("request_secondary_verification", methods=["live_interview", "reference_checks"])
        return PolicyDecision(policy_id, version, artifact_id, decision, actions, rationale)

    # Unknown policy: safe fallback
    return PolicyDecision(
        policy_id,
        "unknown",
        artifact_id,
        "no_policy",
        [{"type": "error", "message": "Unknown policy_id"}],
        ["Unknown policy_id; no decision applied."],
    )

