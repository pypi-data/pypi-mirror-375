from __future__ import annotations

import os
from typing import List, Optional, Sequence

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from .base import TranslatorProvider


class OpenAITranslator(TranslatorProvider):
    """OpenAI-based translator.

    Requires `openai` package and `OPENAI_API_KEY` in environment. Uses
    the newer `openai>=1.0.0` style client if available.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        if OpenAI is None:
            raise RuntimeError(
                "openai package not installed. Install with 'pip install smart-srt-translator[openai]'."
            )
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=self.api_key)

    def translate_texts(
        self, texts: Sequence[str], src_lang: Optional[str], tgt_lang: str
    ) -> List[str]:
        # Simple batching call: instruct model to translate each line, preserving line breaks.
        # This is a minimal viable implementation; can be replaced with a more
        # sophisticated prompt and sentence grouping.
        prompt = self._build_prompt(texts, src_lang, tgt_lang)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You translate subtitles accurately."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content or ""
        outputs = [line for line in content.splitlines()]
        if len(outputs) != len(texts):
            # Fallback: return a single block or pad/truncate
            if len(outputs) == 1 and "\n" in outputs[0]:
                outputs = outputs[0].splitlines()
        # Normalize sizes
        if len(outputs) < len(texts):
            outputs += [""] * (len(texts) - len(outputs))
        return outputs[: len(texts)]

    @staticmethod
    def _build_prompt(texts: Sequence[str], src_lang: Optional[str], tgt_lang: str) -> str:
        src = src_lang or "auto-detect"
        lines = "\n".join(texts)
        return (
            f"Translate the following {src} subtitles to {tgt_lang}.\n"
            "Return exactly the same number of lines, in order, one translation per input line.\n\n"
            f"{lines}"
        )

