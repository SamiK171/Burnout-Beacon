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
    5) Score Calculation:
      - Calculates scores of employee's data based on different weights and values.
    6) Case-Based Matching:
      - Matches employee data to a specific burnout case. If the case is not matched,
      emphasis is put on the employee's stats score with custom interpretation needed
    7) Result Construction:
      - Produces a final verdict composed of the employee's burnout score and burnout
      case (if met)
    """

    def __init__(self):

        # Risk Scoring Matrix:
        self._score_matrix = {
            "Global Weights": {
                "ENV": 0.45, "VOL": 0.35, "DIR": 0.20
            },
            "Environmental Points": {
                "LM": 10, "MM": 5, "HM": 1,
                "LC": 9, "MC": 4, "HC": 1,
                "HW": 10, "MW": 5, "LW": 2,
                "HD": 8, "MD": 4, "LD": 2,
            },
            "Volatility Points": {
                "HV": 10, "MV": 5 , "LV": 2},
            "Internal Direction Points": {
                "UP": 1, "FLAT": 4, "DOWN": 10
             },
            "External Direction Points":
                {
                    "UP": 10, "FLAT": 4, "DOWN": 1
                }
        }

        # Output Matrix's
        self.week_matrix = {} # Weekly Timeframe (7 days or less)
        self.month_matrix = {} # Monthly Timeframe (31 days or less)
        self.year_matrix = {} # Yearly Timeframe (365 days or less)

    # Miscellaneous:

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
        5 - 6: Moderate Mood
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
            return "MM" # Moderate Moods
        elif len(high) / len(data) >= 0.6:
            return "HM" # Good Moods
        return "MM" # Moderate Moods (fallback)

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
            return "HC" # High Completion
        return "MC" # Moderate Competition

    def weight_environment(self, data: list[int]) -> str:
        """Calculates the weight environment of <data>.

        Weekly Range:

        High:
        1 day greater than 35 => High Weight
        Weekly Average >= 25 => High Weight

        Moderate:
        Weekly Average >= 15 and <= 24 => Moderate Weight

        Low:
        Weekly Average < 15 => Low Weight

        """
        weekly_avg = sum(data) / len(data)

        for val in data:
            if val >= 35:
                return "HW" # High Weight

        if weekly_avg >= 35: # in the case that no day weight >= 35
            return "HW"
        elif 20 <= weekly_avg <= 34:
            return "MW" # Moderate Weight
        return "LW" # Low Weight

    def diff_environment(self, data: list[int]) -> str:
        """Calculates the diff environment of <data>.

        Range:

        Weekly Average >= 8 => High Difficulty
        5 <= Weekly Average <= 7 => Moderate Difficulty
        Weekly Average < 5 => Low Difficulty

        """
        weekly_avg = sum(data) / len(data)

        if weekly_avg >= 8:
            return "HD"
        elif 5 <= weekly_avg <= 7:
            return "MD" # Moderate Difficulty
        return "LD" # Low Difficulty

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

    def mas_calculator(self, data: list[int] | list[float]) -> float:
        """Calculate the mean absolute step of <data>."""
        n = len(data)
        count = 0
        for i in range(n - 1):
            count += abs(data[i + 1] - data[i])
        return (1 / (n - 1)) * count


    def mood_volatility(self, data: list[int] | list[float]) -> str:
        """Calculate the volatility of <data>.

        <data> contains mood values or task completion values
        over timeframe.
        """
        data_mas = self.mas_calculator(data)
        if data_mas > 2.5:
            return "HV" # High Volatility
        elif 1.2 <= data_mas <= 2.5:
            return "MV" # Moderate Volatility
        else:
            return "LV" # Low Volatility

    def comp_volatility(self, data: list[int] | list[float]) -> str:
        """Calculate the volatility of <data>.

        <data> contains task completion values
        over timeframe.
        """
        data_mas = self.mas_calculator(data)
        if data_mas > 0.35:
            return "HV" # High Volatility
        elif 0.15 <= data_mas <= 0.35:
            return "MV" # Moderate Volatility
        else:
            return "LV" # Low Volatility

    def task_weight_volatility(self, data: list[int]) -> str:
        """Calculate the volatility of <data>.

        <data> contains task weight values over timeframe.
        """
        data_mas = self.mas_calculator(data)
        # relative_mad = (data_mad / (len(data) / sum(data))) * 100
        if data_mas > 6.0:
            return "HV" # High Volatility
        elif 3.0 <= data_mas <= 6.0:
            return "MV" # Moderate Volatility
        else:
            return "LV" # Low Volatility

    def task_diff_volatility(self, data: list[int]) -> str:
        """Calculate the volatility of <data>.

        <data> contains task difficulty values over timeframe.
        """
        data_mas = self.mas_calculator(data)
        if data_mas > 1.8:
            return "HV"  # High Volatility
        elif 0.8 <= data_mas <= 1.8:
            return "MV" # Moderate Volatility
        else:
            return "LV"  # Low Volatility

    # Step 4: Direction:

    def window_average(self, data: list[int] | list[float]) -> float:
        """Calculate the window average of <data>.

        Average = (40% of the end points) - (40% of the start points)
        # of end & start points differ based on the timeframe.
        """

        if not data:
            return 0.0

        length = len(data)
        window_size = max(1, int(length * 0.40))

        start_window, end_window = data[:window_size], data[-window_size:]
        start_avg, end_avg = sum(start_window) / len(start_window), sum(end_window) / len(end_window)

        shift_calc = end_avg - start_avg
        return shift_calc

    def mood_diff_direction(self, data: list[int]) -> str:
        """Calculate the mood or difficulty direction of <data>."""
        if self.window_average(data) > 0.5:
            return "UP"
        elif -0.5 < self.window_average(data) < 0.5:
            return "FLAT"
        else:
            return "DOWN"

    def comp_direction(self, data: list[float]) -> str:
        """Calculate the comp direction of <data>."""
        if self.window_average(data) > 0.10:
            return "UP"
        elif -0.10 < self.window_average(data) < 0.10:
            return "FLAT"
        else:
            return "DOWN"

    def weight_direction(self, data: list[int]) -> str:
        """Calculate the weight direction of <data>."""
        if self.window_average(data) > 3.0:
            return "UP"
        elif -3.0 < self.window_average(data) < 3.0:
            return "FLAT"
        else:
            return "DOWN"

    # Step 5: Score Calculation:

    def develop_employee_state(self, e: Employee, period: str, period_type: str) -> tuple:
        """Construct the employee state for employee <e>.

        Returns a multi-layered 12-property tuple in the format (env, vol, dir)
        for each employee quality (mood, completion, weight, difficulty).
        """
        moods = self._get_mood_vals(period=period, e=e, period_type=period_type)
        comp = self._get_task_completed_expected_ratio(period=period, e=e, period_type=period_type)
        weights = self.merge_weights(self._get_task_weights(period=period, e=e, period_type=period_type))
        diff = self.merge_diff(self._get_task_difficulties(period=period, e=e, period_type=period_type))

        mood_env, mood_vol, mood_dir = self.mood_environment(moods), self.mood_volatility(moods), self.mood_diff_direction(moods)
        comp_env, comp_vol, comp_dir = self.completion_environment(comp), self.comp_volatility(comp), self.comp_direction(comp)
        weight_env, weight_vol, weight_dir = self.weight_environment(weights), self.task_weight_volatility(weights), self.weight_direction(weights)
        diff_env, diff_vol, diff_dir = self.diff_environment(diff), self.task_diff_volatility(diff), self.mood_diff_direction(diff)

        return (
        (mood_env, mood_vol, mood_dir),
        (comp_env, comp_vol, comp_dir),
        (weight_env, weight_vol, weight_dir),
        (diff_env, diff_vol, diff_dir),
        )

    def _calculate_mood_score(self, state: tuple) -> float:
        """Calculate the mood score of <state>."""
        env = self._score_matrix["Environmental Points"][state[0][0]] * self._score_matrix["Global Weights"]["ENV"]
        vol = self._score_matrix["Volatility Points"][state[0][1]] * self._score_matrix["Global Weights"]["VOL"]
        direction = self._score_matrix["Internal Direction Points"][state[0][2]] * self._score_matrix["Global Weights"]["DIR"]
        return env + vol + direction

    def _calculate_comp_score(self, state: tuple) -> float:
        """Calculate the comp score of <state>."""
        env = self._score_matrix["Environmental Points"][state[1][0]] * self._score_matrix["Global Weights"]["ENV"]
        vol = self._score_matrix["Volatility Points"][state[1][1]] * self._score_matrix["Global Weights"]["VOL"]
        direction = self._score_matrix["Internal Direction Points"][state[1][2]] * self._score_matrix["Global Weights"][
            "DIR"]
        return env + vol + direction

    def _calculate_weight_score(self, state: tuple) -> float:
        """Calculate the weight score of <state>."""
        env = self._score_matrix["Environmental Points"][state[2][0]] * self._score_matrix["Global Weights"]["ENV"]
        vol = self._score_matrix["Volatility Points"][state[2][1]] * self._score_matrix["Global Weights"]["VOL"]
        direction = self._score_matrix["External Direction Points"][state[2][2]] * self._score_matrix["Global Weights"][
            "DIR"]
        return env + vol + direction

    def _calculate_diff_score(self, state: tuple) -> float:
        """Calculate the diff score of <state>."""
        env = self._score_matrix["Environmental Points"][state[3][0]] * self._score_matrix["Global Weights"]["ENV"]
        vol = self._score_matrix["Volatility Points"][state[3][1]] * self._score_matrix["Global Weights"]["VOL"]
        direction = self._score_matrix["External Direction Points"][state[3][2]] * self._score_matrix["Global Weights"][
            "DIR"]
        return env + vol + direction

    def _sum_burnout_score(self, state: tuple) -> float:
        """Calculate the sum burnout score of <state>.
        """
        mood_score = self._calculate_mood_score(state)
        comp_score = self._calculate_comp_score(state)
        weight_score = self._calculate_weight_score(state)
        diff_score = self._calculate_diff_score(state)
        return mood_score + comp_score + weight_score + diff_score

    def _get_score_category(self, score: float) -> str:
        if score <= 12.0:
            return f"OPTIMAL BASELINE: Burnout Score {round(score, 2)}/40.0"
        elif score <= 20.0:
            return f"SUSTAINABLE OPERATIONS: Burnout Score {round(score, 2)}/40.0"
        elif score <= 28.0:
            return f"ELEVATED WORKLOAD STRAIN: Burnout Score {round(score, 2)}/40.0"
        elif score <= 34.0:
            return f"HIGH OPERATIONAL STRESS: Burnout Score {round(score, 2)}/40.0"
        else:
            return f"CRITICAL STRAIN THRESHOLD: Burnout Score {round(score, 2)}/40.0"

    # Step 6: Case-Based Matching:

    def evaluate_case(self, state: tuple) -> str:
        """Evaluate the weekly case matrix for the employee based on their <state>."""

        # CASE 1: High-Output Exhaustion:
        if 'LM' in state[0] and 'DOWN' in state[0]: # Low Mood & Downward Mood Direction
            if ('MC' in state[1] or 'GC' in state[1]) and 'UP' in state[1]: # Moderate/Good Completion & Upward Completion Direction
                return ("HIGH-OUTPUT EXHAUSTION:"
                        "High work output is consistent during collapsing emotional state.")

        # CASE 2: Clinical Depletion:
        if 'LM' in state[0] and 'DOWN' in state[0]: # Low & Downward Mood
            if 'LC' in state[1] and 'DOWN' in state[1]: # Low & Downward
                return ("CLINICAL DEPLETION:"
                        "Workload effectiveness & productivity depletes as emotional state crumbles.")

        # CASE 3: Quiet Quitting / Loss of Interest:
        if 'LM' in state[0] and 'LV' in state[0] and 'FLAT' in state[0]: # Consistent low mood
            if 'LC' in state[1] and 'LV' in state[1] and 'FLAT' in state[1]: # Consistent low completion
                if 'LW' in state[2] or 'MW' in state[2]: # Low or moderate workload
                    if 'LD' in state[3] or 'MD' in state[3]: # Low or moderate difficulty
                        return ("LOSS OF INTEREST:"
                                "Consistent low emotional state with low work completion despite"
                                "reasonable workload and difficulty indicates interest detachment from work.")

        # CASE 4: Structural Overload:
        if 'DOWN' in state[1]: # Downward Completion
            if 'HW' in state[2] and 'UP' in state[2]: # Increasing and High Workload
                if 'HD' in state[3] and 'UP' in state[3]: # Increasing and High Difficulty
                    return ("STRUCTURAL OVERLOAD:"
                            "Task volume and complexity accelerating as output declines.")

        # CASE 5: Complexity Blockade:
        if 'MM' in state[0] or 'LM' in state[0]: # Medium to Low Mood
            if 'LC' in state[1] and 'DOWN' in state[1]: # Downwards and Low Completion
                if 'LW' in state[2] or 'MW' in state[2]: # Low-to-Moderate Workload
                    if 'HD' in state[3] and 'UP' in state[3]: # Increasing and High Difficulty
                        return ("COMPLEXITY BLOCKADE:"
                                "Task volume remains stable but task complexity halts effective output."
                                "")

        # CASE 6: Optimal High-Capacity State:
        if 'HM' in state[0] and ('LV' in state[0] or 'MV' in state[0]):
            if 'HC' in state[1] and ('UP' in state[1] or 'FLAT' in state[1]):
                if 'MW' in state[2] or 'HW' in state[2]:
                    if 'MD' in state[3] or 'HD' in state[3]:
                        return ("OPTIMAL HIGH-CAPACITY STATE:"
                                "High-output under challenging work supported by high emotional resilience"
                                "and low daily volatility.")

        # CASE 7: Fallback Case:
        return "GENERAL OPERATIONAL LOAD: No acute operational patterns detected."

    # Step 7: Result Construction:

    def deliver_report(self, e: Employee, period: str, period_type: str) -> str:
        """Deliver the final burnout report for employee <e> based on their
        burnout score and case."""
        employee_state = self.develop_employee_state(e, period, period_type)
        burnout_score = self._get_score_category(self._sum_burnout_score(employee_state))
        burnout_case = self.evaluate_case(employee_state)
        return burnout_score + "\n" + burnout_case
