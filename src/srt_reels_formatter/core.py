"""SRT parser, micro-gap flicker smoother, and 9:16 safe-zone caption validator."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

TS_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


@dataclass
class CaptionCue:
    index: int
    start_sec: float
    end_sec: float
    text: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def parse_timestamp(ts: str) -> float:
    m = TS_RE.fullmatch(ts.strip())
    if not m:
        raise ValueError(f"Invalid SRT timestamp: {ts!r}")
    hh, mm, ss, ms = (int(g) for g in m.groups())
    return hh * 3600 + mm * 60 + ss + ms / 1000.0


def format_timestamp(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hh, rem = divmod(total_ms, 3_600_000)
    mm, rem = divmod(rem, 60_000)
    ss, ms = divmod(rem, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def parse_srt(raw: str) -> list[CaptionCue]:
    blocks = re.split(r"\r?\n\s*\r?\n", raw.strip())
    cues: list[CaptionCue] = []
    for block in blocks:
        if not block.strip():
            continue
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        time_line_idx = 1 if "-->" in lines[1] else 0
        start_s, end_s = [p.strip() for p in lines[time_line_idx].split("-->", 1)]
        text = "\n".join(lines[time_line_idx + 1 :])
        cues.append(
            CaptionCue(
                index=len(cues) + 1,
                start_sec=parse_timestamp(start_s),
                end_sec=parse_timestamp(end_s),
                text=text,
            )
        )
    return cues


def smooth_micro_gaps(cues: list[CaptionCue], max_gap_sec: float = 0.42) -> list[CaptionCue]:
    """Extend cue end times across tiny pauses (`<= max_gap_sec`) so subtitles never flicker."""
    out = [CaptionCue(i + 1, c.start_sec, c.end_sec, c.text) for i, c in enumerate(cues)]
    for i in range(len(out) - 1):
        gap = out[i + 1].start_sec - out[i].end_sec
        if 0.0 < gap <= max_gap_sec:
            out[i].end_sec = out[i + 1].start_sec
    return out


def audit_safe_zone(cues: list[CaptionCue], max_chars_per_line: int = 28, max_lines: int = 2) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    for c in cues:
        lines = c.text.splitlines()
        if len(lines) > max_lines:
            issues.append({"index": c.index, "rule": "TOO_MANY_LINES", "lines": len(lines), "text": c.text})
        for ln in lines:
            if len(ln) > max_chars_per_line:
                issues.append({"index": c.index, "rule": "LINE_TOO_WIDE", "length": len(ln), "text": ln})
    return issues


def serialize_srt(cues: list[CaptionCue]) -> str:
    chunks = []
    for idx, c in enumerate(cues, start=1):
        chunks.append(f"{idx}\n{format_timestamp(c.start_sec)} --> {format_timestamp(c.end_sec)}\n{c.text}")
    return "\n\n".join(chunks) + ("\n" if chunks else "")
