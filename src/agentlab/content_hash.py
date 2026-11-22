"""Stable content hashes for immutable, versioned inputs."""

import hashlib
import json
from typing import Any


def content_hash(value: Any) -> str:
    """Return the SHA-256 hex digest of `value` as canonical JSON.

    Keys are sorted and whitespace is fixed, so the same content always gives the
    same hash regardless of key order, formatting or line endings in the source file.
    """
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
