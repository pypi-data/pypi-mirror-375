from __future__ import annotations

import json
from dataclasses import asdict
from typing import List

from .models import AudioRequest, Resolution


def write_requests_json(path: str, requests: List[AudioRequest]) -> None:
    data = [asdict(r) for r in requests]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_resolutions_json(path: str) -> List[Resolution]:
    # Use utf-8-sig to be tolerant of BOM from some editors
    with open(path, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    return [Resolution(**item) for item in raw]


def read_requests_json(path: str) -> List[AudioRequest]:
    with open(path, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    return [AudioRequest(**item) for item in raw]
