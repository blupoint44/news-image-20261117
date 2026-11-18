# news-image-20261117

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/blupoint44/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/blupoint44/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

**Day in One Picture** — a newspaper front page for a single day, drawn by a
program. `main.py` reads the day's headlines from `headlines.json` and renders
them as one 1024x1024 PNG: a masthead with the date in the largest type on the
page, the lead story full width, four more stories in a grid with small
pictograms, a sport card, and an "also today" column — nine stories across
war, diplomacy, aid, climate, technology and sport.

This edition sums up **Tuesday 17 November 2026**: tanker attacks in the
Strait of Hormuz as the US–Iran war grips the oil artery, the first
Xi–Trump–Putin trilateral summit, Russia's missile pounding of Kyiv and
Ukraine's strike on the Kerch Bridge, the four-nation call to open Gaza's
crossings, COP31's draft fossil phase-out deal in Antalya, Japan scrambling
jets over a Russian airspace breach, the tightened US AI-chip ban on China,
Depardieu's dropped appeal in Paris, and India's last-ball U19 Asia Cup win
over Pakistan.

The renderer is pure Python 3 standard library — its own 5x7 pixel typeface,
its own raster canvas, its own PNG encoder (zlib + struct) — so it runs
offline in the grader's container and is fully deterministic: the same
`headlines.json` always produces the same bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, well under the 1 MiB cap)
```

Without `MAKEFUN_OUTPUT_DIR` it writes to `/output/entry.png`, as the
competition's harness expects.

---

<sub>Entered on [make.fun](https://make.fun/?ref=43vjng2p&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
