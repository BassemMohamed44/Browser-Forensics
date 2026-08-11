<div align="center">
  <img width="260" height="260" src="assets/Browser Forensics.png" alt="Browser-Forensics-icon"/>
  <h1 align="center">Browser Forensics</h1>
  <p align="center">A cross-platform browser history analysis and digital forensics utility with both <strong>CLI</strong> and <strong>GUI</strong> interfaces. It extracts browsing history from every profile of every major browser installed on your machine — on <strong>Windows, macOS, or Linux</strong> — and provides filtering, search, statistics, and JSON / TXT / CSV export capabilities.</p>
</div>

<div align="center">

<div align="center">
  <img src="https://img.shields.io/static/v1?label=Python&message=3.14.5&color=4C0099" alt="python"/>
  <img src="https://img.shields.io/static/v1?label=macOS&message=Tahoe26.6&color=4C0099" alt="macOS"/>
  <img src="https://img.shields.io/static/v1?label=Linux&message=7.1.6&color=4C0099" alt="linux"/>
  <br>
  <img src="https://img.shields.io/static/v1?label=Browser&message=Engine&color=4C0099" alt="browser"/>
  <img src="https://img.shields.io/static/v1?label=Windows11&message=26H1&color=4C0099" alt="win"/>
  <br>
   <img src="https://img.shields.io/static/v1?label=License&message=MIT&color=4C0099" alt="license"/>
</div>
<br>

