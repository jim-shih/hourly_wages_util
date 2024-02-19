import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np


class Shift(Enum):
    REST = "X"


class Wage(Enum):
    BASE_HOURS = 8
    OVERTIME_HOURS_LIMIT = 2
    OVERTIME_RATE_1 = 1.33
    OVERTIME_RATE_2 = 1.66
    HOLIDAY_RATE = 2
    HOURLY_RATE = 190


class ShiftDataReader:
    """Class to read and manage shift data."""

    def __init__(self, _shift_type_file: Path, _shift_file: Path,
                 _holiday_file: Path):
        self.shift_type = self._load_json_file(_shift_type_file)
        self.shifts = self._load_json_file(_shift_file)
        self.holidays = self._load_json_file(_holiday_file)
        self.holidays = [
            datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            for date in self.holidays
        ]

    @staticmethod
    def _load_json_file(file_path: Path) -> Dict[str, Any]:
        """Load a JSON file and return its contents."""
        return json.loads(file_path.read_text())

    def get_shift(self, key: str) -> Any:
        """Get a specific shift by its key."""
        return self.shifts[key]


class ShiftCalculator:
    """Class to calculate total working hours and wage."""

    def __init__(self, _data_reader: ShiftDataReader):
        self.data_reader = _data_reader
        self._set_wage_info()

    def _set_wage_info(self) -> None:
        """Set wage information based on the Wage enum."""
        self.base_hours = Wage.BASE_HOURS.value
        self.overtime_hours_limit = Wage.OVERTIME_HOURS_LIMIT.value
        self.overtime_rate_1 = Wage.OVERTIME_RATE_1.value
        self.overtime_rate_2 = Wage.OVERTIME_RATE_2.value
        self.holiday_rate = Wage.HOLIDAY_RATE.value
        self.hourly_rate = Wage.HOURLY_RATE.value

    def _calculate_holiday_pay(self, duty_hours: timedelta) -> float:
        """Calculate the pay for holiday hours."""
        duty_hours = duty_hours.total_seconds() / 3600
        return duty_hours * self.hourly_rate * self.holiday_rate

    def _calculate_overtime_pay(self, duty_hours: timedelta) -> float:
        """Calculate the pay for overtime hours."""
        duty_hours = duty_hours.total_seconds() / 3600
        resting_hours = np.round(duty_hours / 4, 0) * 0.5
        working_hours = duty_hours - resting_hours
        overtime_hours = np.floor(np.max([0, duty_hours - self.base_hours]))

        if duty_hours <= self.base_hours:
            return working_hours * self.hourly_rate
        elif overtime_hours <= self.overtime_hours_limit:
            return self._calculate_overtime_pay_rate_1(overtime_hours)
        else:
            return self._calculate_overtime_pay_rate_2(overtime_hours)

    def _calculate_overtime_pay_rate_1(self, overtime_hours: float) -> float:
        """Calculate the pay for overtime hours with rate 1."""
        base_pay = self.base_hours * self.hourly_rate
        overtime_pay = overtime_hours * self.hourly_rate * self.overtime_rate_1
        return base_pay + overtime_pay

    def _calculate_overtime_pay_rate_2(self, overtime_hours: float) -> float:
        """Calculate the pay for overtime hours with rate 2."""
        base_pay = self.base_hours * self.hourly_rate
        overtime_pay_1 = self.overtime_hours_limit * self.hourly_rate * self.overtime_rate_1
        overtime_pay_2 = (overtime_hours - self.overtime_hours_limit
                          ) * self.hourly_rate * self.overtime_rate_2
        return base_pay + overtime_pay_1 + overtime_pay_2

    def calculate_total_working_hours_and_wage(self) -> Tuple[float, float]:
        """Calculate the total working hours and wage."""
        total_wage = 0
        total_working_time = timedelta(0)

        for _date, shift in self.data_reader.shifts.items():
            if shift == Shift.REST.value:
                continue

            date = datetime.strptime(_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            duration = self._calculate_shift_duration(
                self.data_reader.shift_type[shift]["start_time"],
                self.data_reader.shift_type[shift]["end_time"])
            total_working_time += self._calculate_working_hours(duration)

            if date in self.data_reader.holidays:
                print(f"Date: {date} is a holiday, applying holiday rate.")
                total_wage += self._calculate_holiday_pay(duration)
            else:
                total_wage += self._calculate_overtime_pay(duration)

        total_working_hours = round(total_working_time.total_seconds() / 3600,
                                    2)
        total_wage = round(total_wage, 2)

        return total_working_hours, total_wage

    @staticmethod
    def _calculate_working_hours(duration: timedelta) -> timedelta:
        """Calculate the working hours from a given duration."""
        duty_hours = duration.total_seconds() / 3600
        resting_hours = np.round(duty_hours / 4, 0) * 0.5
        working_hours = duty_hours - resting_hours
        return timedelta(hours=working_hours)

    @staticmethod
    def _calculate_shift_duration(start_time: str, end_time: str) -> timedelta:
        """Calculate the duration of a shift."""
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        return end - start

    def __str__(self) -> str:
        total_working_hours, total_salary = self.calculate_total_working_hours_and_wage(
        )
        return f"Total duty hours: {total_working_hours}\nTotal salary: {total_salary}"


if __name__ == "__main__":
    shift_type_file = Path("./data/shift_type.json")
    shift_file = Path("./data/feb_shift.json")
    holiday_file = Path("./data/holiday.json")
    data_reader = ShiftDataReader(shift_type_file, shift_file, holiday_file)
    calculator = ShiftCalculator(data_reader)
    print(calculator)
