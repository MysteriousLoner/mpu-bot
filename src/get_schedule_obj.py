from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import List

from schedule_obj import ScheduleEntry


def _parse_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def get_schedule_obj(target_date: date, csv_path: str) -> List[ScheduleEntry]:
    path = Path(csv_path)
    entries: List[ScheduleEntry] = []

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_date = _parse_date(row["Date"])
            if row_date != target_date:
                continue
            entries.append(
                ScheduleEntry(
                    date=row_date,
                    day=row.get("Day", "").strip(),
                    lecturer=row.get("Lecturer", "").strip(),
                    time=row.get("Time", "").strip(),
                    venue=row.get("Venue", "").strip(),
                    week=row.get("Week", "").strip(),
                )
            )

    return entries


def get_today_schedule(csv_path: str) -> List[ScheduleEntry]:
    return get_schedule_obj(date.today(), csv_path)
