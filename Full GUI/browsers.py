from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from utils import (
    WINDOWS,
    MACOS,
    LINUX,
    get_linux_config_dir,
    get_macos_app_support_dir,
    get_windows_local_app_data,
    get_windows_roaming_app_data,
)

CHROMIUM = "chromium"
FIREFOX = "firefox"


class BrowserSpec:
    """Static description of a supported browser and where to find its data."""

    def __init__(self, key: str, display_name: str, engine: str, paths: Dict[str, Path]):
        self.key = key
        self.display_name = display_name
        self.engine = engine
        self.paths = paths

    def data_root(self, plat: str) -> Optional[Path]:
        return self.paths.get(plat)


# ---------------------------------------------------------------------------
# Chromium-based browsers
# ---------------------------------------------------------------------------

BROWSERS: Dict[str, BrowserSpec] = {
    "chrome": BrowserSpec(
        key="chrome",
        display_name="Google Chrome",
        engine=CHROMIUM,
        paths={
            WINDOWS: get_windows_local_app_data() / "Google" / "Chrome" / "User Data",
            MACOS: get_macos_app_support_dir() / "Google" / "Chrome",
            LINUX: get_linux_config_dir() / "google-chrome",
        },
    ),
    "chrome_beta": BrowserSpec(
        key="chrome_beta",
        display_name="Google Chrome Beta",
        engine=CHROMIUM,
        paths={
            WINDOWS: get_windows_local_app_data() / "Google" / "Chrome Beta" / "User Data",
            MACOS: get_macos_app_support_dir() / "Google" / "Chrome Beta",
            LINUX: get_linux_config_dir() / "google-chrome-beta",
        },
    ),
    "edge": BrowserSpec(
        key="edge",
        display_name="Microsoft Edge",
        engine=CHROMIUM,
        paths={
            WINDOWS: get_windows_local_app_data() / "Microsoft" / "Edge" / "User Data",
            MACOS: get_macos_app_support_dir() / "Microsoft Edge",
            LINUX: get_linux_config_dir() / "microsoft-edge",
        },
    ),
    "brave": BrowserSpec(
        key="brave",
        display_name="Brave",
        engine=CHROMIUM,
        paths={
            WINDOWS: get_windows_local_app_data() / "BraveSoftware" / "Brave-Browser" / "User Data",
            MACOS: get_macos_app_support_dir() / "BraveSoftware" / "Brave-Browser",
            LINUX: get_linux_config_dir() / "BraveSoftware" / "Brave-Browser",
        },
    ),
    "opera": BrowserSpec(
        key="opera",
        display_name="Opera",
        engine=CHROMIUM,
        paths={
            WINDOWS: get_windows_roaming_app_data() / "Opera Software" / "Opera Stable",
            MACOS: get_macos_app_support_dir() / "com.operasoftware.Opera",
            LINUX: get_linux_config_dir() / "opera",
        },
    ),
    "vivaldi": BrowserSpec(
        key="vivaldi",
        display_name="Vivaldi",
        engine=CHROMIUM,
        paths={
            WINDOWS: get_windows_local_app_data() / "Vivaldi" / "User Data",
            MACOS: get_macos_app_support_dir() / "Vivaldi",
            LINUX: get_linux_config_dir() / "vivaldi",
        },
    ),
    "chromium": BrowserSpec(
        key="chromium",
        display_name="Chromium",
        engine=CHROMIUM,
        paths={
            WINDOWS: get_windows_local_app_data() / "Chromium" / "User Data",
            MACOS: get_macos_app_support_dir() / "Chromium",
            LINUX: get_linux_config_dir() / "chromium",
        },
    ),

    "firefox": BrowserSpec(
        key="firefox",
        display_name="Mozilla Firefox",
        engine=FIREFOX,
        paths={
            WINDOWS: get_windows_roaming_app_data() / "Mozilla" / "Firefox" / "Profiles",
            MACOS: get_macos_app_support_dir() / "Firefox" / "Profiles",
            LINUX: get_linux_config_dir() / "mozilla" / "firefox",
        },
    ),
    "firefox_esr": BrowserSpec(
        key="firefox_esr",
        display_name="Firefox ESR",
        engine=FIREFOX,
        paths={
            WINDOWS: get_windows_roaming_app_data() / "Mozilla" / "Firefox" / "Profiles",
            MACOS: get_macos_app_support_dir() / "Firefox" / "Profiles",
            LINUX: get_linux_config_dir() / "mozilla" / "firefox",
        },
    ),
}


def all_browser_keys() -> list[str]:
    return list(BROWSERS.keys())
