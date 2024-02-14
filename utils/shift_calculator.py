import dataclasses
import functools
import json
import weakref
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


def memoized_method(*lru_args, **lru_kwargs):

    def decorator(func):

        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            @functools.lru_cache(*lru_args, **lru_kwargs)
            def cached_method(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)

            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    return decorator


@dataclasses.dataclass
class ShiftCalculator:
    shift_type_file: Path
    shift_file: Path
    holiday_file: Path
    hourly_rate: float

    def __post_init__(self) -> None:
        self.shift_type = self._load_json_file(self.shift_type_file)
        self.shifts = self._load_json_file(self.shift_file)
        self.shifts = {
            datetime.strptime(date, "%Y-%m-%d").date(): shift
            for date, shift in self.shifts.items()
        }

        self.holidays = self._load_json_file(self.holiday_file)
        self.holidays = [
            datetime.strptime(holiday, "%Y-%m-%d").date()
            for holiday in self.holidays.keys()
        ]

    @staticmethod
    def _load_json_file(file_path: Path) -> Dict[str, Any]:
        return json.loads(file_path.read_text())

    @memoized_method()
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
                return (8 *
                        self.hourly_rate) + (2 * self.hourly_rate * 1.33) + (
                            (overtime_hours - 2) * self.hourly_rate * 1.66)

    @staticmethod
    def _calculate_shift_duration(start_time: str, end_time: str) -> timedelta:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        return end - start

    def calculate_total_working_hours_and_wage(self) -> (float, float):
        total_wage = 0
        total_working_time = timedelta(0)

        for date, shift in self.shifts.items():
            if shift == "X":
                continue

            duration = self._calculate_shift_duration(
                self.shift_type[shift]["start_time"],
                self.shift_type[shift]["end_time"])
            total_working_time += duration

            if date in self.holidays:
                print(f"Date: {date} is a holiday")
                total_wage += duration.total_seconds(
                ) / 3600 * self.hourly_rate * 2
            else:
                total_wage += self.calculate_overtime_pay(duration)

        total_working_hours = round(total_working_time.total_seconds() / 3600,
                                    2)
        total_wage = round(total_wage, 2)

        return total_working_hours, total_wage

    def __str__(self) -> str:
        total_working_hours, total_salary = self.calculate_total_working_hours_and_wage(
        )
        return f"Total working hours: {total_working_hours}\nTotal salary: {total_salary}"


if __name__ == "__main__":
    calculator = ShiftCalculator(Path("./data/shift_type.json"),
                                 Path("./data/feb_shift.json"),
                                 Path("./data/holiday.json"), 190)
    print(calculator)