<div align="center">
  
  [![Instagram](https://img.shields.io/badge/Instagram-%23E4405F.svg?style=for-the-badge&logo=Instagram&logoColor=white)](https://instagram.com/@bassemmohamed_0)
  [![Reddit](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://reddit.com/user/00xBassem)
  [![X](https://img.shields.io/badge/X-black.svg?style=for-the-badge&logo=X&logoColor=white)](https://x.com/@Basem2Mohamed)
  
</div>

<p align="center">Made possible by <a href="https://bassemmohamed.pages.dev/"><strong>BassemMohamed</strong></a></p>

# Interfaces

Browser Forensics is available through two interfaces:

- **CLI** — a lightweight command-line interface for terminal-based workflows, scripting, automation, and advanced users.
- **GUI** — a graphical interface for interactive browser history analysis, searching, filtering, statistics, and exporting.

Both interfaces are part of the same Browser Forensics project.

## Screenshots

### CLI
<img src="assets/Screenshot 1.png" alt="Browser Forensics CLI" width="800">

### GUI
<img src="assets/Screenshot-GUI 1.png" alt="Browser Forensics GUI" width="800">
<br>
<img src="assets/Screenshot-GUI 2.jpg" alt="Browser Forensics GUI" width="800">


## Supported Browsers

| Browser              | Engine    | Windows | macOS | Linux |
|-----------------------|-----------|:-------:|:-----:|:-----:|
| Google Chrome          | Chromium  | ✅ | ✅ | ✅ |
| Google Chrome Beta     | Chromium  | ✅ | ✅ | ✅ |
| Microsoft Edge         | Chromium  | ✅ | ✅ | ✅ |
| Brave                  | Chromium  | ✅ | ✅ | ✅ |
| Opera                  | Chromium  | ✅ | ✅ | ✅ |
| Vivaldi                | Chromium  | ✅ | ✅ | ✅ |
| Chromium               | Chromium  | ✅ | ✅ | ✅ |
| Mozilla Firefox        | Firefox   | ✅ | ✅ | ✅ |
| Firefox ESR            | Firefox   | ✅ | ✅ | ✅ |

Every browser is auto-detected — only the ones actually installed on the
current machine are scanned. Adding another Chromium- or Firefox-based
browser later is a one-entry addition to `browsers.py`; no other file needs
to change.

## Features

- **Cross-platform**: detects each browser's data directory correctly on
  Windows (`%LOCALAPPDATA%` / `%APPDATA%`), macOS (`~/Library/Application
  Support`), and Linux (`~/.config`, respecting `$XDG_CONFIG_HOME`).
- **Export ALL history** — every visit, every profile, every browser, no
  record limit.
- **Export between two dates** — e.g. `2026-06-01` to `2026-07-10`.
- **Choose specific browsers** — export from only the browsers you pick.
- **Automatic profile detection** — finds every profile
  (`Default`, `Profile 1`, `Guest Profile`, Firefox's
  `xxxxxxxx.default-release`, etc.) automatically, nothing hardcoded.
- **JSON and TXT export formats**, written to `output/`.
- **Duplicate detection & statistics**: total visits, unique URLs,
  duplicate visits, a per-browser breakdown, and the Top 20 most-visited
  websites (grouped by domain).
- **Robust error handling**: missing browser installs, missing/locked/
  corrupted databases, and permission errors are all caught per-profile —
  the tool always continues with the remaining profiles instead of
  crashing.
- **WAL-aware reads**: copies each database's `-wal`/`-shm` sidecar files
  too, so very recent visits (not yet checkpointed into the main file) are
  still picked up.

## Project Structure

```
Browser-Forensics/
├── main.py             # CLI entry point / menu
├── browsers.py          # Registry: browser -> engine + per-platform data path
├── profiles.py          # Detects every profile of every installed browser
├── chromium.py           # Reads history from Chromium-based browsers
├── firefox.py            # Reads history from Firefox-based browsers
├── reader.py             # Dispatches each profile to the right engine reader
├── history_record.py     # Shared, normalized HistoryRecord / error types
├── exporter.py           # Writes JSON / TXT files to output/
├── stats.py              # Duplicate detection & top-sites/per-browser stats
├── utils.py              # Shared helpers (timestamps, safe file copy, etc.)
└── output/                # Generated export files land here
```

## Requirements

### CLI

- Python 3.9+
- Standard library only at runtime (`sqlite3`, `os`, `pathlib`, `json`,
  `csv`, `shutil`, `tempfile`, `datetime`, `platform`, `logging`,
  `concurrent.futures`, `collections`) — no third-party dependencies.
  `pytest` is only needed to run the test suite (see below).
- At least one supported browser installed on the machine.

### GUI

The repository also includes a graphical interface. See the GUI entry point
and project files for the GUI-specific runtime requirements.

> **Tip:** For the most complete and consistent snapshot, close your
> browsers before running an export. The tool copies each database (and its
> `-wal`/`-shm` sidecars) before reading it, so it will generally still
> work while browsers are open, but a running browser can occasionally hold
> a lock long enough to cause a skipped profile.

## Usage

### CLI

Run the command-line interface:

```bash
python main.py
```

You'll see a menu:

```
====================================
Browser Forensics
====================================

1. Export ALL History (all browsers)
2. Export Between Dates (all browsers)
3. Choose Browsers to Export
4. Exit
```

- **Option 1** exports every visit from every profile of every installed,
  supported browser.
- **Option 2** prompts for a `From` and `To` date (format `YYYY-MM-DD`) and
  exports only visits inside that (inclusive) range, across all browsers.
- **Option 3** lists the browsers found installed on this machine and lets
  you pick a subset (e.g. only Chrome and Firefox) before exporting all of
  their history.
- After reading, you can optionally **filter by domain** (e.g.
  `youtube.com`, which also matches `m.youtube.com`) and/or **search**
  title/URL for a keyword — press Enter to skip either.
- Every export path then asks whether you want JSON, TXT, CSV, or all
  three, writes the files into `output/`, and prints a statistics summary
  (total visits, unique URLs, duplicates, per-browser breakdown, and the
  Top 20 most visited sites).
- A progress bar shows read progress across profiles so the tool never
  looks like it has hung on a large history.
- Every run also writes a detailed log file to `output/logs/run_<timestamp>.log`
  (full detail, for debugging) in addition to the console output you see
  (a friendlier summary).

### GUI

Browser Forensics also includes a graphical user interface for users who prefer
interactive analysis instead of a terminal workflow.

The GUI provides a visual way to work with the project's browser-history
analysis capabilities, including browsing the collected records, searching,
filtering, viewing statistics, and exporting results.

## Each Exported Record Contains

| Field        | Description                                     |
|--------------|--------------------------------------------------|
| Browser      | Which browser the visit came from (e.g. "Google Chrome") |
| Profile      | Which profile within that browser                |
| Title        | Page title at time of visit                       |
| URL          | Full URL                                          |
| Visit Time   | Local timestamp of the visit                      |
| Visit Count  | The browser's own running visit count for that URL|

## How Browser Data Is Located

- **Chromium family** (Chrome, Edge, Brave, Opera, Vivaldi, Chromium):
  scans that browser's `User Data` directory for profile folders (any
  folder containing a `History` or `Preferences` file), then reads
  `History` — a SQLite database joining its `urls` and `visits` tables.
- **Firefox family** (Firefox, Firefox ESR): scans the `Profiles` directory
  for folders containing a `places.sqlite` file, then reads it — a SQLite
  database joining `moz_places` and `moz_historyvisits`.
- Timestamps are converted from each engine's native epoch (Chromium:
  microseconds since 1601-01-01 UTC; Firefox: microseconds since
  1970-01-01 UTC) into standard local datetimes.

## Extending to Other Browsers

The project is intentionally modular:

1. **Another Chromium-based browser** (e.g. Arc, Yandex): add one entry to
   `BROWSERS` in `browsers.py` with its per-platform `User Data` path and
   `engine=CHROMIUM`. `profiles.py` and `chromium.py` work unmodified.
2. **Another Firefox-based browser** (e.g. LibreWolf, Tor Browser): add one
   entry with `engine=FIREFOX` and its per-platform `Profiles` path.
   `profiles.py` and `firefox.py` work unmodified.
3. **A genuinely different engine** (e.g. Safari's WebKit history format):
   add a new reader module (mirroring `chromium.py`/`firefox.py`), register
   it in `reader.py`'s `_READERS` dict, and add the browser's engine +
   paths to `browsers.py`.

## Performance: Concurrency & Benchmarking

- Profiles are read **concurrently** with a thread pool (`reader.py`).
  Reading a profile is I/O-bound (copy the DB, run one local SQLite query),
  so threads give a real speedup with many browsers/profiles without the
  complexity of multiprocessing — each profile gets its own SQLite
  connection, so there's no shared-connection thread-safety concern.
- `benchmark.py` generates synthetic history databases of any size and
  times the read → stats → export pipeline, so you can see how the tool
  scales before pointing it at real (much larger) browser history:

  ```bash
  python benchmark.py                              # 1 profile, 200,000 rows
  python benchmark.py --rows 1000000                # one very large profile
  python benchmark.py --profiles 8 --rows 100000     # 8 profiles, read in parallel
  ```

  On a typical machine, reading and exporting 200,000 synthetic rows
  across 4 profiles took roughly 1-2 seconds to read and 3 seconds to
  export in all three formats (JSON+TXT+CSV) — real browser databases add
  indexes and extra tables, so treat this as a relative, not absolute,
  number.

## Logging

- Console output stays clean and readable (via the standard `logging`
  module, replacing the old `print()`-only approach).
- Every run additionally writes a full-detail log file to
  `output/logs/run_<YYYYmmdd_HHMMSS>.log`, so a failed or unexpected export
  can be diagnosed after the fact without having to reproduce it live.

## Testing

The project ships with a `unittest`-based test suite (also runnable with
`pytest`) covering timestamp conversions, both browser-engine readers
(with synthetic SQLite fixtures — no real browser data is touched),
statistics, filters/search, and the CSV/JSON/TXT exporter:

```bash
python -m unittest discover -s tests -v
# or, if you installed the [dev] extra:
pytest
```

## Packaging

The project includes a `pyproject.toml` so it can be installed as a
regular Python package (and exposes a `browser-forensics` console
command):

```bash
pip install .
browser-forensics
# or, for development with the test dependencies:
pip install -e ".[dev]"
```

## Notes on Data Safety

- The tool never modifies your original browser history databases — it
  always works from a temporary copy (see `utils.safe_copy_database`),
  which is deleted after each profile is processed.
- All exported data stays local; nothing is uploaded anywhere.
