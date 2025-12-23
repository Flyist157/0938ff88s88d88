from __future__ import annotations

import json
from pathlib import Path

import typer

from mti.capture.manifest import sign_file, verify_manifest
from mti.crypto.ed25519 import generate_keypair

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def keygen(
    out_dir: Path = typer.Option(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    )
) -> None:
    """
    Generate an Ed25519 keypair for capture signing (dev).
    """
    priv, pub = generate_keypair()
    priv_path = out_dir / "mti_capture_key.ed25519"
    pub_path = out_dir / "mti_capture_key.pub"
    priv_path.write_bytes(priv)
    pub_path.write_bytes(pub)
    typer.echo(str(priv_path))
    typer.echo(str(pub_path))


@app.command()
def sign(
    file: Path = typer.Option(..., exists=True, dir_okay=False),
    key: Path = typer.Option(
        ...,
        exists=True,
        dir_okay=False,
        help="Private key (raw 32 bytes)",
    ),
    pub: Path | None = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        help="Public key (raw 32 bytes)",
    ),
    out: Path = typer.Option(
        ...,
        dir_okay=False,
        help="Output manifest path (.json)",
    ),
    device_id: str = typer.Option("dev-device", help="Device identifier"),
    app_id: str = typer.Option("dev-app", help="App identifier"),
    capture_mode: str = typer.Option("offline", help="offline|online"),
) -> None:
    """
    Sign a file and produce an MTI sidecar manifest.
    """
    priv_raw = key.read_bytes()
    if pub is None:
        # This CLI stores keys as raw bytes; we require explicit pub to avoid format ambiguity.
        raise typer.BadParameter("--pub is required (provide the matching public key file)")
    pub_raw = pub.read_bytes()

    manifest = sign_file(
        file_path=file,
        private_key_raw=priv_raw,
        public_key_raw=pub_raw,
        device_id=device_id,
        app_id=app_id,
        capture_mode=capture_mode,
    )
    out.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    typer.echo(str(out))


@app.command()
def verify(
    manifest: Path = typer.Option(..., exists=True, dir_okay=False),
    pub: Path | None = typer.Option(
        None,
        exists=True,
        dir_okay=False,
        help="Public key override (raw 32 bytes)",
    ),
) -> None:
    """
    Verify an MTI sidecar manifest signature.
    """
    m = json.loads(manifest.read_text(encoding="utf-8"))
    pub_raw = pub.read_bytes() if pub else None
    ok = verify_manifest(m, public_key_raw=pub_raw)
    raise typer.Exit(code=0 if ok else 1)

