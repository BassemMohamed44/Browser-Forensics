from __future__ import annotations

import logging
import sys
import threading
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from browsers import BROWSERS, all_browser_keys  
from exporter import export_history 
from filters import filter_by_domain, search_records  
from history_record import HistoryRecord  
from profiles import BrowserProfile, detect_all_profiles, detect_installed_browsers 
from reader import read_all_history  
from stats import compute_statistics 

_lock = threading.Lock()
_state: Dict = {
    "records": [],       
    "errors": [],       
    "profiles": [],    
    "logs": [],          
    "scanned_at": None,  
}


class _CollectingLogHandler(logging.Handler):

    def __init__(self):
        super().__init__(level=logging.INFO)
        self.entries: List[dict] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.entries.append(
            {
                "time": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
                "message": record.getMessage(),
                "level": record.levelname,
                "ok": record.levelno < logging.WARNING,
            }
        )


def run_scan(browser_keys: Optional[List[str]] = None) -> Dict:

    handler = _CollectingLogHandler()
    root_logger = logging.getLogger()
    previous_level = root_logger.level
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    try:
        handler.entries.append(
            {"time": datetime.now().strftime("%H:%M:%S"), "message": "Scan started by user",
             "level": "INFO", "ok": True}
        )

        installed = detect_installed_browsers()
        if browser_keys:
            wanted = set(browser_keys)
            installed = [spec for spec in installed if spec.key in wanted]

        handler.entries.append(
            {"time": datetime.now().strftime("%H:%M:%S"),
             "message": f"Detected {len(installed)} browser(s)", "level": "INFO", "ok": True}
        )

        profiles = detect_all_profiles(browser_keys)
        for spec in installed:
            count = len([p for p in profiles if p.browser_key == spec.key])
            if count:
                handler.entries.append(
                    {"time": datetime.now().strftime("%H:%M:%S"),
                     "message": f"{spec.display_name} - {count} profile(s) found",
                     "level": "INFO", "ok": True}
                )

        records, errors = read_all_history(profiles, show_progress=False)

        handler.entries.append(
            {"time": datetime.now().strftime("%H:%M:%S"),
             "message": "Scan completed successfully", "level": "INFO", "ok": True}
        )

        with _lock:
            _state["records"] = records
            _state["errors"] = errors
            _state["profiles"] = profiles
            _state["logs"] = list(reversed(handler.entries))[:40]
            _state["scanned_at"] = datetime.now()

        return {
            "profiles_found": len(profiles),
            "records_found": len(records),
            "errors": len(errors),
        }
    finally:
        root_logger.removeHandler(handler)
        root_logger.setLevel(previous_level)


def has_scanned() -> bool:
    with _lock:
        return _state["scanned_at"] is not None


def _domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc or url
    except ValueError:
        netloc = url
    netloc = netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def _apply_filters(
    records: List[HistoryRecord],
    browser: Optional[str],
    profile: Optional[str],
    date_from: Optional[str],
    date_to: Optional[str],
    keyword: Optional[str],
    include_duplicates: bool,
    top_sites_only: bool,
) -> List[HistoryRecord]:
    filtered = records

    if browser and browser != "all":
        filtered = [r for r in filtered if r.browser == browser]

    if profile and profile != "all":
        filtered = [r for r in filtered if r.profile == profile]

    if date_from:
        try:
            start = datetime.strptime(date_from, "%Y-%m-%d")
            filtered = [r for r in filtered if r.visit_time and r.visit_time >= start]
        except ValueError:
            pass

    if date_to:
        try:
            end = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            filtered = [r for r in filtered if r.visit_time and r.visit_time < end]
        except ValueError:
            pass

    if keyword:
        filtered = search_records(filtered, keyword)

    if not include_duplicates:
        seen = set()
        deduped = []
        for r in filtered:
            if r.url in seen:
                continue
            seen.add(r.url)
            deduped.append(r)
        filtered = deduped

    if top_sites_only:
        domain_counts = Counter(_domain_of(r.url) for r in filtered)
        top_domains = {d for d, _ in domain_counts.most_common(20)}
        filtered = [r for r in filtered if _domain_of(r.url) in top_domains]

    return filtered


def _format_day_label(d) -> str:
    return f"{d.strftime('%b')} {d.day}"


def _build_activity_timeline(records: List[HistoryRecord]) -> Dict:
    by_day: Counter = Counter()
    for r in records:
        if r.visit_time:
            by_day[r.visit_time.date()] += 1

    if not by_day:
        return {"labels": [], "values": []}

    days = sorted(by_day.keys())
    labels = [_format_day_label(d) for d in days]
    values = [by_day[d] for d in days]
    return {"labels": labels, "values": values}


