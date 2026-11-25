import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import unittest

from srt_reels_formatter.core import audit_safe_zone, parse_srt, serialize_srt, smooth_micro_gaps

SAMPLE_SRT = """1
00:00:00,100 --> 00:00:01,200
First short hook

2
00:00:01,450 --> 00:00:02,800
Second punchy line
"""


class TestSrtReelsFormatter(unittest.TestCase):
    def test_smooth_closes_micro_gap(self) -> None:
        cues = parse_srt(SAMPLE_SRT)
        self.assertEqual(len(cues), 2)
        smoothed = smooth_micro_gaps(cues, max_gap_sec=0.42)
        self.assertAlmostEqual(smoothed[0].end_sec, 1.45, places=3)
        roundtrip = parse_srt(serialize_srt(smoothed))
        self.assertEqual(roundtrip[0].text, "First short hook")

    def test_audit_flags_wide_lines(self) -> None:
        cues = parse_srt("1\n00:00:00,000 --> 00:00:02,000\nThis single subtitle line is way too wide for vertical mobile reels\n")
        issues = audit_safe_zone(cues, max_chars_per_line=28)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["rule"], "LINE_TOO_WIDE")


if __name__ == "__main__":
    unittest.main()
