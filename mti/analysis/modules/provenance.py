from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mti.analysis.modules.base import SignalModule
from mti.analysis.types import ArtifactContext, SignalCandidate
from mti.crypto.ed25519 import b64d, verify
from mti.util.jsoncanon import canonical_json_bytes


def _load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class ProvenanceModule(SignalModule):
    name = "provenance"

    async def analyze(self, ctx: ArtifactContext) -> list[SignalCandidate]:
        # MVP: verify MTI capture sidecar manifest (not full C2PA parsing).
        if ctx.manifest_path is None:
            return [
                SignalCandidate(
                    pillar="provenance",
                    signal_id="prov.manifest.present",
                    finding="absent",
                    value=0.5,
                    reliability=0.95,
                    evidence_refs={},
                    raw={"reason": "no_manifest_provided"},
                )
            ]

        try:
            manifest = _load_manifest(ctx.manifest_path)
        except Exception as e:  # noqa: BLE001
            return [
                SignalCandidate(
                    pillar="provenance",
                    signal_id="prov.manifest.parse",
                    finding="invalid_manifest",
                    value=0.0,
                    reliability=0.95,
                    evidence_refs={"manifest_path": str(ctx.manifest_path)},
                    raw={"error": str(e)},
                )
            ]

        schema = manifest.get("schema")
        payload = manifest.get("payload", {})
        signature_b64 = manifest.get("signature_b64")
        pub_b64 = manifest.get("public_key_b64")

        expected_sha = payload.get("artifact_sha256")
        sha_ok = expected_sha == ctx.sha256

        if not signature_b64 or not pub_b64:
            return [
                SignalCandidate(
                    pillar="provenance",
                    signal_id="prov.manifest.signature",
                    finding="missing_signature",
                    value=0.1,
                    reliability=0.9,
                    evidence_refs={"schema": schema},
                    raw={"has_pub": bool(pub_b64), "has_sig": bool(signature_b64), "sha_matches": sha_ok},
                )
            ]

        # Canonical signing: schema + payload (signature excluded)
        message = canonical_json_bytes({"schema": schema, "payload": payload})
        sig_ok = verify(b64d(pub_b64), message, b64d(signature_b64))

        candidates: list[SignalCandidate] = []
        candidates.append(
            SignalCandidate(
                pillar="provenance",
                signal_id="prov.manifest.sha256_binding",
                finding="match" if sha_ok else "mismatch",
                value=1.0 if sha_ok else 0.0,
                reliability=0.98,
                evidence_refs={"manifest_path": str(ctx.manifest_path)},
                raw={"expected_sha256": expected_sha, "observed_sha256": ctx.sha256},
            )
        )
        candidates.append(
            SignalCandidate(
                pillar="provenance",
                signal_id="prov.manifest.signature_valid",
                finding="valid" if sig_ok else "invalid",
                value=1.0 if sig_ok else 0.0,
                reliability=0.99,
                evidence_refs={"manifest_path": str(ctx.manifest_path)},
                raw={"schema": schema, "signing_message_format": "canonical_json(schema,payload)"},
            )
        )

        # Derive "chain completeness" proxy: if payload contains capture info.
        chain = payload.get("chain", [])
        chain_ok = isinstance(chain, list) and len(chain) >= 1
        candidates.append(
            SignalCandidate(
                pillar="provenance",
                signal_id="prov.chain.present",
                finding="present" if chain_ok else "absent",
                value=1.0 if chain_ok else 0.5,
                reliability=0.8,
                evidence_refs={},
                raw={"chain_len": len(chain) if isinstance(chain, list) else None},
            )
        )
        return candidates

