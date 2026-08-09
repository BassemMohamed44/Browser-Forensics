from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from browsers import BROWSERS, CHROMIUM, FIREFOX, BrowserSpec
from utils import current_platform


_IGNORED_CHROMIUM_FOLDER_NAMES = {
    "System Profile",
    "Crashpad",
    "ShaderCache",
    "GrShaderCache",
    "GraphiteDawnCache",
    "OptimizationGuidePredictionModels",
    "component_crx_cache",
    "extensions_crx_cache",
    "WidevineCdm",
    "CertificateRevocation",
    "SwReporter",
}


@dataclass
class BrowserProfile:
    browser_key: str   
    browser_name: str   
    engine: str          
    name: str            
    path: Path           
    history_path: Path   

    @property
    def label(self) -> str:
        return f"{self.browser_name} - {self.name}"


def _looks_like_chromium_profile_dir(entry: Path) -> bool:
    if not entry.is_dir():
        return False
    if entry.name in _IGNORED_CHROMIUM_FOLDER_NAMES:
        return False
    if entry.name.startswith("."):
        return False
    return (entry / "History").exists() or (entry / "Preferences").exists()


def _detect_chromium_profiles(spec: BrowserSpec, user_data_dir: Path) -> List[BrowserProfile]:
    profiles: List[BrowserProfile] = []

    for entry in sorted(user_data_dir.iterdir()):
        if not _looks_like_chromium_profile_dir(entry):
            continue

        history_path = entry / "History"
        profiles.append(
            BrowserProfile(
                browser_key=spec.key,
                browser_name=spec.display_name,
                engine=CHROMIUM,
                name=entry.name,
                path=entry,
                history_path=history_path,
            )
        )

    return profiles


def _detect_firefox_profiles(spec: BrowserSpec, profiles_dir: Path) -> List[BrowserProfile]:
    profiles: List[BrowserProfile] = []

    for entry in sorted(profiles_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue

        history_path = entry / "places.sqlite"
        if not history_path.exists():
            continue

        profiles.append(
            BrowserProfile(
                browser_key=spec.key,
                browser_name=spec.display_name,
                engine=FIREFOX,
                name=entry.name,
                path=entry,
                history_path=history_path,
            )
        )

    return profiles


def detect_installed_browsers() -> List[BrowserSpec]:
    plat = current_platform()
    installed: List[BrowserSpec] = []
    seen_roots: Set[Path] = set()

    for spec in BROWSERS.values():
        root = spec.data_root(plat)
        if root is None or not root.exists():
            continue
        resolved = root.resolve()
        if resolved in seen_roots:
            continue
        seen_roots.add(resolved)
        installed.append(spec)

    return installed


def detect_profiles_for_browser(spec: BrowserSpec) -> List[BrowserProfile]:
    plat = current_platform()
    root = spec.data_root(plat)

    if root is None:
        raise FileNotFoundError(
            f"{spec.display_name} is not supported on this platform ({plat})."
        )
    if not root.exists():
        raise FileNotFoundError(
            f"{spec.display_name} installation not found. Expected data at: {root}"
        )

    if spec.engine == CHROMIUM:
        return _detect_chromium_profiles(spec, root)
    return _detect_firefox_profiles(spec, root)


def detect_all_profiles(browser_keys: List[str] = None) -> List[BrowserProfile]:
    all_profiles: List[BrowserProfile] = []
    installed = detect_installed_browsers()

    if browser_keys:
        wanted = set(browser_keys)
        installed = [spec for spec in installed if spec.key in wanted]
    all_profiles: List[BrowserProfile] = []
    installed = detect_installed_browsers()

    if browser_keys:
        wanted = set(browser_keys)
        installed = [spec for spec in installed if spec.key in wanted]

    for spec in installed:
        try:
            all_profiles.extend(detect_profiles_for_browser(spec))
        except FileNotFoundError:
            continue

    return all_profiles
