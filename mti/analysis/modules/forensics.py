from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from PIL import Image

from mti.analysis.modules.base import SignalModule
from mti.analysis.types import ArtifactContext, SignalCandidate


def _jpeg_quant_table_strength(img: Image.Image) -> dict[str, Any] | None:
    # Pillow exposes quantization tables for JPEG; presence indicates JPEG compression.
    q = getattr(img, "quantization", None)
    if not q or not isinstance(q, dict):
        return None
    # Smaller values generally mean higher quality; this is a crude metric.
    vals: list[int] = []
    for table in q.values():
        if isinstance(table, list):
            vals.extend([int(x) for x in table if isinstance(x, int)])
    if not vals:
        return None
    return {
        "q_min": min(vals),
        "q_max": max(vals),
        "q_mean": sum(vals) / len(vals),
    }


def _safe_open_image(path: Path) -> Image.Image | None:
    try:
        img = Image.open(path)
        img.load()
        return img
    except Exception:  # noqa: BLE001
        return None


class ForensicsModule(SignalModule):
    name = "forensics"

    async def analyze(self, ctx: ArtifactContext) -> list[SignalCandidate]:
        if ctx.media_type != "image":
            return [
                SignalCandidate(
                    pillar="forensics",
                    signal_id="forensics.support",
                    finding="not_implemented_for_media_type",
                    value=0.5,
                    reliability=0.2,
                    evidence_refs={},
                    raw={"media_type": ctx.media_type},
                )
            ]

        img = _safe_open_image(ctx.file_path)
        if img is None:
            return [
                SignalCandidate(
                    pillar="forensics",
                    signal_id="img.decode",
                    finding="decode_failed",
                    value=0.0,
                    reliability=0.9,
                    evidence_refs={},
                    raw={},
                )
            ]

        w, h = img.size
        fmt = (img.format or "").upper()
        mode = img.mode

        qinfo = _jpeg_quant_table_strength(img) if fmt == "JPEG" else None
        # Rough "recompression suspicion" heuristic:
        # - Very low quality JPEG + missing EXIF can be benign (platform transcode), but degrades evidentiary value.
        compression_deg = 0.0
        if qinfo is not None:
            q_mean = float(qinfo["q_mean"])
            # Map q_mean into 0..1 where higher means heavier quantization.
            compression_deg = max(0.0, min(1.0, (q_mean - 20.0) / 60.0))

        # EXIF presence is weak evidence; we use it for reliability gating only.
        exif = {}
        try:
            exif_raw = img.getexif()
            if exif_raw:
                exif = {"count": len(exif_raw)}
        except Exception:  # noqa: BLE001
            exif = {"count": 0, "error": "exif_read_failed"}

        # Findings: "compression_heavy" reduces trust (integrity harder to establish), not "fake".
        candidates: list[SignalCandidate] = []
        candidates.append(
            SignalCandidate(
                pillar="forensics",
                signal_id="img.metadata.exif_present",
                finding="present" if exif.get("count", 0) else "absent",
                value=1.0 if exif.get("count", 0) else 0.5,
                reliability=0.4,
                evidence_refs={},
                raw=exif,
            )
        )

        if qinfo is not None:
            finding = "compression_heavy" if compression_deg >= 0.6 else "compression_moderate"
            # Convert compression to a trust contribution: heavier compression => lower value.
            value = 1.0 - compression_deg
            reliability = 0.55  # heuristic; decomposes under platform transcodes
            candidates.append(
                SignalCandidate(
                    pillar="forensics",
                    signal_id="img.compression.estimated",
                    finding=finding,
                    value=max(0.0, min(1.0, value)),
                    reliability=reliability,
                    evidence_refs={},
                    raw={"format": fmt, "qinfo": qinfo, "compression_degree": compression_deg},
                )
            )
        else:
            candidates.append(
                SignalCandidate(
                    pillar="forensics",
                    signal_id="img.compression.estimated",
                    finding="unknown_non_jpeg",
                    value=0.6,
                    reliability=0.25,
                    evidence_refs={},
                    raw={"format": fmt},
                )
            )

        # Simple sanity checks for obviously invalid images (rare but important).
        megapixels = (w * h) / 1_000_000.0
        size_mib = ctx.size_bytes / (1024 * 1024)
        bpp = (ctx.size_bytes * 8) / max(1.0, w * h)
        # If bpp is implausibly low for JPEG/PNG, file may be aggressively compressed or corrupted.
        implausible = (fmt in {"JPEG", "PNG"} and bpp < 0.2 and megapixels > 0.2) or math.isnan(bpp)
        candidates.append(
            SignalCandidate(
                pillar="forensics",
                signal_id="img.encoding.plausibility",
                finding="implausible" if implausible else "plausible",
                value=0.2 if implausible else 0.8,
                reliability=0.7,
                evidence_refs={},
                raw={"width": w, "height": h, "format": fmt, "mode": mode, "size_mib": size_mib, "bpp": bpp},
            )
        )
        return candidates

