import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.fixtures import make_firefox_profile  

import firefox 
from history_record import ProfileReadError  
from profiles import BrowserProfile  


class TestFirefoxReader(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _profile(self, name="abc.default-release"):
        profile_dir = self.tmp_path / name
        return BrowserProfile(
            browser_key="firefox",
            browser_name="Mozilla Firefox",
            engine="firefox",
            name=name,
            path=profile_dir,
            history_path=profile_dir / "places.sqlite",
        )

    def test_reads_all_records(self):
        profile = self._profile()
        make_firefox_profile(
            profile.path,
            [("https://mozilla.org", "Mozilla", 2, datetime(2026, 7, 2, 11, 0))],
        )

        records = firefox.read_profile_history(profile)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].url, "https://mozilla.org")
        self.assertEqual(records[0].browser, "Mozilla Firefox")
        self.assertEqual(records[0].visit_count, 2)

    def test_date_range_filtering(self):
        profile = self._profile()
        make_firefox_profile(
            profile.path,
            [
                ("https://a.example", "A", 1, datetime(2026, 1, 1)),
                ("https://b.example", "B", 1, datetime(2026, 6, 1)),
            ],
        )

        records = firefox.read_profile_history(
            profile, start_date=datetime(2026, 5, 1), end_date=datetime(2026, 7, 1)
        )
        self.assertEqual([r.url for r in records], ["https://b.example"])

    def test_missing_database_raises_profile_read_error(self):
        profile = self._profile("missing")
        with self.assertRaises(ProfileReadError):
            firefox.read_profile_history(profile)


if __name__ == "__main__":
    unittest.main()
