from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Sequence


class TranslatorProvider(ABC):
    @abstractmethod
    def translate_texts(
        self, texts: Sequence[str], src_lang: Optional[str], tgt_lang: str
    ) -> List[str]:
        ...


class TranscriberProvider(ABC):
    @abstractmethod
    def transcribe_segment(self, audio_path: str, start: str, end: str) -> str:
        ...

