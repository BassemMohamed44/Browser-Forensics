import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import exporter   
from history_record import HistoryRecord  


def _rec():
    return HistoryRecord(
        browser="Google Chrome",
        profile="Default",
        title="Example",
        url="https://example.com",
        visit_time=datetime(2026, 7, 1, 10, 0),
        visit_count=3,
    )


class TestExporter(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_output_dir = exporter.OUTPUT_DIR
        exporter.OUTPUT_DIR = Path(self._tmp.name)
        self.records = [_rec()]

    def tearDown(self):
        exporter.OUTPUT_DIR = self._orig_output_dir
        self._tmp.cleanup()

    def test_export_json(self):
        paths = exporter.export_history(self.records, "json")
        self.assertEqual(len(paths), 1)
        data = json.loads(paths[0].read_text(encoding="utf-8"))
        self.assertEqual(data[0]["url"], "https://example.com")
        self.assertEqual(data[0]["browser"], "Google Chrome")

    def test_export_csv(self):
        paths = exporter.export_history(self.records, "csv")
        self.assertEqual(len(paths), 1)
        with open(paths[0], newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["url"], "https://example.com")
        self.assertEqual(rows[0]["visit_count"], "3")

    def test_export_txt(self):
        paths = exporter.export_history(self.records, "txt")
        content = paths[0].read_text(encoding="utf-8")
        self.assertIn("https://example.com", content)
        self.assertIn("Google Chrome", content)

    def test_export_all_writes_three_files(self):
        paths = exporter.export_history(self.records, "all")
        self.assertEqual(len(paths), 3)
        extensions = {p.suffix for p in paths}
        self.assertEqual(extensions, {".json", ".txt", ".csv"})

    def test_export_both_alias_still_works(self):
        paths = exporter.export_history(self.records, "both")
        self.assertEqual(len(paths), 3)

    def test_comma_separated_formats(self):
        paths = exporter.export_history(self.records, "json,csv")
        extensions = {p.suffix for p in paths}
        self.assertEqual(extensions, {".json", ".csv"})

    def test_unsupported_format_raises(self):
        with self.assertRaises(ValueError):
            exporter.export_history(self.records, "xml")


if __name__ == "__main__":
    unittest.main()
