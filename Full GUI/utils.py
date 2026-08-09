from __future__ import annotations

import os
import platform
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

WINDOWS = "windows"
MACOS = "macos"
LINUX = "linux"


def current_platform() -> str:
    system = platform.system().lower()
    if system == "windows":
        return WINDOWS
    if system == "darwin":
        return MACOS
    return LINUX


# ---------------------------------------------------------------------------
# Chromium family
# ---------------------------------------------------------------------------
_CHROME_EPOCH = datetime(1601, 1, 1)

_UNIX_EPOCH = datetime(1970, 1, 1)

    
def chrome_time_to_datetime(chrome_timestamp: int) -> Optional[datetime]:
    if not chrome_timestamp:
        return None
    try:
        return _CHROME_EPOCH + timedelta(microseconds=chrome_timestamp)
    except (OverflowError, OSError, ValueError):
        return None


def datetime_to_chrome_time(dt: datetime) -> int:
    delta = dt - _CHROME_EPOCH
    return int(delta.total_seconds() * 1_000_000)


def firefox_time_to_datetime(prtime: int) -> Optional[datetime]:
    if not prtime:
        return None
    try:
        return _UNIX_EPOCH + timedelta(microseconds=prtime)
    except (OverflowError, OSError, ValueError):
        return None


def datetime_to_firefox_time(dt: datetime) -> int:
    delta = dt - _UNIX_EPOCH
    return int(delta.total_seconds() * 1_000_000)


def format_datetime(dt: Optional[datetime]) -> str:
    if dt is None:
        return "Unknown"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_user_date(date_str: str) -> datetime:
    return datetime.strptime(date_str.strip(), "%Y-%m-%d")


# ---------------------------------------------------------------------------
# Per-platform
# ---------------------------------------------------------------------------


def get_windows_local_app_data() -> Path:
    value = os.environ.get("LOCALAPPDATA")
    if value:
        return Path(value)
    return Path.home() / "AppData" / "Local"


def get_windows_roaming_app_data() -> Path:
    value = os.environ.get("APPDATA")
    if value:
        return Path(value)
    return Path.home() / "AppData" / "Roaming"


def get_macos_app_support_dir() -> Path:
    return Path.home() / "Library" / "Application Support"


def get_linux_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".config"


def ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def safe_copy_database(source_path: Path) -> Path:
    if not source_path.exists():
        raise FileNotFoundError(f"History database not found: {source_path}")

    temp_dir = Path(tempfile.gettempdir())
    unique = f"{os.getpid()}_{abs(hash(str(source_path)))}"
    temp_file = temp_dir / f"browser_history_copy_{unique}{source_path.suffix or '.db'}"

    try:
        shutil.copy2(source_path, temp_file)
        for suffix in ("-wal", "-shm"):
            sidecar = source_path.with_name(source_path.name + suffix)
            if sidecar.exists():
                try:
                    shutil.copy2(sidecar, temp_file.with_name(temp_file.name + suffix))
                except OSError:
                    pass
    except PermissionError as exc:
        raise PermissionError(
            f"Permission denied while copying database: {source_path}"
        ) from exc
    except OSError as exc:
        raise OSError(f"Failed to copy database {source_path}: {exc}") from exc

    return temp_file


def cleanup_temp_file(temp_path: Path) -> None:
    for candidate in (temp_path, temp_path.with_name(temp_path.name + "-wal"),
                      temp_path.with_name(temp_path.name + "-shm")):
        try:
            if candidate.exists():
                candidate.unlink()
        except OSError:
            pass


def sanitize_filename(name: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name.strip() or "unnamed"
