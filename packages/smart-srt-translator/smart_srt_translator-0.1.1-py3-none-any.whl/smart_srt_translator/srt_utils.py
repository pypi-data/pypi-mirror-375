from __future__ import annotations

from typing import List

from .models import Segment


def parse_srt(content: str) -> List[Segment]:
    segments: List[Segment] = []
    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = [l.rstrip("\r") for l in block.splitlines()]
        if len(lines) < 2:
            continue
        try:
            index = int(lines[0].strip())
        except ValueError:
            # Some SRTs might lack numeric index; fallback
            index = len(segments) + 1
            ts_line = lines[0]
            text_lines = lines[1:]
        else:
            ts_line = lines[1] if len(lines) > 1 else ""
            text_lines = lines[2:]

        if "-->" not in ts_line:
            # malformed, skip
            continue
        start, end = [part.strip() for part in ts_line.split("-->")]
        text = "\n".join(text_lines).strip()
        segments.append(Segment(index=index, start=start, end=end, text=text))
    return segments


def format_srt(segments: List[Segment]) -> str:
    blocks: List[str] = []
    for i, seg in enumerate(segments, start=1):
        idx = seg.index if isinstance(seg.index, int) else i
        blocks.append(
            f"{idx}\n{seg.start} --> {seg.end}\n{seg.text}".rstrip()
        )
    return "\n\n".join(blocks) + "\n"

