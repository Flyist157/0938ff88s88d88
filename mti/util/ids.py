from __future__ import annotations

import ulid


def new_ulid(prefix: str) -> str:
    return f"{prefix}:{ulid.new().str}"

