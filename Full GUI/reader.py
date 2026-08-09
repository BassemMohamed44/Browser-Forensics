from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional, Tuple

import chromium
import firefox
from browsers import CHROMIUM, FIREFOX
from history_record import HistoryRecord, ProfileReadError
from log_setup import get_logger
from profiles import BrowserProfile
from progress import ProgressBar

log = get_logger(__name__)

_READERS = {
    CHROMIUM: chromium.read_profile_history,
    FIREFOX: firefox.read_profile_history,
}

DEFAULT_MAX_WORKERS = 8


def _read_one(
    profile: BrowserProfile,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> Tuple[BrowserProfile, Optional[List[HistoryRecord]], Optional[ProfileReadError]]:
    read_fn = _READERS.get(profile.engine)
    if read_fn is None:
        return profile, None, ProfileReadError(profile.label, f"Unsupported engine: {profile.engine}")

    try:
        records = read_fn(profile, start_date, end_date)
        return profile, records, None
    except ProfileReadError as exc:
        return profile, None, exc


def read_all_history(
    profiles: List[BrowserProfile],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_workers: int = DEFAULT_MAX_WORKERS,
    show_progress: bool = True,
) -> Tuple[List[HistoryRecord], List[ProfileReadError]]:
    all_records: List[HistoryRecord] = []
    errors: List[ProfileReadError] = []

    if not profiles:
        return all_records, errors

    bar = ProgressBar(total=len(profiles), label="Reading profiles") if show_progress else None
    workers = max(1, min(max_workers, len(profiles)))

    log.debug("Reading %d profile(s) with %d worker thread(s).", len(profiles), workers)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(_read_one, profile, start_date, end_date): profile
            for profile in profiles
        }

        for future in as_completed(futures):
            profile, records, error = future.result()
            if error is not None:
                log.warning("Skipped %s: %s", error.profile_label, error.reason)
                errors.append(error)
            else:
                log.info("%s -> %d visit(s) found.", profile.label, len(records))
                all_records.extend(records)

            if bar is not None:
                bar.update(1)

    if bar is not None:
        bar.finish()

    all_records.sort(key=lambda r: r.visit_time or datetime.min)

    return all_records, errors