def _build_visits_by_day(records: List[HistoryRecord], num_days: int = 7) -> Dict:

    by_day: Counter = Counter()
    for r in records:
        if r.visit_time:
            by_day[r.visit_time.date()] += 1

    if not by_day:
        return {"labels": [], "values": []}

    days = sorted(by_day.keys())[-num_days:]
    labels = [_format_day_label(d) for d in days]
    values = [by_day[d] for d in days]
    return {"labels": labels, "values": values}


def _build_hour_heatmap(records: List[HistoryRecord]) -> List[List[int]]:
    matrix = [[0] * 24 for _ in range(7)]
    for r in records:
        if r.visit_time:
            matrix[r.visit_time.weekday()][r.visit_time.hour] += 1
    return matrix


def _build_top_sites(records: List[HistoryRecord], top_n: int = 10) -> List[Dict]:
    per_domain_visits: Counter = Counter()
    per_domain_last_seen: Dict[str, datetime] = {}
    per_domain_browsers: Dict[str, Counter] = defaultdict(Counter)

    for r in records:
        domain = _domain_of(r.url)
        per_domain_visits[domain] += 1
        per_domain_browsers[domain][r.browser] += 1
        if r.visit_time and (domain not in per_domain_last_seen or r.visit_time > per_domain_last_seen[domain]):
            per_domain_last_seen[domain] = r.visit_time

    rows = []
    for rank, (domain, count) in enumerate(per_domain_visits.most_common(top_n), start=1):
        last_seen = per_domain_last_seen.get(domain)
        top_browser = per_domain_browsers[domain].most_common(1)[0][0] if per_domain_browsers[domain] else "-"
        rows.append(
            {
                "rank": rank,
                "domain": domain,
                "visits": count,
                "last_visit": last_seen.strftime("%Y-%m-%d %H:%M") if last_seen else "Unknown",
                "browser": top_browser,
            }
        )
    return rows


def get_dashboard(
    browser: Optional[str] = None,
    profile: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    keyword: Optional[str] = None,
    include_duplicates: bool = True,
    top_sites_only: bool = False,
) -> Dict:
    with _lock:
        all_records: List[HistoryRecord] = list(_state["records"])
        errors = list(_state["errors"])
        profiles: List[BrowserProfile] = list(_state["profiles"])
        logs = list(_state["logs"])
        scanned_at = _state["scanned_at"]

    filtered = _apply_filters(
        all_records, browser, profile, date_from, date_to, keyword, include_duplicates, top_sites_only
    )

    stats = compute_statistics(filtered)
    installed = detect_installed_browsers()
    browsers_present = sorted({r.browser for r in all_records})
    profiles_present = sorted({r.profile for r in all_records})

    total_domains = len({_domain_of(r.url) for r in filtered})

    donut = []
    total = stats.total_visits or 1
    for name, count in stats.per_browser:
        donut.append({"browser": name, "count": count, "pct": round(count / total * 100, 1)})

    return {
        "scanned_at": scanned_at.strftime("%Y-%m-%d %H:%M:%S") if scanned_at else None,
        "cards": {
            "total_browsers": len(installed),
            "total_profiles": len(profiles),
            "history_records": stats.total_visits,
            "unique_domains": total_domains,
            "duplicate_visits": stats.duplicate_visits,
            "read_errors": len(errors),
        },
        "activity_timeline": _build_activity_timeline(filtered),
        "visits_by_day": _build_visits_by_day(filtered),
        "hour_heatmap": _build_hour_heatmap(filtered),
        "browsers_overview": donut,
        "top_sites": _build_top_sites(filtered),
        "recent_logs": logs,
        "filters": {
            "browsers": browsers_present,
            "profiles": profiles_present,
        },
        "summary": {
            "total_records": stats.total_visits,
            "unique_domains": total_domains,
            "duplicate_visits": stats.duplicate_visits,
            "browsers_detected": len(installed),
            "profiles_found": len(profiles),
            "errors": len(errors),
        },
        "errors": [{"profile": e.profile_label, "reason": e.reason} for e in errors],
    }


def export_current(export_format: str) -> List[Path]:
    with _lock:
        records = list(_state["records"])
    if not records:
        raise ValueError("No scan data available yet. Run a scan first.")
    return export_history(records, export_format, prefix="dashboard_export")
