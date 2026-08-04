import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (
    chrome_time_to_datetime,
    datetime_to_chrome_time,
    datetime_to_firefox_time,
    firefox_time_to_datetime,
    format_datetime,
    parse_user_date,
    sanitize_filename,
)


class TestTimestampConversions(unittest.TestCase):
    def test_chrome_time_roundtrip(self):
        dt = datetime(2026, 7, 1, 12, 30, 45)
        chrome_ts = datetime_to_chrome_time(dt)
        self.assertEqual(chrome_time_to_datetime(chrome_ts), dt)

    def test_chrome_time_zero_is_none(self):
        self.assertIsNone(chrome_time_to_datetime(0))

    def test_firefox_time_roundtrip(self):
        dt = datetime(2026, 1, 15, 8, 0, 0)
        ff_ts = datetime_to_firefox_time(dt)
        self.assertEqual(firefox_time_to_datetime(ff_ts), dt)

    def test_firefox_time_zero_is_none(self):
        self.assertIsNone(firefox_time_to_datetime(0))

    def test_chrome_and_firefox_epochs_differ(self):
        dt = datetime(2026, 1, 1)
        self.assertNotEqual(datetime_to_chrome_time(dt), datetime_to_firefox_time(dt))


class TestFormatting(unittest.TestCase):
    def test_format_datetime_none(self):
        self.assertEqual(format_datetime(None), "Unknown")

    def test_format_datetime_value(self):
        dt = datetime(2026, 3, 4, 5, 6, 7)
        self.assertEqual(format_datetime(dt), "2026-03-04 05:06:07")

    def test_parse_user_date_valid(self):
        self.assertEqual(parse_user_date("2026-06-01"), datetime(2026, 6, 1))

    def test_parse_user_date_invalid(self):
        with self.assertRaises(ValueError):
            parse_user_date("06/01/2026")

    def test_sanitize_filename_strips_invalid_chars(self):
        self.assertEqual(sanitize_filename('a<b>c:d"e/f\\g|h?i*j'), "a_b_c_d_e_f_g_h_i_j")

    def test_sanitize_filename_empty_falls_back(self):
        self.assertEqual(sanitize_filename("   "), "unnamed")


if __name__ == "__main__":
    unittest.main()
