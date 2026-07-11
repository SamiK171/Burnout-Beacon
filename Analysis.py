from Employee import Employee
from Employee import Manager
# from typing import Optional
from Task import Task
from datetime import date, timedelta
import numpy as np
import pandas as pd

class Analysis:
    """The analysis engine.

    Process:
    1) Extraction:
       - Extracts employee data over timeframe (mood, task difficulties, weights and completion)
    2) Environment:
       - Measures overall value ranges (are the values overall low, high, or mixed)?
       - Determines how to deal with data going forward
    3) Volatility (Chaos):
       - Measures volatility in values (are they fluctuating or consistent)?
    4) Direction (Trend):
       - Determines the direction values are going in (increasing, decreasing, or stable)?
    5) Result Construction:
      - Uses environment, volatility and trend to produce verdicts regarding burnout risk
      for the employee within the desired timeframe.
    """

    def __init__(self):

        # Output Matrix's
        self.week_matrix = {} # Weekly Timeframe (7 days or less)
        self.month_matrix = {} # Monthly Timeframe (31 days or less)
        self.year_matrix = {} # Yearly Timeframe (365 days or less)

    # Miscellaneous
    def _to_iso_week(self, date_str: str) -> str:
        dt = date.fromisoformat(date_str).isocalendar()
        return f"{dt.year}-W{dt.week:02d}"

    def iso_week_to_date_range(self, year: int, week: int):
        # ISO week: Monday is start of week
        start = date.fromisocalendar(year, week, 1)  # Monday
        end = start + timedelta(days=6)

        return start.isoformat(), end.isoformat()

    # Step 1: Extraction:

    def _get_mood_vals(self, period: str, e: Employee, period_type: str) -> list[int]:
        """Helper method for mood ROC calculation.
        Returns list of mood values for a specific week.
        """
        moods = e.get_moods()
        vals = []
        if period_type == "week":
            for singular_date in moods:
                if self._to_iso_week(singular_date) == period:
                    vals.append(moods[singular_date])
        elif period_type == "month":
            for singular_date in moods:
                if singular_date[:7] == period:
                    vals.append(moods[singular_date])
        elif period_type == "year": # year
            for singular_date in moods:
                if singular_date[:4] == period:
                    vals.append(moods[singular_date])
        return vals

    def _get_task_weights(self, period: str, e: Employee, period_type: str) -> dict[str, list[int]]:
        """Helper method for task weight ROC calculation."""
        tasks = e.get_tasks()
        weight_vals = {}

        if period_type == "week":
            for singular_date in tasks:
                if self._to_iso_week(singular_date) == period:
                    for task in tasks[singular_date]:
                        weight_vals.setdefault(singular_date, []).append(task.get_weight())
        elif period_type == "month":
            for singular_date in tasks:
                if singular_date[:7] == period:
                    for task in tasks[singular_date]:
                        weight_vals.setdefault(singular_date, []).append(task.get_weight())
        elif period_type == "year":
            for singular_date in tasks:
                if singular_date[:4] == period:
                    for task in tasks[singular_date]:
                        weight_vals.setdefault(singular_date, []).append(task.get_weight())
        return weight_vals

    def _get_task_difficulties(self, period: str, e: Employee, period_type: str) -> dict[str, list[int]]:
        """Helper method for task difficulty ROC calculation."""
        tasks = e.get_tasks()
        difficulty_vals = {}

        if period_type == "week":
            for singular_date in tasks:
                if self._to_iso_week(singular_date) == period:
                    for task in tasks[singular_date]:
                        difficulty_vals.setdefault(singular_date, []).append(task.get_difficulty())
        elif period_type == "month":
            for singular_date in tasks:
                if singular_date[:7] == period:
                    for task in tasks[singular_date]:
                        difficulty_vals.setdefault(singular_date, []).append(task.get_difficulty())
        elif period_type == "year":
            for singular_date in tasks:
                if singular_date[:4] == period:
                    for task in tasks[singular_date]:
                        difficulty_vals.setdefault(singular_date, []).append(task.get_difficulty())
        return difficulty_vals

    def _get_task_completed_expected_ratio(self, period: str, e: Employee, period_type: str) -> list[float]:
        """Helper method for task completion ROC calculation."""
        tasks = e.get_tasks()
        ratios = []
        completed = 0

        if period_type == "week":
            for singular_date in tasks:
                if self._to_iso_week(singular_date) == period:
                    for task in tasks[singular_date]:
                        if task.completed:
                            completed += 1
                    ratios.append(completed / len(tasks[singular_date]))
                    completed = 0
        elif period_type == "month":
            for singular_date in tasks:
                if singular_date[:7] == period:
                    for task in tasks[singular_date]:
                        if task.completed:
                            completed += 1
                    ratios.append(completed / len(tasks[singular_date]))
        elif period_type == "year":
            for singular_date in tasks:
                if singular_date[:4] == period:
                    for task in tasks[singular_date]:
                        if task.completed:
                            completed += 1
                    ratios.append(completed / len(tasks[singular_date]))
        return ratios

    def merge_diff(self, info: dict[str, list[int]]) -> list[int]:
        """Returns a list of max difficulties over the timeframe."""
        max_diffs = []
        for key in info:
            max_diffs.append(max(info[key]))
        return max_diffs

    def merge_weights(self, info: dict[str, list[int]]) -> list[int]:
        """Return merged lists with weights accumulated from <info>."""
        merged = []
        for key in info:
            merged.append(sum(info[key]))
        return merged

    # Step 2: Environment:

    def mood_environment(self, data: list[int]) -> str:
        """Calculates the mood environment of <data>.

        Mood environment is determined by which
        mood type takes over 60% of the timeframe.
        Range:
        1 - 4: Low Mood
        5 - 6: Decent Mood
        7 - 10: High Mood

        """
        low, decent, high = [], [], []
        for val in data:
            if 1 <= val <= 4:
                low.append(val)
            elif 5 <= val <= 6:
                decent.append(val)
            else:
                high.append(val)

        if len(low) / len(data) >= 0.6:
            return "LM" # Low Moods
        elif len(decent) / len(data) >= 0.6:
            return "DM" # Decent Moods
        elif len(high) / len(data) >= 0.6:
            return "GM" # Good Moods
        return "MM" # Mixed Moods

    def completion_environment(self, data: list[int] | list[float]) -> str:
        """Calculates the completion environment of <data>.

        Completion environment is determined by which
        completion type takes over 60% of the timeframe.
        Range:
        <= 50%: Low Completion
        > 50%: Good Completion
        """
        low, good = [], []
        for val in data:
            if val <= 0.5:
                low.append(val)
            else:
                good.append(val)

        if len(low) / len(data) >= 0.6:
            return "LC" # Low Completion
        elif len(good) / len(data) >= 0.6:
            return "GC" # Good Completion
        return "MC" # Mixed Competition

    def weight_environment(self, data: list[int]) -> str:
        """Calculates the weight environment of <data>.

        Range:
        Weekly: 1 day greater than 35: High Weight
        Monthly: 5 days greater than 35: High Weight
        Yearly: 100 days greater than 35: High Weight
        """
        counter = []

        if len(data) <= 7: # Weekly
            for val in data:
                if val >= 35:
                    return "HW" # High Weight
        elif 7 < len(data) <= 31: # Monthly
            for val in data:
                if val >= 35: counter.append(val)
            if len(counter) >= 5:
                return "HW"
        else:
            for val in data:
                if val >= 35: counter.append(val)
            if len(counter) >= 100:
                return "HW"
        return "LW" # Low Weight


    def diff_environment(self, data: list[int]) -> str:
        """Calculates the diff environment of <data>.

        Range:
        Weekly: 1 day greater than 15: High Weight
        Monthly: 5 days greater than 15: High Weight
        Yearly: 100 days greater than 15: High Weight
        """
        counter = []

        if len(data) <= 7:  # Weekly
            for val in data:
                if val > 8:
                    return "HD"  # High Difficulty
        elif 7 < len(data) <= 31:  # Monthly
            for val in data:
                if val > 8: counter.append(val)
            if len(counter) >= 5:
                return "HD"
        else:
            for val in data:
                if val > 8: counter.append(val)
            if len(counter) >= 100:
                return "HD"
        return "LD"  # Low Difficulty

    # Step 3: Volatility:

    def average_calculator(self, data: list[int] | list[float]) -> float:
        """Calculate the average of <data>."""
        return sum(data) / len(data)

    def mad_calculator(self, data: list[int] | list[float]) -> float:
        """Calculate the mean absolute deviation of <data>."""
        mad = 0
        avg = self.average_calculator(data)
        for val in data:
            mad += abs(val - avg)
        return mad / len(data)

    def mood_volatility(self, data: list[int] | list[float]) -> str:
        """Calculate the volatility of <data>.

        <data> contains mood values or task completion values
        over timeframe.
        """
        data_mad = self.mad_calculator(data)
        if data_mad > 1.5:
            return "HV" # High Volatility
        else:
            return "LV" # Low Volatility

    def comp_volatility(self, data: list[int] | list[float]) -> str:
        """Calculate the volatility of <data>.

        <data> contains task completion values
        over timeframe.
        """
        data_mad = self.mad_calculator(data)
        if data_mad > 0.15:
            return "HV" # High Volatility
        else:
            return "LV" # Low Volatility

    def task_weight_volatility(self, data: list[int]) -> str:
        """Calculate the volatility of <data>.

        <data> contains task weight values over timeframe.
        """
        data_mad = self.mad_calculator(data)
        if data_mad > 5.0:
            return "HV" # High Volatility
        else:
            return "LV" # Low Volatility

    def task_diff_volatility(self, data: list[int]) -> str:
        """Calculate the volatility of <data>.

        <data> contains task difficulty values over timeframe.
        """
        data_mad = self.mad_calculator(data)
        if data_mad > 1.0:
            return "HV"  # High Volatility
        else:
            return "LV"  # Low Volatility

    # Step 4: Direction:

    def window_average(self, data: list[int] | list[float]) -> float:
        """Calculate the window average of <data>.

        Average = (40% of the end points) - (40% of the start points)
        # of end & start points differ based on the timeframe.
        """
        length = len(data)
        window_size = max(1, int(length * 0.40))

        start_window, end_window = data[:window_size], data[window_size:]
        start_avg, end_avg = sum(start_window) / len(start_window), sum(end_window) / len(end_window)

        shift_calc = end_avg - start_avg
        return shift_calc

    def mood_diff_direction(self, data: list[int]) -> str:
        """Calculate the mood or difficulty direction of <data>."""
        if self.window_average(data) > 0.5:
            return "UP"
        else:
            return "DOWN"

    def comp_direction(self, data: list[float]) -> str:
        """Calculate the comp direction of <data>."""
        if self.window_average(data) > 0.10:
            return "UP"
        else:
            return "DOWN"

    def weight_direction(self, data: list[int]) -> str:
        """Calculate the weight direction of <data>."""
        if self.window_average(data) > 3.0:
            return "UP"
        else:
            return "DOWN"

    # Step 5: Result Construction:
