from datetime import datetime, time, date
from functools import lru_cache
from typing import Any, Union, Dict, List
from bson import ObjectId

@lru_cache(maxsize=128)
def parse_datetime_or_time(value: str) -> Union[datetime, time, str]:
    """Try to parse a string into datetime or time."""
    formats = [
        # UTC datetime formats (most common)
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2025-09-10T05:30:00.000Z
        "%Y-%m-%dT%H:%M:%SZ",     # 2025-09-10T05:30:00Z
        "%Y-%m-%dT%H:%M:%S%z",    # 2025-09-10T05:30:00+00:00
        "%Y-%m-%dT%H:%M:%S.%f%z", # 2025-09-10T05:30:00.000+00:00
        "%Y-%m-%dT%H:%M:%S.%f",   # 2025-09-10T05:30:00.000
        "%Y-%m-%dT%H:%M:%S",      # 2025-09-10T05:30:00
        # Date formats
        "%Y-%m-%d",               # 2025-09-10
        "%Y/%m/%d",               # 2025/09/10
        "%m-%d-%Y",               # 09-10-2025
        "%m/%d/%Y",               # 09/10/2025
        # Space-separated formats
        "%Y-%m-%d %H:%M:%S",      # 2025-09-10 05:30:00
        "%Y-%m-%d %H:%M:%S.%f",   # 2025-09-10 05:30:00.000
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed
        except Exception:
            continue
    return value


BOOLEAN_MAP = {"true": True, "false": False}


def coerce_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: coerce_value(v) for k, v in value.items()}

    if isinstance(value, list):
        return [coerce_value(v) for v in value]

    if isinstance(value, str):
        # Boolean
        lowered = value.lower()
        if lowered in BOOLEAN_MAP:
            return BOOLEAN_MAP[lowered]
        # ObjectId
        try:
            if ObjectId.is_valid(value):
                return ObjectId(value)
        except Exception as e:
            pass
        # Date or time
        return parse_datetime_or_time(value)

    # Everything else (int, float, None)
    return value