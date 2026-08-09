from __future__ import annotations

from datetime import datetime, time
from typing import List, Optional

from exporter import export_history
from filters import filter_by_domain, search_records
from history_record import HistoryRecord
from log_setup import configure_logging, get_logger
from profiles import BrowserProfile, detect_all_profiles, detect_installed_browsers
from reader import read_all_history
from stats import compute_statistics, format_statistics
from utils import current_platform, parse_user_date

log = get_logger(__name__)

MENU_TEXT = """
====================================
Browser History Exporter
====================================

1. Export ALL History (all browsers)
2. Export Between Dates (all browsers)
3. Choose Browsers to Export
4. Exit
"""


def _print_platform_banner() -> None:
    plat = current_platform()
    label = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}.get(plat, plat)
    log.info("Detected platform: %s", label)


def scan_profiles(browser_keys: Optional[List[str]] = None) -> Optional[List[BrowserProfile]]:
    log.info("Scanning browser profiles...")
    profiles = detect_all_profiles(browser_keys)

    if not profiles:
        log.warning("No browser profiles were found. Nothing to export.")
        return None

    log.info("Found:")
    for profile in profiles:
        log.info("  - %s", profile.label)

    return profiles


def prompt_export_format() -> str:
    print("\nChoose export format:")
    print("  1. JSON")
    print("  2. TXT")
    print("  3. CSV")
    print("  4. All of the above")
    choice = input("Enter choice [1-4]: ").strip()

    return {"1": "json", "2": "txt", "3": "csv", "4": "all"}.get(choice, "all")


def prompt_browser_selection() -> Optional[List[str]]:
    installed = detect_installed_browsers()
    if not installed:
        log.warning("No supported browsers were found on this machine.")
        return None

    print("\nInstalled browsers:")
    for i, spec in enumerate(installed, start=1):
        print(f"  {i}. {spec.display_name}")

    raw = input(
        "\nEnter the numbers of the browsers to export, separated by commas "
        "(or press Enter for all): "
    ).strip()

    if not raw:
        return [spec.key for spec in installed]

    chosen_keys: List[str] = []
    for token in raw.split(","):
        token = token.strip()
        if not token.isdigit():
            continue
        index = int(token) - 1
        if 0 <= index < len(installed):
            chosen_keys.append(installed[index].key)

    return chosen_keys or [spec.key for spec in installed]


def prompt_filters(records: List[HistoryRecord]) -> List[HistoryRecord]:
    domain = input(
        "\nFilter by domain (e.g. youtube.com), or press Enter to skip: "
    ).strip()
    if domain:
        before = len(records)
        records = filter_by_domain(records, domain)
        log.info("Domain filter '%s': %d -> %d record(s).", domain, before, len(records))

    query = input(
        "Search title/URL for a keyword, or press Enter to skip: "
    ).strip()
    if query:
        before = len(records)
        records = search_records(records, query)
        log.info("Search '%s': %d -> %d record(s).", query, before, len(records))

    return records


def run_export(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    browser_keys: Optional[List[str]] = None,
) -> None:
    profiles = scan_profiles(browser_keys)
    if not profiles:
        return

    log.info("Reading databases...")
    records, errors = read_all_history(profiles, start_date, end_date)

    if errors:
        log.warning("%d profile(s) were skipped due to errors:", len(errors))
        for err in errors:
            log.warning("  - %s", err)

    if not records:
        log.warning("No history records matched the given criteria. Nothing to export.")
        return

    records = prompt_filters(records)
    if not records:
        log.warning("No history records left after filtering. Nothing to export.")
        return

    export_format = prompt_export_format()

    log.info("Exporting...")
    written_files = export_history(records, export_format)
    for path in written_files:
        log.info("  -> Written: %s", path)

    stats = compute_statistics(records)
    print(format_statistics(stats))

    log.info("Finished.")


def export_all_history() -> None:
    run_export(start_date=None, end_date=None)


def export_between_dates() -> None:
    print("\nEnter the date range (format: YYYY-MM-DD)")

    while True:
        try:
            from_str = input("From: ").strip()
            to_str = input("To: ").strip()
            start_date = parse_user_date(from_str)
            # Include the entire "to" day by setting time to 23:59:59.
            end_date = datetime.combine(parse_user_date(to_str).date(), time(23, 59, 59))
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (e.g. 2026-06-01).\n")

    if start_date > end_date:
        print("The 'From' date must be before the 'To' date.")
        return

    run_export(start_date=start_date, end_date=end_date)


def export_chosen_browsers() -> None:
    browser_keys = prompt_browser_selection()
    if not browser_keys:
        return
    run_export(start_date=None, end_date=None, browser_keys=browser_keys)


def main() -> None:
    log_path = configure_logging()
    log.debug("Log file for this run: %s", log_path)
    _print_platform_banner()

    while True:
        print(MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "1":
            export_all_history()
        elif choice == "2":
            export_between_dates()
        elif choice == "3":
            export_chosen_browsers()
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option. Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting.")
