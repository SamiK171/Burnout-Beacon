import pytest
from Employee import Employee, Manager
from Task import Task
from Analytics import Analytics
from Loader import Loader
from Storage import Storage
from datetime import date

class Testing:
    """The testing suite.

     This class focuses on testcases ensuring implementation is meeting expectations.
    Standard cases, edge cases, and property-based testing are all covered.
     """

    def test_all(self):
        """Placeholder for all tests."""
        pass

    class TestObjectConstruction:
        def test_employee_builder(self):
            """Test if an employee can be built from a JSON file."""
            storage = Storage('employee_info.json')
            assert storage.get_employee('E1001').name == 'Jim Halpert'
            assert storage.get_employee('E1002').name == 'Dwight Schrute'
            assert storage.get_employee('E1001')._moods['2026-05-23'] == 7

    class TestMoodRater:
        def test_mood_rater_success(self):
            """Test if an employee can properly rate their mood for the current day.

            The current day as of testing is '06-18-26'
            """
            s = Storage('employee_info.json')
            m = Manager('Michael Scott', 'E0067')
            jim = s.get_employee('E1001')
            t = Task('Prank Dwight', 10, 10, str(date.today()), False)
            m.add_task(t, jim, str(date.today()))
            jim.rate_mood(9)
            assert jim.get_specific_mood(str(date.today())) == 9

        def test_mood_rater_no_task(self):
            """Test the case where an employee tries to rate their mood, despite not
            having task(s) for that day. This implies that the employee was essentially
            absent that day."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            jim.rate_mood(9)
            assert jim.get_specific_mood(str(date.today())) is None

        def test_mood_rater_day_exists(self):
            """Test the case where an employee tries to rate their mood, yet they have
            already rated their mood for that day. Note that employees rate their mood
            before clocking off for work, so rating after the shift is over cannot work."""
            s = Storage('employee_info.json')
            m = Manager('Michael Scott', 'E0067')
            jim = s.get_employee('E1001')
            t = Task('Prank Dwight', 10, 10, str(date.today()), False)
            m.add_task(t, jim, str(date.today()))
            jim.rate_mood(9)
            jim.rate_mood(4)
            assert jim.get_specific_mood(str(date.today())) == 9 # no change

    class TestTaskCRUD:
        def test_add_task_success(self):
            """Test a manager adding a task for an employee."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('Michael Scott', 'E0067')
            t = Task('Raid Utica', 10, 10, str(date.today()), False)
            m.add_task(t, jim, str(date.today()))
            jim_tasks = jim.get_tasks()
            assert t in jim_tasks[str(date.today())]

        def test_add_task_fail(self):
            """Test a manager adding a duplicate task for an employee"""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('Michael Scott', 'E0067')
            t1 = Task('Raid Utica', 10, 10, str(date.today()), False)
            m.add_task(t1, jim, str(date.today()))
            t2 = Task('Raid Utica', 10, 10, str(date.today()), False)
            m.add_task(t2, jim, str(date.today()))
            jim_tasks = jim.get_tasks()
            assert t1 in jim_tasks[str(date.today())]
            assert t2 not in jim_tasks[str(date.today())] # no duplicate exists


        def test_remove_task(self):
            """Test a manager removing a task for an employee."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('Michael Scott', 'E0067')
            #pre-removal:
            assert jim.get_specific_task('2026-05-23', 'Client Outreach') is not None
            m.remove_task('Client Outreach', jim, '2026-05-23')
            #post-removal:
            assert jim.get_specific_task('2026-05-23', 'Client Outreach') is None

        def test_change_task(self):
            """Test a manager changing a task for an employee."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('Michael Scott', 'E0067')
            task = jim.get_specific_task('2026-05-23', 'Client Outreach')
            # pre-change:
            assert task.name == 'Client Outreach'
            assert task.get_weight() == 9
            assert task.get_difficulty() == 6
            m.change_task('Client Outreach', jim, '2026-05-23', 'Contact Leads',
                          8, 8)
            # post-change:
            assert task.name == 'Contact Leads'
            assert task.get_weight() == 8
            assert task.get_difficulty() == 8

    class TestAnalyticsDataRetrieval:
        def test_mood_value_retrieval(self):
            """Test the helper method which retrieves mood values for a specific week.
            Weeks are ISO-based.
            """
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            assert a._get_mood_vals('2026-W21', jim, 'week') == [7, 4]
            assert a._get_mood_vals('2026-W22', jim, 'week') == [6, 3, 8, 4, 9]

        def test_task_weight_value_retrieval(self):
            """Test the helper method which retrieves task weights for a specific week.
            Weeks are ISO-based.
            """
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            assert (a._get_task_weights('2026-W21', jim, 'week') ==
                    {"2026-05-23": [9, 6], "2026-05-24": [8, 4]})
            assert (a._get_task_weights('2026-W22', jim, 'week') ==
                    {'2026-05-25': [3, 5],
                     '2026-05-26': [8, 4],
                     '2026-05-27': [7, 10, 5],
                     '2026-05-28': [9, 10, 5],
                     '2026-05-29': [4, 10, 8]})

        def test_task_diff_value_retrieval(self):
            """Test the helper method which retrieves task difficulties for a specific week.
            Weeks are ISO-based.
            """
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            assert (a._get_task_difficulties('2026-W21', jim, 'week') ==
                    {"2026-05-23": [6, 7], "2026-05-24": [6, 7]})
            assert (a._get_task_difficulties('2026-W22', jim, 'week') ==
                    {'2026-05-25': [6, 7],
                     '2026-05-26': [6, 8],
                     '2026-05-27': [2, 8, 3],
                     '2026-05-28': [3, 10, 2],
                     '2026-05-29': [3, 10, 7]})
        def test_task_comp_ratio(self):
            """Test task completion to task expected ratio."""
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            # assert a._get_task_completed_expected_ratio('2026-W21', jim) == 0.75 #3/4
            # assert a._get_task_completed_expected_ratio('2026-W22', jim) == 0.50 #2/4
            assert a._get_task_completed_expected_ratio('2026-W21', jim, 'week') == [1.0, 0.50]
            assert a._get_task_completed_expected_ratio('2026-W22', jim, 'week') == [1.0, 0.0, 0.6666666666666666, 1.0, 0.3333333333333333]

    class TestAnalyticsVolatilityTrends:
        def test_volatility_measurement_first(self):
            """Test the helper method which analyzes the volatility (low or high)
            of moods, task weights, difficulties, completion"""
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            jim_moods = a._get_mood_vals('2026-W22', jim, 'week')
            jim_weights = a._merge_lists(a._get_task_weights('2026-W22', jim, 'week'))
            jim_difficulties = a._merge_lists(a._get_task_difficulties('2026-W22', jim, 'week'))
            jim_completion = a._get_task_completed_expected_ratio('2026-W22', jim, 'week')

            assert a._volatility_measurement(jim_moods) == "High Volatility" # [6, 3, 8, 4, 9]
            assert a._volatility_measurement(jim_weights) == "High Volatility" # [8, 12, 22, 24, 22]
            assert a._volatility_measurement(jim_difficulties) == "Low/Stable Volatility" # [13, 14, 13, 15, 20]
            assert a._volatility_measurement(jim_completion) == "High Volatility" # [1.0, 0.0 ,0.66666, 1.0, 0.33333]

        def test_trend_shift(self):
            """Test the helper method analyzing trend direction of list (inc, stable, dec)."""
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            jim_moods = a._get_mood_vals('2026-W22', jim, 'week')
            jim_weights = a._merge_lists(a._get_task_weights('2026-W22', jim, 'week'))
            jim_difficulties = a._merge_lists(a._get_task_difficulties('2026-W22', jim, 'week'))
            jim_completion = a._get_task_completed_expected_ratio('2026-W22', jim, 'week')
            assert a._trend_shift(jim_moods) == "Increasing Trend"
            assert a._trend_shift(jim_weights) == "Increasing Trend"
            #assert a._trend_shift([8, 12, 22, 24, 22]) == "Sustained Increasing Trend"
            assert a._trend_shift(jim_difficulties) == "Increasing Trend"
            #assert a._trend_shift([13, 14, 13, 15, 20]) == "Sustained Increasing Trend"
            assert a._trend_shift(jim_completion) == "Decreasing Trend"
            #assert a._trend_shift([1.0, 0.0, 0.66666, 1.0, 0.33333]) == "Sustained Decreasing Trend"


    class TestAnalyticsDiagnosis:
        def test_total_analyzer_weekly(self):
            """Test the analyzer for a specific week.
            (May 25, 2026 - May 29, 2026)."""
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            assert a.total_analyzer(e=jim, period='2026-W22', period_type='week') == 1.0

        def test_total_analyzer_monthly(self):
            """Test the analyzer for a specific month.
            (May 2026) (does not include all days)."""
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            assert a.total_analyzer(e=jim, period='2026-05', period_type='month') == 1.0

        def test_total_analyzer_yearly(self):
            """Test the analyzer for a specific year.
            (2026) (does not include all months)."""
            s = Storage('employee_info.json')
            a = Analytics()
            jim = s.get_employee('E1001')
            assert a.total_analyzer(e=jim, period='2026', period_type='year') == 1.0
