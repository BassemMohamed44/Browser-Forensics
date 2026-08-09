from __future__ import annotations

import argparse
import random
import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

from exporter import export_history
from profiles import BrowserProfile
from reader import read_all_history
from stats import compute_statistics
from utils import datetime_to_chrome_time

SAMPLE_DOMAINS = [
    "github.com", "stackoverflow.com", "youtube.com", "wikipedia.org",
    "reddit.com", "news.ycombinator.com", "amazon.com", "python.org",
]


def _build_synthetic_profile(profile_dir: Path, row_count: int, seed: int) -> None:
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / "Preferences").write_text("{}")

    rng = random.Random(seed)
    history_path = profile_dir / "History"
    conn = sqlite3.connect(history_path)
    conn.execute("CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INTEGER)")
    conn.execute("CREATE TABLE visits (id INTEGER PRIMARY KEY, url INTEGER, visit_time INTEGER)")

    base_time = datetime(2026, 1, 1)
    rows_urls = []
    rows_visits = []
    for i in range(1, row_count + 1):
        domain = rng.choice(SAMPLE_DOMAINS)
        url = f"https://{domain}/page-{i % 5000}"
        title = f"Page {i % 5000} on {domain}"
        visit_time = base_time + timedelta(seconds=i * 5)
        rows_urls.append((i, url, title, rng.randint(1, 20)))
        rows_visits.append((i, i, datetime_to_chrome_time(visit_time)))

    conn.executemany("INSERT INTO urls VALUES (?, ?, ?, ?)", rows_urls)
    conn.executemany("INSERT INTO visits VALUES (?, ?, ?)", rows_visits)
    conn.commit()
    conn.close()


def _timed(label: str, fn):
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    print(f"  {label:<30} {elapsed:8.3f}s")
    return result, elapsed


def run_benchmark(num_profiles: int, rows_per_profile: int) -> None:
    total_rows = num_profiles * rows_per_profile
    print("=" * 60)
    print("Browser History Exporter - Benchmark")
    print("=" * 60)
    print(f"Profiles: {num_profiles}   Rows/profile: {rows_per_profile:,}   Total rows: {total_rows:,}\n")

    tmp_dir = Path(tempfile.mkdtemp(prefix="bhe_benchmark_"))
    try:
        profiles = []
        print("Generating synthetic data...")

        def _generate():
            for i in range(num_profiles):
                profile_dir = tmp_dir / f"Profile {i}"
                _build_synthetic_profile(profile_dir, rows_per_profile, seed=i)
                profiles.append(
                    BrowserProfile(
                        browser_key="chrome",
                        browser_name="Google Chrome",
                        engine="chromium",
                        name=f"Profile {i}",
                        path=profile_dir,
                        history_path=profile_dir / "History",
                    )
                )

        _timed("Generate synthetic DB(s)", _generate)

        (records, errors), read_time = _timed(
            "Read all profiles", lambda: read_all_history(profiles, show_progress=False)
        )
        if errors:
            print(f"  WARNING: {len(errors)} profile(s) failed to read.")

        stats, _ = _timed("Compute statistics", lambda: compute_statistics(records))

        import exporter as exporter_module
        exporter_module.OUTPUT_DIR = tmp_dir / "output"
        _, export_time = _timed("Export to JSON+TXT+CSV", lambda: export_history(records, "all"))

        print()
        print(f"Total records read: {len(records):,}")
        print(f"Throughput (read):  {len(records) / read_time:,.0f} records/sec" if read_time > 0 else "")
        print(f"Throughput (export): {len(records) / export_time:,.0f} records/sec" if export_time > 0 else "")
        print()
        print("Note: real browser History files add indexes and extra tables,")
        print("so real-world throughput will differ from this synthetic benchmark.")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Browser History Exporter with synthetic data.")
    parser.add_argument("--profiles", type=int, default=1, help="Number of synthetic profiles to generate.")
    parser.add_argument("--rows", type=int, default=200_000, help="Number of history rows per profile.")
    args = parser.parse_args()

    run_benchmark(num_profiles=args.profiles, rows_per_profile=args.rows)


if __name__ == "__main__":
    sys.exit(main())
