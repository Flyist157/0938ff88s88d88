from __future__ import annotations

import io
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from mti import config
from mti.api.main import app
from mti.db import get_sessionmaker, init_db
from mti.worker import process_one


@pytest.mark.asyncio
async def test_upload_analyze_report(tmp_path: Path) -> None:
    # Configure isolated paths before engine creation.
    config.settings.db_url = f"sqlite+aiosqlite:///{(tmp_path / 'mti_test.db').as_posix()}"
    config.settings.object_store_dir = tmp_path / "obj"
    config.settings.signing_key_path = tmp_path / "svc_key.ed25519"
    config.settings.signing_pubkey_path = tmp_path / "svc_key.pub"

    await init_db()

    # Build an in-memory JPEG.
    img = Image.new("RGB", (64, 64), color=(10, 20, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/v1/artifacts",
            files={"file": ("test.jpg", buf.read(), "image/jpeg")},
        )
        assert resp.status_code == 200
        data = resp.json()
        artifact_id = data["artifact_id"]
        job_id = data["job_id"]

        # Run worker once to process queued job.
        async with get_sessionmaker()() as session:
            did = await process_one(session)
            assert did is True

        job = await client.get(f"/v1/jobs/{job_id}")
        assert job.status_code == 200
        assert job.json()["status"] == "succeeded"

        report = await client.get(f"/v1/artifacts/{artifact_id}/report")
        assert report.status_code == 200
        rj = report.json()
        assert rj["artifact_id"] == artifact_id
        assert "trust" in rj
        assert "score" in rj["trust"]
        assert rj["report_signature_b64"]
        assert rj["signer_pubkey_b64"]

