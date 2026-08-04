from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse

from history_record import HistoryRecord

TOP_N_DEFAULT = 20


@dataclass
class HistoryStatistics:
    total_visits: int
    unique_urls: int
    duplicate_visits: int
    per_browser: List[tuple] = field(default_factory=list)  
    top_sites: List[tuple] = field(default_factory=list) 


def _extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc or url
    except ValueError:
        netloc = url
    netloc = netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def compute_statistics(records: List[HistoryRecord], top_n: int = TOP_N_DEFAULT) -> HistoryStatistics:
    total_visits = len(records)

    url_counter = Counter(record.url for record in records)
    unique_urls = len(url_counter)
    duplicate_visits = total_visits - unique_urls

    browser_counter: Counter = Counter()
    domain_counter: Counter = Counter()
    for record in records:
        browser_counter[record.browser] += 1
        domain_counter[_extract_domain(record.url)] += 1

    top_sites = domain_counter.most_common(top_n)
    per_browser = browser_counter.most_common()

    return HistoryStatistics(
        total_visits=total_visits,
        unique_urls=unique_urls,
        duplicate_visits=duplicate_visits,
        per_browser=per_browser,
        top_sites=top_sites,
    )


def format_statistics(stats: HistoryStatistics) -> str:
    lines = []
    lines.append("\n" + "=" * 40)
    lines.append("History Statistics")
    lines.append("=" * 40)
    lines.append(f"Total Visits:     {stats.total_visits}")
    lines.append(f"Unique URLs:      {stats.unique_urls}")
    lines.append(f"Duplicate Visits: {stats.duplicate_visits}")

    if stats.per_browser:
        lines.append("")
        lines.append("Visits by Browser:")
        lines.append("-" * 40)
        for browser, count in stats.per_browser:
            lines.append(f"  {browser:<35} ({count} visits)")

    lines.append("")
    lines.append(f"Top {len(stats.top_sites)} Most Visited Websites:")
    lines.append("-" * 40)

    for rank, (domain, count) in enumerate(stats.top_sites, start=1):
        lines.append(f"{rank:>2}. {domain:<35} ({count} visits)")

    lines.append("=" * 40)
    return "\n".join(lines)
