# Changelog

All notable changes to `srt-reels-formatter` are documented in this file.

## [1.0.0] - 2026-11-25

### Added
- Strict SRT parser and serializer preserving `1 line = 1 caption` cue ordering.
- Micro-gap flicker smoother (`smooth_micro_gaps`) closing tiny inter-cue gaps (`<= 0.42s`) so mobile captions never blink off across jump-cuts.
- 9:16 safe-zone density auditor flagging cues that exceed single-line mobile character budgets.
- CLI (`srt-reels`) and multi-version GitHub Actions CI matrix.
