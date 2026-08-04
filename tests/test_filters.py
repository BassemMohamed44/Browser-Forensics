import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from filters import filter_by_domain, search_records  
from history_record import HistoryRecord   


def _rec(url, title="Some Title"):
    return HistoryRecord(
        browser="Google Chrome",
        profile="Default",
        title=title,
        url=url,
        visit_time=datetime(2026, 1, 1),
        visit_count=1,
    )


class TestFilterByDomain(unittest.TestCase):
    def test_exact_domain_match(self):
        records = [_rec("https://youtube.com/watch"), _rec("https://google.com")]
        result = filter_by_domain(records, "youtube.com")
        self.assertEqual([r.url for r in result], ["https://youtube.com/watch"])

    def test_subdomain_matches(self):
        records = [_rec("https://m.youtube.com/watch"), _rec("https://google.com")]
        result = filter_by_domain(records, "youtube.com")
        self.assertEqual(len(result), 1)

    def test_www_and_case_insensitive(self):
        records = [_rec("https://WWW.YouTube.com/watch")]
        result = filter_by_domain(records, "www.youtube.com")
        self.assertEqual(len(result), 1)

    def test_empty_domain_returns_all(self):
        records = [_rec("https://a.com"), _rec("https://b.com")]
        self.assertEqual(filter_by_domain(records, ""), records)


class TestSearchRecords(unittest.TestCase):
    def test_matches_title(self):
        records = [_rec("https://a.com", title="My Bank Login"), _rec("https://b.com", title="News")]
        result = search_records(records, "bank")
        self.assertEqual(len(result), 1)

    def test_matches_url(self):
        records = [_rec("https://secretsite.example/login"), _rec("https://other.example")]
        result = search_records(records, "secretsite")
        self.assertEqual(len(result), 1)

    def test_case_insensitive(self):
        records = [_rec("https://a.com", title="HELLO WORLD")]
        result = search_records(records, "hello")
        self.assertEqual(len(result), 1)

    def test_empty_query_returns_all(self):
        records = [_rec("https://a.com"), _rec("https://b.com")]
        self.assertEqual(search_records(records, ""), records)


if __name__ == "__main__":
    unittest.main()
