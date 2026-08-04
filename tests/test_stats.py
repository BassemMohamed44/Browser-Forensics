import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from history_record import HistoryRecord  
from stats import compute_statistics 


def _rec(url, browser="Google Chrome", profile="Default"):
    return HistoryRecord(
        browser=browser,
        profile=profile,
        title="Title",
        url=url,
        visit_time=datetime(2026, 1, 1),
        visit_count=1,
    )


class TestStats(unittest.TestCase):
    def test_counts_and_duplicates(self):
        records = [
            _rec("https://a.com"),
            _rec("https://a.com"),
            _rec("https://b.com"),
        ]
        stats = compute_statistics(records)
        self.assertEqual(stats.total_visits, 3)
        self.assertEqual(stats.unique_urls, 2)
        self.assertEqual(stats.duplicate_visits, 1)

    def test_domain_grouping_strips_www_and_case(self):
        records = [
            _rec("https://WWW.Example.com/page1"),
            _rec("https://example.com/page2"),
        ]
        stats = compute_statistics(records)
        self.assertEqual(stats.top_sites, [("example.com", 2)])

    def test_per_browser_breakdown(self):
        records = [
            _rec("https://a.com", browser="Google Chrome"),
            _rec("https://b.com", browser="Mozilla Firefox"),
            _rec("https://c.com", browser="Google Chrome"),
        ]
        stats = compute_statistics(records)
        self.assertIn(("Google Chrome", 2), stats.per_browser)
        self.assertIn(("Mozilla Firefox", 1), stats.per_browser)

    def test_empty_records(self):
        stats = compute_statistics([])
        self.assertEqual(stats.total_visits, 0)
        self.assertEqual(stats.unique_urls, 0)
        self.assertEqual(stats.duplicate_visits, 0)
        self.assertEqual(stats.top_sites, [])


if __name__ == "__main__":
    unittest.main()
