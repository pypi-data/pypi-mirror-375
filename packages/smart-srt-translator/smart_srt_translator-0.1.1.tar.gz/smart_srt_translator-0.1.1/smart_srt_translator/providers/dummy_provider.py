from __future__ import annotations

from typing import List, Optional, Sequence

from .base import TranslatorProvider


class DummyTranslator(TranslatorProvider):
    """A no-op translator useful for wiring and tests.

    It returns the input text unchanged.
    """

    def translate_texts(
        self, texts: Sequence[str], src_lang: Optional[str], tgt_lang: str
    ) -> List[str]:
        return list(texts)

