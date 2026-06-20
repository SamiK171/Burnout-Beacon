from Employee import Employee
from Employee import Manager
# from typing import Optional
from Task import Task
from datetime import date

class Analytics:
    """Analytics tracker and calculator.

    Analyzes the relationship between an employee's mood, tasks completed and
    task difficulties/weights over a period of time to determine burnout risk.
    This is done through pattern recognition, change in trends, and the rates of
    change in variables such as mood, tasks completed and difficulties.

    === Private Attributes ===
    _employee: the Employee whose burnout risk is being determined.
    _mood_track: tracks weekly mood values
    _completed_tasks: tracks expected vs. actual completed tasks by date
    _task_weights: tracks weight of tasks based on date

    === Representation Invariants ===
    - the length of the list of weekly mood values in _mood_track must be
      less than or equal to 5.
    - len(_task_weights[date]) == len(_employee._tasks[date])
    """
    # _employee: Optional[Employee, Manager]
    _mood_track: dict[str, list]
    _completed_tasks: dict[date, dict[str, int]]
    _task_weights: dict[date, dict[Task, int]]

    def __init__(self):
        ...

    def _to_iso_week(self, date_str: str) -> str:
        dt = date.fromisoformat(date_str).isocalendar()
        return f"{dt.year}-W{dt.week:02d}"

    def _get_mood_vals(self, week_id: str, e: Employee) -> list[int]:
        """Helper method for mood ROC calculation.
        Returns list of mood values for a specific week.
        """
        moods = e.get_moods()
        vals = []
        for singular_date in moods:
            if self._to_iso_week(singular_date) == week_id:
                vals.append(moods[singular_date])
        return vals

    def _get_task_weights(self, week_id: str, e: Employee) -> dict[str, list[int]]:
        """Helper method for task weight ROC calculation."""
        tasks = e.get_tasks()
        weight_vals = {}
        for singular_date in tasks:
            if self._to_iso_week(singular_date) == week_id:
                for task in tasks[singular_date]:
                    weight_vals.setdefault(singular_date, []).append(task.get_weight())
        return weight_vals

    def _get_task_difficulties(self, week_id: str, e: Employee) -> dict[str, list[int]]:
        """Helper method for task difficulty ROC calculation."""
        tasks = e.get_tasks()
        difficulty_vals = {}
        for singular_date in tasks:
            if self._to_iso_week(singular_date) == week_id:
                for task in tasks[singular_date]:
                    difficulty_vals.setdefault(singular_date, []).append(task.get_difficulty())
        return difficulty_vals

    def calculate_mood_ROC(self):
        """Calculate the rate of change in a employee's mood
        over time."""

    def calculate_task_comp_ROC(self):
        """Calculate the rate of change in an employee's task
        completion over time."""

    def calculate_weight_ROC(self):
        """Calculate the rate of change in the weight of an
        employee's tasks over time."""
