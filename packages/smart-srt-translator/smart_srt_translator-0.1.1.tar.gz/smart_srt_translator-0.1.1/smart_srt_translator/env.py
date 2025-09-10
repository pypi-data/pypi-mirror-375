from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def _strip_quotes(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1].strip()
    return v


def _load_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    try:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="latin-1").splitlines()
        for line in lines:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.lower().startswith("export "):
                s = s[7:].lstrip()
            if "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            v = _strip_quotes(v)
            env[k] = v
    except Exception:
        pass
    return env


def load_env_vars(candidates: Iterable[Path] | None = None) -> None:
    """Load OPENAI_* vars from .env-style files if not already set.

    Looks for OPENAI_API_KEY and OPENAI_MODEL; does not override existing env.
    Default candidates: ./.env, ./VidScalerSubtitleAdder/.env
    """
    if candidates is None:
        candidates = [Path(".env"), Path("VidScalerSubtitleAdder/.env")]  # common repo locations

    have_key = bool(os.getenv("OPENAI_API_KEY"))
    have_model = bool(os.getenv("OPENAI_MODEL"))
    if have_key and have_model:
        return

    for c in candidates:
        if not c.exists():
            continue
        found = _load_env_file(c)
        if not have_key and "OPENAI_API_KEY" in found:
            os.environ["OPENAI_API_KEY"] = found["OPENAI_API_KEY"]
            have_key = True
        if not have_model and "OPENAI_MODEL" in found:
            os.environ["OPENAI_MODEL"] = found["OPENAI_MODEL"]
            have_model = True
        if have_key and have_model:
            break

