from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile

from mti.config import settings


def ensure_object_store() -> None:
    settings.object_store_dir.mkdir(parents=True, exist_ok=True)


def artifact_dir(artifact_id: str) -> Path:
    ensure_object_store()
    safe = artifact_id.replace(":", "_")
    p = settings.object_store_dir / safe
    p.mkdir(parents=True, exist_ok=True)
    return p


async def save_upload(upload: UploadFile, dest: Path) -> int:
    """
    Save an UploadFile to dest. Returns bytes written.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    size = 0
    with dest.open("wb") as f:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    return size


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)

