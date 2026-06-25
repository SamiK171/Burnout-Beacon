from Employee import Employee
from Employee import Manager
# from typing import Optional
from Task import Task
from datetime import date
import numpy as np
import pandas as pd

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

    def _get_task_completed_expected_ratio(self, week_id: str, e: Employee) -> list[float]:
        """Helper method for task completion ROC calculation."""
        tasks = e.get_tasks()
        ratios = []
        completed = 0
        for singular_date in tasks:
            if self._to_iso_week(singular_date) == week_id:
                for task in tasks[singular_date]:
                    if task.completed:
                        completed += 1
                ratios.append(completed / len(tasks[singular_date]))
                completed = 0
        return ratios

    def _merge_lists(self, info: dict[str, list[int]]) -> list[int]:
        """Return merged lists from <info>."""
        merged = []
        for key in info:
            merged.append(sum(info[key]))
        return merged

    def _volatility_measurement(self, l: list) -> str:
        """Measures the volatility of the list <l>.
        Adaptable to any list containing mood values or task weights, etc.
        """

        if len(l) < 2:
            return "Insufficient data."

        arr = np.array(l)
        volatility_score = np.std(arr) / np.average(arr)
        # Co-Efficient of Variation (Standard Deviation / Average)
        threshold = 0.25 # 25% threshold.

        if volatility_score > threshold:
            return "High Volatility"
        else:
            return "Low/Stable Volatility"

    def _trend_shift(self, l: list) -> str:
        """Calculates the trend shift of the list <l>.
        Determines whether it is increasing, decreasing
        or stable."""
        if len(l) < 2:
            return "Insufficient data."
        arr = np.array(l)
        smoothed_data = pd.Series(arr).ewm(span=3, adjust=False).mean().to_numpy()

        percentage_shift = (smoothed_data[-1] - smoothed_data[0]) / smoothed_data[0]
        jumps = np.diff(smoothed_data)
        pos_ratio = np.sum(jumps > 0) / len(jumps)

        score = 0
        if percentage_shift > 0.10:
            score += 1
        elif percentage_shift < -0.10:
            score -= 1

        if pos_ratio > 0.55:
            score += 1
        elif pos_ratio < 0.45:
            score -= 1

        if score >= 1:
            return "Increasing Trend"
        elif score <= -1:
            return "Decreasing Trend"
        else:
            return "Stable Trend"

    def _mood_analyzer(self, vol: str, trend: str) -> list[str]:
        """Analyze mood and return observations."""
        results = []

        if vol == "High Volatility":
            results.append("Fluctuating & Inconsistent Mood")

        if vol == "Low/Stable Volatility":
            results.append("Minimal Change in Mood")

        if trend == "Increasing Trend":
            results.append("Improving Mood")

        if trend == "Decreasing Trend":
            results.append("Declining Mood")

        if trend == "Stable Trend":
            results.append("Consistent Mood")

        return results

    def _weight_analyzer(self, vol: str, trend: str) -> list[str]:
        """Analyze weights and return observations."""
        results = []

        if vol == "High Volatility":
            results.append("Fluctuating & Inconsistent Workload Importance")

        if vol == "Low/Stable Volatility":
            results.append("Minimal Change in Workload Importance")

        if trend == "Increasing Trend":
            results.append("Increasing Workload Importance")

        if trend == "Decreasing Trend":
            results.append("Decreasing Workload Importance")

        if trend == "Stable Trend":
            results.append("Consistent Workload Importance")

        return results

    def _diff_analyzer(self, vol: str, trend: str) -> list[str]:
        """Analyze difficulties and return observations."""
        results = []

        if vol == "High Volatility":
            results.append("Fluctuating & Inconsistent Workload Difficulty")

        if vol == "Low/Stable Volatility":
            results.append("Minimal Change in Workload Difficulty")

        if trend == "Increasing Trend":
            results.append("Increasing Workload Difficulty")

        if trend == "Decreasing Trend":
            results.append("Decreasing Workload Difficulty")

        if trend == "Stable Trend":
            results.append("Consistent Workload Difficulty")

        return results

    def _comp_analyzer(self, vol: str, trend: str) -> list[str]:
        """Analyze completion and return observations."""
        results = []

        if vol == "High Volatility":
            results.append("Fluctuating & Inconsistent Task Completion")

        if vol == "Low/Stable Volatility":
            results.append("Minimal Change in Task Completion")

        if trend == "Increasing Trend":
            results.append("Increase in Task Completion")

        if trend == "Decreasing Trend":
            results.append("Declining Task Completion")

        if trend == "Stable Trend":
            results.append("Consistent Task Completion")

        return results

    def total_analyzer(self, e: Employee, week_id: str) -> str:
        """Produces a verdict based on employee data."""
        mood_analysis = self._mood_analyzer(vol=self._volatility_measurement(self._get_mood_vals(week_id, e)),
                                            trend=self._trend_shift(self._get_mood_vals(week_id, e)))
        weight_analysis = self._weight_analyzer(vol=self._volatility_measurement(self._merge_lists(self._get_task_weights(week_id, e))),
                                            trend=self._trend_shift(self._merge_lists(self._get_task_weights(week_id, e))))
        diff_analysis = self._diff_analyzer(
            vol=self._volatility_measurement(self._merge_lists(self._get_task_difficulties(week_id, e))),
            trend=self._trend_shift(self._merge_lists(self._get_task_difficulties(week_id, e))))
        comp_analysis = self._comp_analyzer(vol=self._volatility_measurement(self._get_task_completed_expected_ratio(week_id, e)),
                                            trend=self._trend_shift(self._get_task_completed_expected_ratio(week_id, e)))

        summary = [mood_analysis, weight_analysis, diff_analysis, comp_analysis]
        report = f"{e.name}'s Burnout Diagnostic Report: \n"

        for individual_summary in summary:
            for info in individual_summary:
                if individual_summary == mood_analysis:
                    if info == mood_analysis[0]:
                        report += "Mood Diagnostic: \n"
                        report += f"{info}\n"
                    else:
                        report += f"{info}\n"
                        report += "---------- \n"
                elif individual_summary == weight_analysis:
                    if info == weight_analysis[0]:
                        report += "Task Weight Diagnostic: \n"
                        report += f"{info}\n"
                    else:
                        report += f"{info}\n"
                        report += "---------- \n"
                elif individual_summary == diff_analysis:
                    if info == diff_analysis[0]:
                        report += "Task Difficulty Diagnostic: \n"
                        report += f"{info}\n"
                    else:
                        report += f"{info}\n"
                        report += "---------- \n"
                else:
                    if info == comp_analysis[0]:
                        report += "Task Completion Diagnostic: \n"
                        report += f"{info}\n"
                    else:
                        report += f"{info}\n"
                        report += "---------- \n"
        return report
