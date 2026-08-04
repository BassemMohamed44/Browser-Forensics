from __future__ import annotations

from typing import List
from urllib.parse import urlparse

from history_record import HistoryRecord


def _domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc or url
    except ValueError:
        netloc = url
    netloc = netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def filter_by_domain(records: List[HistoryRecord], domain: str) -> List[HistoryRecord]:

    needle = domain.strip().lower()
    if needle.startswith("www."):
        needle = needle[4:]
    if not needle:
        return records

    return [
        record
        for record in records
        if _domain_of(record.url) == needle or _domain_of(record.url).endswith("." + needle)
    ]


def search_records(records: List[HistoryRecord], query: str) -> List[HistoryRecord]:

    needle = query.strip().lower()
    if not needle:
        return records

    return [
        record
        for record in records
        if needle in record.title.lower() or needle in record.url.lower()
    ]
