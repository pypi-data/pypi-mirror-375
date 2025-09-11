import base64
import json
from datetime import datetime, timedelta, timezone


def deep_json_parse(data):
    if isinstance(data, dict):
        return {k: deep_json_parse(v) for k, v in data.items()}
    if isinstance(data, list):
        return [deep_json_parse(v) for v in data]
    if isinstance(data, str):
        try:
            return deep_json_parse(json.loads(data))
        except (ValueError, TypeError):
            return data
    return data


def is_jwt_expired(token: str, window: int = 30) -> bool:
    """
    Check if a JWT token is expired or will expire within the given window (in seconds).
    Works without verifying the signature.
    """
    try:
        # Split JWT into 3 parts
        parts = token.split(".")
        if len(parts) < 2:
            return True  # invalid structure

        payload_b64 = parts[1]

        # Add padding if missing (base64 requires multiple of 4 length)
        padding = "=" * (-len(payload_b64) % 4)
        payload_b64 += padding

        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        payload = json.loads(payload_json)

        exp = payload.get("exp")
        if exp is None:
            return True

        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        return exp_datetime < datetime.now(tz=timezone.utc) + timedelta(seconds=window)

    except (ValueError, json.JSONDecodeError, base64.binascii.Error):
        return True
