# srt-reels-formatter

[![CI](https://github.com/tarikra1/srt-reels-formatter/actions/workflows/ci.yml/badge.svg)](https://github.com/tarikra1/srt-reels-formatter/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/release-v1.0.0-0EA5E9.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Zero-dependency Python CLI and library for smoothing micro-gap subtitle flicker and auditing 9:16 mobile safe-zone density in `.srt` caption timelines.**

## Quickstart

```bash
pip install -e .

# Bridge micro-gaps <= 0.42s so subtitles never blink across jump-cuts
srt-reels smooth captions.srt -o captions_clean.srt

# Audit 9:16 mobile line widths
srt-reels audit captions_clean.srt --max-chars 28
```

## License

MIT License — see [LICENSE](LICENSE).
