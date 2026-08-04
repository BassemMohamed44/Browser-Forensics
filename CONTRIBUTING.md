# Contributing

Thanks for considering a contribution to Browser Forensics.

## Setup

```bash
git clone <your-fork-url>
cd BrowserHistoryExporter
pip install -e ".[dev]"
```

## Running the tests

```bash
python -m unittest discover -s tests -v
# or
pytest
```

Please add or update tests for any behavior change. Readers for new
engines should use the synthetic-database fixtures in `tests/fixtures.py`
rather than touching real browser data.

## Adding a new browser

- **Chromium-based** (shares the `urls`/`visits` schema): add one entry to
  `BROWSERS` in `browsers.py` with `engine=CHROMIUM` and its per-platform
  `User Data` path. No other file needs to change.
- **Firefox-based**: add one entry with `engine=FIREFOX` and its
  per-platform `Profiles` path.
- **A different engine entirely**: add a new reader module (mirroring
  `chromium.py` / `firefox.py`), register it in `reader.py`'s `_READERS`
  dict, and add the browser's engine + paths to `browsers.py`.

## Code style

- Standard library only at runtime — no new third-party runtime
  dependencies without discussion first.
- Keep modules single-purpose (see the existing split between profile
  detection, per-engine reading, exporting, and stats).
- Log through `log_setup.get_logger(__name__)` rather than `print()` for
  anything that isn't a direct user prompt.

## Reporting issues

Please include your OS, Python version, and which browser/profile
triggered the issue (never attach your actual `History`/`places.sqlite`
file or exported output — those contain your personal browsing data).
