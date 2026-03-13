import csv
import json
from datetime import datetime, timedelta

# Week ranges (start_date, end_date) - None means single day
WEEK_RANGES = {
    1:  ("09/02/2026", "14/02/2026"),
    2:  ("23/02/2026", "28/02/2026"),
    3:  ("02/03/2026", "07/03/2026"),
    4:  ("09/03/2026", "14/03/2026"),
    5:  ("16/03/2026", "16/03/2026"),  # single day
    6:  ("23/03/2026", "28/03/2026"),
    7:  ("30/03/2026", "04/04/2026"),
    8:  ("06/04/2026", "11/04/2026"),
    9:  ("13/04/2026", "18/04/2026"),
    10: ("20/04/2026", "25/04/2026"),
    11: ("04/05/2026", "09/05/2026"),
    12: ("11/05/2026", "16/05/2026"),
    13: ("18/05/2026", "22/05/2026"),
}

DAY_TO_WEEKDAY = {
    "MONDAY": 0,
    "TUESDAY": 1,
    "WEDNESDAY": 2,
    "THURSDAY": 3,
    "FRIDAY": 4,
    "SATURDAY": 5,
    "SUNDAY": 6,
}

def get_date_for_day_in_week(week_num, day_name):
    """Return the specific date (DD/MM/YYYY) for a given day within a week range."""
    start_str, end_str = WEEK_RANGES[week_num]
    start = datetime.strptime(start_str, "%d/%m/%Y")
    end = datetime.strptime(end_str, "%d/%m/%Y")
    target_weekday = DAY_TO_WEEKDAY.get(day_name.upper())
    if target_weekday is None:
        return None
    # Find the date within the range that matches the target weekday
    current = start
    while current <= end:
        if current.weekday() == target_weekday:
            return current.strftime("%d/%m/%Y")
        current += timedelta(days=1)
    return None  # day not found in this week range

def parse_schedule():
    with open("schedule", "r", encoding="utf-8") as f:
        raw = f.read()

    # Parse the TSV using csv module to handle multi-line quoted fields
    reader = csv.reader(raw.splitlines(), delimiter="\t")
    rows = list(reader)

    # The header row (row 0) contains: LECTURER, CLASS DETAILS, WEEK1..WEEK13, then trailing
    # Because of multi-line quoted fields, row 0 spans logical index 0 only when parsed by csv
    # Let's find the header row and data rows
    header_row = rows[0]

    # Build week number -> column index mapping from the header
    # Header: ['LECTURER', 'CLASS DETAILS', 'WEEK\n1\n(9/2/26 - 14/2/26)', ..., 'WEEK\n13\n...']
    week_col = {}  # week_number -> column_index
    for col_idx, cell in enumerate(header_row):
        cell_clean = cell.strip()
        for wn in range(1, 14):
            if f"WEEK\n{wn}\n" in cell or f"WEEK\r\n{wn}\r\n" in cell:
                week_col[wn] = col_idx
                break

    print("Week-to-column mapping:", week_col)
    print(f"Total columns in header: {len(header_row)}")

    # Find rows belonging to each lecturer
    # A lecturer row starts with a non-empty name in col 0
    sessions = []

    # We'll process the rows and find lecturer blocks
    # Each block has: [DAY row, TIME row, VENUE row] for regular sessions
    # and [DAY row, TIME row, VENUE row] for Saturday sessions
    i = 1
    current_lecturer = None

    while i < len(rows):
        row = rows[i]
        if not row:
            i += 1
            continue

        # Skip re-printed header rows
        if len(row) > 0 and row[0].strip() == "LECTURER":
            i += 1
            continue

        col0 = row[0].strip() if len(row) > 0 else ""
        col1 = row[1].strip() if len(row) > 1 else ""

        # Detect lecturer name row
        if col0 and col0 != "LECTURER" and col1 == "DAY":
            current_lecturer = col0
            day_row = row
            # Next rows should be TIME and VENUE
            time_row = rows[i + 1] if i + 1 < len(rows) else []
            venue_row = rows[i + 2] if i + 2 < len(rows) else []

            # Extract regular weekday sessions
            for wn, col_idx in week_col.items():
                day_val = day_row[col_idx].strip() if col_idx < len(day_row) else ""
                time_val = time_row[col_idx].strip() if col_idx < len(time_row) else ""
                venue_val = venue_row[col_idx].strip() if col_idx < len(venue_row) else ""

                if day_val and day_val.upper() not in ("FINAL EXAMINATION WEEK", "CLASS DETAILS", "DAY"):
                    date = get_date_for_day_in_week(wn, day_val)
                    if date:
                        sessions.append({
                            "date": date,
                            "week": wn,
                            "lecturer": current_lecturer,
                            "day": day_val,
                            "time": time_val,
                            "venue": venue_val,
                        })

            i += 3  # skip TIME and VENUE rows
            continue

        # Saturday / supplementary session rows (col0 is empty, col1 is DAY/TIME/VENUE)
        if col0 == "" and col1 == "DAY" and current_lecturer:
            sat_day_row = row
            sat_time_row = rows[i + 1] if i + 1 < len(rows) else []
            sat_venue_row = rows[i + 2] if i + 2 < len(rows) else []

            for wn, col_idx in week_col.items():
                day_val = sat_day_row[col_idx].strip() if col_idx < len(sat_day_row) else ""
                time_val = sat_time_row[col_idx].strip() if col_idx < len(sat_time_row) else ""
                venue_val = sat_venue_row[col_idx].strip() if col_idx < len(sat_venue_row) else ""

                if day_val and day_val.upper() not in ("FINAL EXAMINATION WEEK", "CLASS DETAILS", "DAY"):
                    date = get_date_for_day_in_week(wn, day_val)
                    if date:
                        sessions.append({
                            "date": date,
                            "week": wn,
                            "lecturer": current_lecturer,
                            "day": day_val,
                            "time": time_val,
                            "venue": venue_val,
                        })

            i += 3
            continue

        i += 1

    # Sort by date
    sessions.sort(key=lambda s: datetime.strptime(s["date"], "%d/%m/%Y"))

    return sessions

sessions = parse_schedule()

print(f"\nTotal sessions extracted: {len(sessions)}\n")

# Write to JSON (date as primary key, with list of sessions per date)
schedule_by_date = {}
for s in sessions:
    date = s["date"]
    if date not in schedule_by_date:
        schedule_by_date[date] = []
    schedule_by_date[date].append({
        "lecturer": s["lecturer"],
        "day": s["day"],
        "time": s["time"],
        "venue": s["venue"],
        "week": s["week"],
    })

with open("schedule_formatted.json", "w") as f:
    json.dump(schedule_by_date, f, indent=2)

# Also write a flat CSV
with open("schedule_formatted.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "week", "day", "time", "venue", "lecturer"])
    for s in sessions:
        writer.writerow([s["date"], s["week"], s["day"], s["time"], s["venue"], s["lecturer"]])

print("Outputs written to schedule_formatted.json and schedule_formatted.csv")
print("\nPreview (first 10 entries):")
for s in sessions[:10]:
    print(f"  {s['date']} | {s['day']:<10} | {s['time']:<22} | {s['venue']:<10} | {s['lecturer']}")

# Debug: Print raw session list
print("\nAll sessions:")
for s in sessions:
    print(f"  {s['date']} | W{s['week']:<2} | {s['day']:<10} | {s['time']:<22} | {s['venue']:<10} | {s['lecturer']}")
