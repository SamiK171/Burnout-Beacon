from Employee import Employee
from Employee import Manager
from typing import Optional
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
    _employee: Optional[Employee, Manager]
    _mood_track: dict[str, list]
    _completed_tasks: dict[date, dict[str, int]]
    _task_weights: dict[date, dict[Task, int]]

    def __init__(self):
        ...

    def calculate_mood_ROC(self):
        """Calculate the rate of change in a employee's mood
        over time."""

    def calculate_task_comp_ROC(self):
        """Calculate the rate of change in an employee's task
        completion over time."""

    def calculate_weight_ROC(self):
        """Calculate the rate of change in the weight of an
        employee's tasks over time."""
