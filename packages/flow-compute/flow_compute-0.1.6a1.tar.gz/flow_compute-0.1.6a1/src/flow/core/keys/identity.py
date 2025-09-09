from __future__ import annotations

"""Key Identity Graph: local mapping between platform key IDs and private paths.

Centralizes persistence and lookup of SSH key identity data so multiple layers
(CLI, providers, wizards) can share a single source of truth.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_META_PATH = Path.home() / ".flow" / "keys" / "metadata.json"


def _load_all() -> dict[str, Any]:
    try:
        if _META_PATH.exists():
            return json.loads(_META_PATH.read_text()) or {}
    except Exception:
        return {}
    return {}


def _save_all(data: dict[str, Any]) -> None:
    try:
        _META_PATH.parent.mkdir(parents=True, exist_ok=True)
        _META_PATH.write_text(json.dumps(data, indent=2))
        try:
            _META_PATH.chmod(0o600)
        except Exception:
            pass
    except Exception:
        # Best-effort persistence
        pass


def store_mapping(
    *,
    key_id: str,
    key_name: str,
    private_key_path: Path,
    project_id: str | None = None,
    auto_generated: bool = False,
) -> None:
    """Persist mapping from platform key ID to local private key path.

    Keeps the existing metadata schema for backward compatibility.
    """
    if not key_id or not str(private_key_path):
        return
    metadata = _load_all()
    entry = {
        "key_id": key_id,
        "key_name": key_name,
        "private_key_path": str(private_key_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": project_id,
        "auto_generated": bool(auto_generated),
    }
    metadata[key_id] = entry
    _save_all(metadata)


def get_local_private_path(key_id: str) -> Path | None:
    """Return the local private key path for a given platform key ID, if known."""
    try:
        data = _load_all()
        info = (data or {}).get(key_id)
        if not info:
            return None
        p = Path(info.get("private_key_path", ""))
        return p if p.exists() else None
    except Exception:
        return None
