from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import datetime_to_chrome_time, datetime_to_firefox_time  


def make_chromium_profile(
    profile_dir: Path,
    entries: List[Tuple[str, str, int, datetime]],
) -> Path:
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / "Preferences").write_text("{}")

    history_path = profile_dir / "History"
    conn = sqlite3.connect(history_path)
    conn.execute(
        "CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INTEGER)"
    )
    conn.execute(
        "CREATE TABLE visits (id INTEGER PRIMARY KEY, url INTEGER, visit_time INTEGER)"
    )

    for i, (url, title, visit_count, visit_time) in enumerate(entries, start=1):
        conn.execute("INSERT INTO urls VALUES (?, ?, ?, ?)", (i, url, title, visit_count))
        conn.execute(
            "INSERT INTO visits VALUES (?, ?, ?)",
            (i, i, datetime_to_chrome_time(visit_time)),
        )

    conn.commit()
    conn.close()
    return history_path


def make_firefox_profile(
    profile_dir: Path,
    entries: List[Tuple[str, str, int, datetime]],
) -> Path:

    profile_dir.mkdir(parents=True, exist_ok=True)

    history_path = profile_dir / "places.sqlite"
    conn = sqlite3.connect(history_path)
    conn.execute(
        "CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INTEGER)"
    )
    conn.execute(
        "CREATE TABLE moz_historyvisits (id INTEGER PRIMARY KEY, place_id INTEGER, visit_date INTEGER)"
    )

    for i, (url, title, visit_count, visit_time) in enumerate(entries, start=1):
        conn.execute("INSERT INTO moz_places VALUES (?, ?, ?, ?)", (i, url, title, visit_count))
        conn.execute(
            "INSERT INTO moz_historyvisits VALUES (?, ?, ?)",
            (i, i, datetime_to_firefox_time(visit_time)),
        )

    conn.commit()
    conn.close()
    return history_path
