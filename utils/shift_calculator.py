import dataclasses
import json
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict


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

    def calculate_overtime_pay(self, total_hours: timedelta) -> float:
        total_hours = total_hours.total_seconds() / 3600
        if total_hours <= 8:
            return total_hours * self.hourly_rate
        else:
            overtime_hours = total_hours - 8
            if overtime_hours <= 2:
                return (8 * self.hourly_rate) + (overtime_hours *
                                                 self.hourly_rate * 1.33)
            else:
                first_two_hours_overtime = 2 * self.hourly_rate * 1.33
                remaining_overtime = (overtime_hours -
                                      2) * self.hourly_rate * 1.66
                return (8 * self.hourly_rate
                        ) + first_two_hours_overtime + remaining_overtime

    @staticmethod
    def _calculate_shift_duration(start_time: str, end_time: str) -> timedelta:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        duration = end - start
        return duration

    def calculate_total_wage(self) -> (float, timedelta):
        total_wage = 0
        total_working_time = timedelta(0)
        for shift, frequency in Counter(self.shifts.values()).items():
            if shift == "X" or shift not in self.shift_type:
                continue
            shift_duration = self._calculate_shift_duration(
                self.shift_type[shift]["start_time"],
                self.shift_type[shift]["end_time"])
            total_wage += self.calculate_overtime_pay(
                shift_duration) * frequency
            total_working_time += shift_duration * frequency
        return total_wage, total_working_time

    def calculate_total_working_hours(self) -> (float, float):
        total_wage, total_working_time = self.calculate_total_wage()
        total_working_hours = total_working_time.total_seconds() / 3600
        return total_working_hours, total_wage

    def print_results(self) -> None:
        total_working_hours, total_salary = self.calculate_total_working_hours(
        )
        print(f"Total working hours: {total_working_hours}")
        print(f"Total salary: {total_salary}")


if __name__ == "__main__":
    calculator = ShiftCalculator("./data/shift_type.json",
                                 "./data/jan_shift.json", 190)
    calculator.print_results()
