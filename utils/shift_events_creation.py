# [START calendar_quickstart]
import json
from datetime import datetime
from pathlib import Path

from google_calendar_api import APIConnector
from shift_calculator import ShiftCalculator, ShiftDataReader

SHIFT_TYPE_PATH = Path("./data/shift_type.json")
HOLIDAY_PATH = Path("./data/holiday.json")


def check_latest_shift():
    # first, list all the files in the data folder ends with _shift.json, the prefix is the month
    # then, find the latest month
    # finally, return the latest month file path
    files = list(Path("./data").glob("*_shift.json"))
    latest_file = max(files, key=lambda x: x.stat().st_mtime)
    print(f"create shift events from {latest_file}")
    return latest_file


def load_data(shift_type_path: str, shift_time_path: str):
    with open(shift_type_path, "r") as f:
        shift_type = json.load(f)

    with open(shift_time_path, "r") as f:
        shift_time = json.load(f)

    return shift_type, shift_time


def create_event(
    service, start_time: datetime, end_time: datetime, summary: str, description: str
):
    event = {
        "summary": summary,
        "location": "No. 7, Section 5, Xinyi Road, Xinyi District, Taipei City, Taiwan 110",
        "description": description,
        "start": {
            "dateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "Asia/Taipei",
        },
        "end": {
            "dateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "Asia/Taipei",
        },
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    print("Event created: %s" % (event.get("htmlLink")))


def process_shifts(service, shift_type: dict, shift_time: dict):
    count = 0
    for day, shift in shift_time.items():
        if shift == "X":
            count = 0
            continue

        start_time_str = shift_type[shift]["start_time"]
        end_time_str = shift_type[shift]["end_time"]

        start_time = datetime.strptime(f"{day} {start_time_str}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{day} {end_time_str}", "%Y-%m-%d %H:%M")

        summary = f"Workday {shift} {count+1}th"
        description = f"Shift: {shift}, Location: Taipei101"

        create_event(service, start_time, end_time, summary, description)

        count += 1


def main():
    SHIFT_TIME_PATH = check_latest_shift()
    with APIConnector() as service:
        shift_type, shift_time = load_data(SHIFT_TYPE_PATH, SHIFT_TIME_PATH)
        process_shifts(service, shift_type, shift_time)

    data_reader = ShiftDataReader(SHIFT_TYPE_PATH, SHIFT_TIME_PATH, HOLIDAY_PATH)
    calculator = ShiftCalculator(data_reader)
    print(calculator)


if __name__ == "__main__":
    main()
# [END calendar_quickstart]
