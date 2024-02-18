import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Tuple
from enum import Enum


class Shift(Enum):
    REST = "X"


class Wage(Enum):
    BASE_HOURS = 8
    OVERTIME_HOURS_LIMIT = 2
    OVERTIME_RATE_1 = 1.33
    OVERTIME_RATE_2 = 1.66
    HOLIDAY_RATE = 2
    HOURLY_RATE = 190


class ShiftCalculator:

    def __init__(self, shift_type_file: Path, shift_file: Path,
                 holiday_file: Path):
        self.shift_type_file = shift_type_file
        self.shift_file = shift_file
        self.holiday_file = holiday_file
        self.shift_type = self._load_json_file(self.shift_type_file)
        self.shifts = self._load_json_file(self.shift_file)
        self.holidays = self._load_json_file(self.holiday_file)
        self.holidays = [
            datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            for date in self.holidays
        ]
        self._set_wage_info()

    def _set_wage_info(self):
        self.base_hours = Wage.BASE_HOURS.value
        self.overtime_hours_limit = Wage.OVERTIME_HOURS_LIMIT.value
        self.overtime_rate_1 = Wage.OVERTIME_RATE_1.value
        self.overtime_rate_2 = Wage.OVERTIME_RATE_2.value
        self.holiday_rate = Wage.HOLIDAY_RATE.value
        self.hourly_rate = Wage.HOURLY_RATE.value

    @staticmethod
    def _load_json_file(file_path: Path) -> Dict[str, Any]:
        return json.loads(file_path.read_text())

    def _calculate_holiday_pay(self, duty_hours: timedelta) -> float:
        duty_hours = duty_hours.total_seconds() / 3600
        return duty_hours * self.hourly_rate * self.holiday_rate

    def _calculate_overtime_pay(self, duty_hours: timedelta) -> float:
        duty_hours = duty_hours.total_seconds() / 3600
        resting_hours = np.round(duty_hours / 4, 0) * 0.5
        working_hours = duty_hours - resting_hours
        overtime_hours = np.floor(np.max([0, duty_hours - self.base_hours]))

        if duty_hours <= self.base_hours:
            return working_hours * self.hourly_rate
        elif overtime_hours <= self.overtime_hours_limit:
            base_pay = self.base_hours * self.hourly_rate
            overtime_pay = overtime_hours * self.hourly_rate * self.overtime_rate_1
            return base_pay + overtime_pay
        else:
            base_pay = self.base_hours * self.hourly_rate
            overtime_pay_1 = self.overtime_hours_limit * self.hourly_rate * self.overtime_rate_1
            overtime_pay_2 = (overtime_hours - self.overtime_hours_limit
                              ) * self.hourly_rate * self.overtime_rate_2
            return base_pay + overtime_pay_1 + overtime_pay_2

    @staticmethod
    def _calculate_shift_duration(start_time: str, end_time: str) -> timedelta:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        return end - start

    def calculate_total_working_hours_and_wage(self) -> Tuple[float, float]:
        total_wage = 0
        total_working_time = timedelta(0)

        for _date, shift in self.shifts.items():
            if shift == Shift.REST.value:
                continue

            date = datetime.strptime(_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            duration = self._calculate_shift_duration(
                self.shift_type[shift]["start_time"],
                self.shift_type[shift]["end_time"])
            total_working_time += duration

            if date in self.holidays:
                print(f"Date: {date} is a holiday, applying holiday rate.")
                total_wage += self._calculate_holiday_pay(duration)
            else:
                total_wage += self._calculate_overtime_pay(duration)

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
