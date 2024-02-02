import json
import dataclasses
from datetime import datetime
from collections import Counter
from datetime import timedelta
from typing import Dict, Any


@dataclasses.dataclass
class ShiftCalculator:
    shift_type_file: str
    shift_file: str
    hourly_rate: float

    def __post_init__(self) -> None:
        self.shift_type = self._load_json_file(self.shift_type_file)
        self.shifts = self._load_json_file(self.shift_file)

    @staticmethod
    def _load_json_file(file_path: str) -> Dict[str, Any]:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data

    @staticmethod
    def _calculate_shift_duration(start_time: str, end_time: str) -> timedelta:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        duration = end - start
        return duration

    def calculate_total_working_time(self) -> timedelta:
        total_working_time = timedelta(0)
        for shift, frequency in Counter(self.shifts.values()).items():
            if shift == "X" or shift not in self.shift_type:
                continue
            shift_duration = self._calculate_shift_duration(
                self.shift_type[shift]["start_time"],
                self.shift_type[shift]["end_time"])
            total_working_time += shift_duration * frequency
        return total_working_time

    def calculate_total_working_hours(self) -> float:
        total_working_time = self.calculate_total_working_time()
        total_working_hours = total_working_time.total_seconds() / 3600
        return total_working_hours

    def calculate_total_salary(self) -> float:
        total_working_hours = self.calculate_total_working_hours()
        total_salary = total_working_hours * self.hourly_rate
        return total_salary

    def print_results(self) -> None:
        total_working_hours = self.calculate_total_working_hours()
        total_salary = self.calculate_total_salary()
        print(f"Total working hours: {total_working_hours}")
        print(f"Total salary: {total_salary}")


if __name__ == "__main__":
    calculator = ShiftCalculator("./data/shift_type.json",
                                 "./data/fab_shift.json", 190)
    calculator.print_results()
