import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.fixtures import make_chromium_profile, make_firefox_profile  

import reader 
from profiles import BrowserProfile  #


class TestReadAllHistory(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _chrome_profile(self, name, entries):
        profile_dir = self.tmp_path / "chrome" / name
        make_chromium_profile(profile_dir, entries)
        return BrowserProfile(
            browser_key="chrome",
            browser_name="Google Chrome",
            engine="chromium",
            name=name,
            path=profile_dir,
            history_path=profile_dir / "History",
        )

    def _firefox_profile(self, name, entries):
        profile_dir = self.tmp_path / "firefox" / name
        make_firefox_profile(profile_dir, entries)
        return BrowserProfile(
            browser_key="firefox",
            browser_name="Mozilla Firefox",
            engine="firefox",
            name=name,
            path=profile_dir,
            history_path=profile_dir / "places.sqlite",
        )

    def test_merges_across_engines_and_sorts_chronologically(self):
        chrome_profile = self._chrome_profile(
            "Default", [("https://later.example", "Later", 1, datetime(2026, 6, 1))]
        )
        firefox_profile = self._firefox_profile(
            "default-release", [("https://earlier.example", "Earlier", 1, datetime(2026, 1, 1))]
        )

        records, errors = reader.read_all_history(
            [chrome_profile, firefox_profile], show_progress=False
        )

        self.assertEqual(errors, [])
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].url, "https://earlier.example")
        self.assertEqual(records[1].url, "https://later.example")

    def test_broken_profile_collected_as_error_but_others_continue(self):
        good = self._chrome_profile(
            "Default", [("https://ok.example", "OK", 1, datetime(2026, 1, 1))]
        )
        broken = self._chrome_profile("Broken", [])
        broken.history_path.write_bytes(b"not a real database")

        records, errors = reader.read_all_history([good, broken], show_progress=False)

        self.assertEqual(len(records), 1)
        self.assertEqual(len(errors), 1)

    def test_empty_profile_list(self):
        records, errors = reader.read_all_history([], show_progress=False)
        self.assertEqual(records, [])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
