from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import List, Optional

from .models import (
    AudioRequest,
    Resolution,
    Segment,
    SegmentIssue,
    TranslateHooks,
    TranslateOptions,
    TranslateResult,
    TranslatorProvider,
)
from .providers import DummyTranslator
from .srt_utils import parse_srt, format_srt
from .io_json import write_requests_json


def translate_srt_file(
    input_path: str,
    src_lang: Optional[str],
    tgt_lang: str,
    options: Optional[TranslateOptions] = None,
    hooks: Optional[TranslateHooks] = None,
) -> TranslateResult:
    options = options or TranslateOptions()
    provider: TranslatorProvider = options.provider or DummyTranslator()
    hooks = hooks or TranslateHooks()

    in_path = Path(input_path)
    content = in_path.read_text(encoding="utf-8")
    segments = parse_srt(content)

    # Translate each segment line-preserving
    texts: List[str] = [seg.text for seg in segments]
    translated: List[str] = provider.translate_texts(texts, src_lang, tgt_lang)
    out_segments: List[Segment] = []
    for i, seg in enumerate(segments):
        new_seg = Segment(index=seg.index, start=seg.start, end=seg.end, text=translated[i])
        out_segments.append(new_seg)
        if hooks.on_progress:
            hooks.on_progress(i + 1, len(segments))

    issues: List[SegmentIssue] = []
    pending: List[AudioRequest] = []

    # Heuristics for audio probe requests
    if options.probe_mode in ("ask", "auto"):
        flagged_indices = set()

        # 1) Flag empty/zero-length source segments first
        for i, seg in enumerate(segments):
            is_empty_text = not seg.text.strip()
            is_zero_length = seg.start == seg.end
            if is_empty_text or is_zero_length:
                reason = "empty-source" if is_empty_text else "zero-length"
                issue = SegmentIssue(
                    segment_id=seg.index,
                    index=i + 1,
                    start=seg.start,
                    end=seg.end,
                    source_text=seg.text,
                    draft_translation=out_segments[i].text,
                    reason=reason,
                    confidence=0.2,
                )
                issues.append(issue)
                pending.append(
                    AudioRequest(
                        request_id=str(uuid.uuid4()),
                        segment_id=seg.index,
                        start=seg.start,
                        end=seg.end,
                        reason=reason,
                        expected_response="transcript",
                    )
                )
                flagged_indices.add(i)
                if hooks.on_issue:
                    try:
                        res = hooks.on_issue(issue)
                    except Exception:
                        res = None
                    if res and res.corrected_translation:
                        out_segments[i].text = res.corrected_translation

        # 2) If translation came back empty while source non-empty (and not already flagged),
        #    flag as potential issue needing transcript.
        for i, (src, dst, seg) in enumerate(zip(texts, translated, segments)):
            if i in flagged_indices:
                continue
            if src.strip() and not dst.strip():
                issue = SegmentIssue(
                    segment_id=seg.index,
                    index=i + 1,
                    start=seg.start,
                    end=seg.end,
                    source_text=src,
                    draft_translation=dst,
                    reason="empty-translation",
                    confidence=0.3,
                )
                issues.append(issue)
                pending.append(
                    AudioRequest(
                        request_id=str(uuid.uuid4()),
                        segment_id=seg.index,
                        start=seg.start,
                        end=seg.end,
                        reason="empty-translation",
                        expected_response="transcript",
                    )
                )
                if hooks.on_issue:
                    try:
                        res = hooks.on_issue(issue)
                    except Exception:
                        res = None
                    if res and res.corrected_translation:
                        out_segments[i].text = res.corrected_translation

    # Write output SRT
    out_path = _compute_output_path(str(in_path), tgt_lang, options.output_path)
    Path(out_path).write_text(format_srt(out_segments), encoding="utf-8")

    # If we have pending requests and probe is ask, persist them next to output
    if pending and options.probe_mode == "ask":
        req_path = os.fspath(Path(out_path).with_suffix(".requests.json"))
        write_requests_json(req_path, pending)

    return TranslateResult(
        output_path=out_path, issues=issues, pending_requests=pending, segments=out_segments
    )


def _compute_output_path(input_path: str, tgt_lang: str, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    p = Path(input_path)
    stem = p.stem
    parent = p.parent
    candidate = parent / f"{stem}_translated_{tgt_lang}{p.suffix}"
    # avoid overwrite: if exists, add numeric suffix
    if not candidate.exists():
        return os.fspath(candidate)
    i = 2
    while True:
        cand = parent / f"{stem}_translated_{tgt_lang}_{i}{p.suffix}"
        if not cand.exists():
            return os.fspath(cand)
        i += 1


def apply_resolutions_to_srt(
    translated_srt_path: str,
    resolutions: List[Resolution],
    request_to_segment: Optional[dict[str, int]] = None,
    output_path: Optional[str] = None,
) -> str:
    """Apply provided resolutions to a translated SRT and write a new file.

    - Matches segments by `segment_id` (numeric index from the original SRT).
    - If a `corrected_translation` is present, it replaces the segment text.
    - If only a `transcript_text` is present, it will set the segment text to that transcript.
    - To avoid overwriting, writes `<stem>_final.srt` by default unless `output_path` is given.
    """
    p = Path(translated_srt_path)
    content = p.read_text(encoding="utf-8")
    segs = parse_srt(content)

    # Build quick index by segment_id
    id_to_pos = {seg.index: i for i, seg in enumerate(segs)}

    request_to_segment = request_to_segment or {}
    for r in resolutions:
        seg_id = r.segment_id if r.segment_id is not None else request_to_segment.get(r.request_id)
        if seg_id is None:
            continue
        pos = id_to_pos.get(seg_id)
        if pos is None:
            continue
        # Accept empty string corrections; apply if any of the fields is not None
        replacement = r.corrected_translation if r.corrected_translation is not None else r.transcript_text
        if replacement is not None:
            segs[pos].text = replacement

    # Compute output path
    if output_path is None:
        p_out = p.with_name(p.stem + "_final" + p.suffix)
    else:
        p_out = Path(output_path)
    p_out.write_text(format_srt(segs), encoding="utf-8")
    return os.fspath(p_out)
