#!/usr/bin/env python3
"""Shared model-observation schema and receiver-owned key exclusion."""
from __future__ import annotations

from typing import Any
from urllib.parse import unquote
import unicodedata


MODEL_OBSERVATION_KEYS = {
    "source_url_or_null",
    "publisher_or_null",
    "title_or_null",
    "original_location_or_null",
    "bounded_summary_or_null",
    "access_state",
    "conditions",
    "limitations",
    "counterevidence",
}
SNAPSHOT_RECEIPT_KEYS = {
    "receipt_id",
    "observation_id",
    "source_observation_reference",
    "receiver_snapshot_reference",
    "receiver_snapshot_sha256",
    "snapshot_capture_state",
    "snapshot_captured_at",
    "receipt_sha256",
}
MAX_KEY_LENGTH = 4096
MAX_DECODE_ROUNDS = 32


def _normalized_key(value: str) -> str | None:
    if len(value) > MAX_KEY_LENGTH:
        return None
    current = value
    for _ in range(MAX_DECODE_ROUNDS):
        normalized = unicodedata.normalize("NFKC", current).casefold()
        combined = unicodedata.normalize("NFKC", unquote(normalized)).casefold()
        if len(combined) > MAX_KEY_LENGTH:
            return None
        if combined == current:
            return "".join(char for char in combined if char.isalnum())
        current = combined
    return None


_FORBIDDEN_NORMALIZED_KEYS = {
    _normalized_key(key) for key in SNAPSHOT_RECEIPT_KEYS
}


def contains_receiver_owned_field(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = _normalized_key(str(key))
            if (
                normalized is None
                or normalized in _FORBIDDEN_NORMALIZED_KEYS
                or "receiver" in normalized
                or contains_receiver_owned_field(item)
            ):
                return True
        return False
    if isinstance(value, list):
        return any(contains_receiver_owned_field(item) for item in value)
    return False


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_model_observation(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == MODEL_OBSERVATION_KEYS
        and all(
            value.get(field) is None or _nonempty(value.get(field))
            for field in (
                "source_url_or_null",
                "publisher_or_null",
                "title_or_null",
                "original_location_or_null",
                "bounded_summary_or_null",
            )
        )
        and _nonempty(value.get("access_state"))
        and all(
            isinstance(value.get(field), list)
            for field in ("conditions", "limitations", "counterevidence")
        )
        and not contains_receiver_owned_field(value)
    )
