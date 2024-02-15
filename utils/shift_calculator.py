import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Tuple
from enum import Enum


class ShiftType(Enum):
    REST = "X"


class ShiftCalculator:
    BASE_HOURS = 8
    OVERTIME_HOURS_LIMIT = 2
    OVERTIME_RATE_1 = 1.33
    OVERTIME_RATE_2 = 1.66
    HOLIDAY_RATE = 2
    HOURLY_RATE = 190

    def __init__(
            self,
            shift_type_file: Path,
            shift_file: Path,  # noqa
            holiday_file: Path):  # noqa
        self.shift_type_file = shift_type_file
        self.shift_file = shift_file
        self.holiday_file = holiday_file
        self.shift_type = self._load_json_file(self.shift_type_file)
        self.shifts = self._load_json_file(self.shift_file)
        self.holidays = self._load_json_file(self.holiday_file)

    @staticmethod
    def _load_json_file(file_path: Path) -> Dict[str, Any]:
        """Load and return data from a JSON file."""
        return json.loads(file_path.read_text())

    def calculate_overtime_pay(self, duty_hours: timedelta) -> float:
        """Calculate the overtime pay based on the duty hours."""
        duty_hours = duty_hours.total_seconds() / 3600
        resting_hours = np.ceil(duty_hours / 4) * 0.5
        working_hours = np.floor([duty_hours - resting_hours])
        overtime_hours = np.floor(np.max([0, duty_hours - self.BASE_HOURS]))

        if duty_hours <= self.BASE_HOURS:
            return working_hours * self.HOURLY_RATE
        elif overtime_hours <= self.OVERTIME_HOURS_LIMIT:
            return (self.BASE_HOURS * self.HOURLY_RATE) + (
                overtime_hours * self.HOURLY_RATE * self.OVERTIME_RATE_1)
        else:  # overtime_hours > 2
            return (self.BASE_HOURS * self.HOURLY_RATE) + (
                self.OVERTIME_HOURS_LIMIT * self.HOURLY_RATE *
                self.OVERTIME_RATE_1) + (
                    (overtime_hours - self.OVERTIME_HOURS_LIMIT) *
                    self.HOURLY_RATE * self.OVERTIME_RATE_2)

    @staticmethod
    def _calculate_shift_duration(start_time: str, end_time: str) -> timedelta:
        """Calculate and return the duration of a shift."""
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        return end - start

    def calculate_total_working_hours_and_wage(self) -> Tuple[float, float]:
        """Calculate and return the total working hours and wage."""
        total_wage = 0
        total_working_time = timedelta(0)

        for date, shift in self.shifts.items():
            if shift == ShiftType.REST.value:
                continue

            duration = self._calculate_shift_duration(
                self.shift_type[shift]["start_time"],
                self.shift_type[shift]["end_time"])
            total_working_time += duration

            if date in self.holidays:
                print(f"Date: {date} is a holiday")
                total_wage += duration.total_seconds(
                ) / 3600 * self.HOURLY_RATE * self.HOLIDAY_RATE
            else:
                total_wage += self.calculate_overtime_pay(duration)

        total_working_hours = round(total_working_time.total_seconds() / 3600,
                                    2)
        total_wage = round(total_wage, 2)

        return total_working_hours, total_wage

    def __str__(self) -> str:
        total_working_hours, total_salary = self.calculate_total_working_hours_and_wage(
        )
        return f"Total duty hours: {total_working_hours}\nTotal salary: {total_salary}"


if __name__ == "__main__":
    shift_type_file = Path("./data/shift_type.json")
    shift_file = Path("./data/jan_shift.json")
    holiday_file = Path("./data/holiday.json")

    calculator = ShiftCalculator(shift_type_file, shift_file, holiday_file)
    print(calculator)
