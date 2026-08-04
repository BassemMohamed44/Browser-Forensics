import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.fixtures import make_chromium_profile   

import chromium   
from history_record import ProfileReadError  
from profiles import BrowserProfile  


class TestChromiumReader(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _profile(self, name="Default"):
        profile_dir = self.tmp_path / name
        return BrowserProfile(
            browser_key="chrome",
            browser_name="Google Chrome",
            engine="chromium",
            name=name,
            path=profile_dir,
            history_path=profile_dir / "History",
        )

    def test_reads_all_records(self):
        profile = self._profile()
        make_chromium_profile(
            profile.path,
            [
                ("https://example.com", "Example", 3, datetime(2026, 7, 1, 10, 0)),
                ("https://python.org", "Python", 1, datetime(2026, 7, 2, 9, 0)),
            ],
        )

        records = chromium.read_profile_history(profile)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].url, "https://example.com")
        self.assertEqual(records[0].browser, "Google Chrome")
        self.assertEqual(records[0].profile, "Default")
        self.assertEqual(records[0].visit_count, 3)

    def test_missing_title_becomes_placeholder(self):
        profile = self._profile()
        make_chromium_profile(profile.path, [("https://no-title.example", "", 0, datetime(2026, 1, 1))])

        records = chromium.read_profile_history(profile)
        self.assertEqual(records[0].title, "(No Title)")

    def test_date_range_filtering(self):
        profile = self._profile()
        make_chromium_profile(
            profile.path,
            [
                ("https://a.example", "A", 1, datetime(2026, 1, 1)),
                ("https://b.example", "B", 1, datetime(2026, 6, 1)),
                ("https://c.example", "C", 1, datetime(2026, 12, 1)),
            ],
        )

        records = chromium.read_profile_history(
            profile, start_date=datetime(2026, 3, 1), end_date=datetime(2026, 9, 1)
        )
        self.assertEqual([r.url for r in records], ["https://b.example"])

    def test_missing_database_raises_profile_read_error(self):
        profile = self._profile("NoSuchProfile")
        with self.assertRaises(ProfileReadError):
            chromium.read_profile_history(profile)

    def test_corrupted_database_raises_profile_read_error(self):
        profile = self._profile("Corrupt")
        profile.path.mkdir(parents=True)
        profile.history_path.write_bytes(b"not a real sqlite file")

        with self.assertRaises(ProfileReadError):
            chromium.read_profile_history(profile)


if __name__ == "__main__":
    unittest.main()
