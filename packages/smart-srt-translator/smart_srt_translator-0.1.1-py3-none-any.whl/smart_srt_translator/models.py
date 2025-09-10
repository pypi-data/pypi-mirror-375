from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Literal, Optional, Sequence


Timecode = str  # format: HH:MM:SS,mmm


@dataclass
class Segment:
    index: int
    start: Timecode
    end: Timecode
    text: str


@dataclass
class SegmentIssue:
    segment_id: int
    index: int
    start: Timecode
    end: Timecode
    source_text: str
    draft_translation: Optional[str]
    reason: str
    confidence: float


@dataclass
class AudioRequest:
    request_id: str
    segment_id: int
    start: Timecode
    end: Timecode
    reason: str
    expected_response: Literal["transcript", "confirmation", "term-meaning"]


@dataclass
class Resolution:
    request_id: str
    segment_id: Optional[int] = None
    transcript_text: Optional[str] = None
    corrected_translation: Optional[str] = None
    confirmed_term: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class TranslateOptions:
    provider: Optional["TranslatorProvider"] = None
    src_lang: Optional[str] = None
    tgt_lang: str = "en"
    probe_mode: Literal["off", "ask", "auto"] = "off"
    audio_source: Optional[str] = None
    uncertainty_threshold: float = 0.7
    output_path: Optional[str] = None


@dataclass
class TranslateHooks:
    on_issue: Optional[Callable[[SegmentIssue], Optional[Resolution]]] = None
    on_progress: Optional[Callable[[int, int], None]] = None  # processed, total
    on_log: Optional[Callable[[str], None]] = None


@dataclass
class TranslateResult:
    output_path: Optional[str]
    issues: List[SegmentIssue] = field(default_factory=list)
    pending_requests: List[AudioRequest] = field(default_factory=list)
    segments: List[Segment] = field(default_factory=list)


# Provider protocol hints (no runtime import cycle)
class TranslatorProvider:  # pragma: no cover - protocol-ish
    def translate_texts(
        self, texts: Sequence[str], src_lang: Optional[str], tgt_lang: str
    ) -> List[str]:
        raise NotImplementedError


class TranscriberProvider:  # pragma: no cover - protocol-ish
    def transcribe_segment(self, audio_path: str, start: Timecode, end: Timecode) -> str:
        raise NotImplementedError
