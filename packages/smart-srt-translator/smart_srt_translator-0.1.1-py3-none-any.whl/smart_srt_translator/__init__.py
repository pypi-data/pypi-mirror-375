from .api import translate_srt_file, TranslateOptions, TranslateResult, apply_resolutions_to_srt
from .smart_pipeline import translate_srt_smart

__all__ = [
    "translate_srt_file",
    "translate_srt_smart",
    "TranslateOptions",
    "TranslateResult",
    "apply_resolutions_to_srt",
]

# Package version (kept in sync with pyproject.toml)
__version__ = "0.1.1"
