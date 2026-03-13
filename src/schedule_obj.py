from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ScheduleEntry:
    date: date
    day: str
    lecturer: str
    time: str
    venue: str
    week: str
