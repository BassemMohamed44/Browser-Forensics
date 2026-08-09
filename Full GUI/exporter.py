from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List

from history_record import HistoryRecord
from log_setup import get_logger
from utils import ensure_output_dir, format_datetime

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

log = get_logger(__name__)

CSV_FIELDNAMES = ["browser", "profile", "title", "url", "visit_time", "visit_count"]


def _timestamped_filename(prefix: str, extension: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}.{extension}"


def export_to_json(records: List[HistoryRecord], filename: str) -> Path:
    output_dir = ensure_output_dir(OUTPUT_DIR)
    file_path = output_dir / filename

    data = [record.to_dict() for record in records]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return file_path


def export_to_txt(records: List[HistoryRecord], filename: str) -> Path:
    output_dir = ensure_output_dir(OUTPUT_DIR)
    file_path = output_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Browser History Export\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {format_datetime(datetime.now())}\n")
        f.write(f"Total Records: {len(records)}\n")
        f.write("=" * 60 + "\n\n")

        for i, record in enumerate(records, start=1):
            f.write(f"[{i}] Browser:     {record.browser}\n")
            f.write(f"    Profile:     {record.profile}\n")
            f.write(f"    Title:       {record.title}\n")
            f.write(f"    URL:         {record.url}\n")
            f.write(f"    Visit Time:  {format_datetime(record.visit_time)}\n")
            f.write(f"    Visit Count: {record.visit_count}\n")
            f.write("-" * 60 + "\n")

    return file_path


def export_to_csv(records: List[HistoryRecord], filename: str) -> Path:
    output_dir = ensure_output_dir(OUTPUT_DIR)
    file_path = output_dir / filename

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_dict())

    return file_path


_EXPORTERS = {
    "json": ("json", export_to_json),
    "txt": ("txt", export_to_txt),
    "csv": ("csv", export_to_csv),
}


def export_history(records: List[HistoryRecord], export_format: str, prefix: str = "browser_history") -> List[Path]:
    export_format = export_format.lower().strip()

    if export_format in ("both", "all"):
        requested = list(_EXPORTERS.keys())
    else:
        requested = [fmt.strip() for fmt in export_format.split(",") if fmt.strip()]

    unknown = [fmt for fmt in requested if fmt not in _EXPORTERS]
    if unknown:
        raise ValueError(f"Unsupported export format(s): {', '.join(unknown)}")

    written_files: List[Path] = []
    for fmt in requested:
        extension, writer_fn = _EXPORTERS[fmt]
        filename = _timestamped_filename(prefix, extension)
        path = writer_fn(records, filename)
        log.info("Wrote %s (%s records) -> %s", fmt.upper(), len(records), path)
        written_files.append(path)

    if not written_files:
        raise ValueError(f"Unsupported export format: '{export_format}'")

    return written_files
