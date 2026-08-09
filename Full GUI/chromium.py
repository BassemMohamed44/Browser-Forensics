from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from history_record import HistoryRecord, ProfileReadError
from profiles import BrowserProfile
from utils import chrome_time_to_datetime, cleanup_temp_file, safe_copy_database

_HISTORY_QUERY = """
    SELECT
        urls.title,
        urls.url,
        urls.visit_count,
        visits.visit_time
    FROM urls
    JOIN visits ON urls.id = visits.url
    ORDER BY visits.visit_time ASC
"""


def _fetch_rows_from_database(db_path: Path) -> List[tuple]:
    uri = f"file:{db_path.as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=5)
    try:
        cursor = connection.cursor()
        cursor.execute(_HISTORY_QUERY)
        return cursor.fetchall()
    finally:
        connection.close()


def read_profile_history(
    profile: BrowserProfile,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[HistoryRecord]:
    if not profile.history_path.exists():
        raise ProfileReadError(profile.label, "History database not found (skipped).")

    temp_copy: Optional[Path] = None
    try:
        try:
            temp_copy = safe_copy_database(profile.history_path)
        except PermissionError as exc:
            raise ProfileReadError(
                profile.label, f"Permission denied while accessing database: {exc}"
            ) from exc
        except OSError as exc:
            raise ProfileReadError(
                profile.label, f"Could not copy database (it may be locked): {exc}"
            ) from exc

        try:
            rows = _fetch_rows_from_database(temp_copy)
        except sqlite3.DatabaseError as exc:
            raise ProfileReadError(
                profile.label, f"Database appears corrupted or unreadable: {exc}"
            ) from exc
        except sqlite3.OperationalError as exc:
            raise ProfileReadError(
                profile.label, f"Database is locked or inaccessible: {exc}"
            ) from exc

        records: List[HistoryRecord] = []
        for title, url, visit_count, chrome_time in rows:
            visit_time = chrome_time_to_datetime(chrome_time)

            if start_date and visit_time and visit_time < start_date:
                continue
            if end_date and visit_time and visit_time > end_date:
                continue
            if (start_date or end_date) and visit_time is None:
                continue

            records.append(
                HistoryRecord(
                    browser=profile.browser_name,
                    profile=profile.name,
                    title=title or "(No Title)",
                    url=url,
                    visit_time=visit_time,
                    visit_count=visit_count or 0,
                )
            )

        return records

    finally:
        if temp_copy is not None:
            cleanup_temp_file(temp_copy)
