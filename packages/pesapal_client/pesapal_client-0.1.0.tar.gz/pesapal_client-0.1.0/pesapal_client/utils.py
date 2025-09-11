import json
from datetime import datetime, timezone

import jwt


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


def is_jwt_expired(token: str) -> bool:
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get("exp")
        if exp is None:
            return True
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        return exp_datetime < datetime.now(tz=timezone.utc)
    except jwt.DecodeError:
        return True
