# Media Trust Infrastructure (MTI) — Reference Implementation

This repository contains a **production-oriented, provenance-first** implementation of a Media Trust
Infrastructure service:

- **API-first**: upload media, run analysis jobs, fetch audit-grade reports
- **Pluggable signal pipeline**: provenance, watermark/fingerprint, forensics, consistency
- **Probabilistic scoring**: trust score + confidence band + explicit uncertainty
- **Policy engine**: context-dependent decisions (court, insurance, social, dating, HR)
- **Capture SDK**: sign/verify capture manifests binding media hashes to device/app identities

This is **not** an “AI detector.” It computes **media trust** given available evidence.

## Quickstart (local)

Requirements: Python 3.12+

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"

# Initialize DB (auto-creates on first run) and start API:
mti-api

# In another terminal, start the worker:
mti-worker
```

Upload an image:

```bash
curl -sS -F "file=@/path/to/image.jpg" http://127.0.0.1:8000/v1/artifacts | jq .
```

Get job status and report using the returned `job_id` / `artifact_id`.

## Configuration

Environment variables (defaults are safe for local dev):

- `MTI_DB_URL` (default: `sqlite+aiosqlite:///./mti.db`)
- `MTI_OBJECT_STORE_DIR` (default: `./mti_object_store`)
- `MTI_SIGNING_KEY_PATH` (default: `./mti_signing_key.ed25519`)
- `MTI_SIGNING_PUBKEY_PATH` (default: `./mti_signing_key.pub`)

## Capture SDK

Generate a dev keypair:

```bash
mti-capture keygen --out-dir .
```

Sign a file to create a sidecar manifest:

```bash
mti-capture sign --file /path/to/image.jpg --key ./mti_capture_key.ed25519 --out /path/to/image.jpg.mti.json
```

Upload with manifest:

```bash
curl -sS \
  -F "file=@/path/to/image.jpg" \
  -F "manifest=@/path/to/image.jpg.mti.json" \
  http://127.0.0.1:8000/v1/artifacts | jq .
```

## Notes

- For video metadata extraction, MTI will use `ffprobe` if available. If not present, it degrades
  gracefully and reports reduced reliability for video signals.
- SQLite is used by default for portability; swap `MTI_DB_URL` to Postgres in production.

