"""CLI for srt-reels-formatter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import audit_safe_zone, parse_srt, serialize_srt, smooth_micro_gaps


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="srt-reels", description="Format and validate 9:16 Reels SRT captions.")
    sub = parser.add_subparsers(dest="command", required=True)

    sm = sub.add_parser("smooth", help="Close micro-gaps between consecutive SRT cues.")
    sm.add_argument("input", help="Input .srt path")
    sm.add_argument("-o", "--output", default="", help="Output .srt path (prints to stdout if omitted)")
    sm.add_argument("--max-gap", type=float, default=0.42, help="Max gap in seconds to bridge (default: 0.42)")

    au = sub.add_parser("audit", help="Audit 9:16 mobile safe-zone line width and count.")
    au.add_argument("input", help="Input .srt path")
    au.add_argument("--max-chars", type=int, default=28)

    args = parser.parse_args(argv)
    raw = Path(args.input).read_text(encoding="utf-8")
    cues = parse_srt(raw)

    if args.command == "smooth":
        smoothed = smooth_micro_gaps(cues, max_gap_sec=args.max_gap)
        rendered = serialize_srt(smoothed)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8", newline="\n")
        else:
            print(rendered, end="")
        return 0

    issues = audit_safe_zone(cues, max_chars_per_line=args.max_chars)
    print(json.dumps({"ok": len(issues) == 0, "cue_count": len(cues), "issues": issues}, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
