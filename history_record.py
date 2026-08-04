from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class HistoryRecord:
    """A single browsing history entry, normalized across browsers/profiles."""
    browser: str           
    profile: str             
    title: str
    url: str
    visit_time: Optional[datetime]
    visit_count: int

    def to_dict(self) -> dict:
        return {
            "browser": self.browser,
            "profile": self.profile,
            "title": self.title,
            "url": self.url,
            "visit_time": self.visit_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.visit_time
            else None,
            "visit_count": self.visit_count,
        }


class ProfileReadError(Exception):

    def __init__(self, profile_label: str, reason: str):
        self.profile_label = profile_label
        self.reason = reason
        super().__init__(f"[{profile_label}] {reason}")
