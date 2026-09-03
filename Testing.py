import pytest
import json
from Employee import Employee, Manager
from Task import Task
from Analysis import Analysis
from Loader import Loader
from Storage import Storage
from datetime import date

class Testing:
    """The testing suite.

     This class focuses on testcases ensuring implementation is meeting expectations.
    Standard cases, edge cases, and property-based testing are all covered.

    Components:

    Section 1: The First Testing:
    (All tested on one employee with 5 days worth of data):
    - TestObjectConstruction: checks if objects are properly being constructed from the JSON
    - TestMoodRater: checks if moods are properly being rated and recorded
    - TestTaskCRUD: checks for correct CRUD functionalities
    - TestAnalysisDataRetrieval: tests proper data extraction from employee objects for analysis
    - TestAnalysisEnvironment, TestAnalysisVolatility, TestAnalysisDirection, TestAnalysisCases
    and TestAnalysisResult: these classes all test the building blocks of the analysis and the final results

    Section 2: The Analysis Focused Testing:
    (Tested on a JSON file containing various employees with different data)

    Section 3: JSON File/IO Testing

    Section 4: Streamlit Frontend Testing

     """

    def test_all(self):
        """Placeholder for all tests."""
        pass

# Section 1: The First Testing:
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
            m = Manager('employee_info.json')
            jim = s.get_employee('E1001')
            t = Task('T1', 'Prank Dwight', 10, 10, str(date.today()), False)
            m.add_task(t, jim)
            jim.rate_mood(9, str(date.today()))
            assert jim.get_specific_mood(str(date.today())) == 9

        def test_mood_rater_no_task(self):
            """Test the case where an employee tries to rate their mood, despite not
            having task(s) for that day. This implies that the employee was essentially
            absent that day."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            jim.rate_mood(9, str(date.today()))
            assert jim.get_specific_mood(str(date.today())) is None

        def test_mood_rater_change(self):
            """Test the case where an employee updates their mood for a day."""
            s = Storage('employee_info.json')
            m = Manager('employee_info.json')
            jim = s.get_employee('E1001')
            t = Task('T1', 'Prank Dwight', 10, 10, str(date.today()), False)
            m.add_task(t, jim)
            jim.rate_mood(9, str(date.today()))
            jim.rate_mood(4, str(date.today()))
            assert jim.get_specific_mood(str(date.today())) == 4 # no change

    class TestTaskCRUD:
        def test_add_task_success(self):
            """Test a manager adding a task for an employee."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('employee_info.json')
            t = Task('T1', 'Raid Utica', 10, 10, str(date.today()), False)
            m.add_task(t, jim)
            jim_tasks = jim.get_tasks()
            assert t in jim_tasks[str(date.today())]

        def test_add_task_fail(self):
            """Test a manager adding a duplicate task for an employee"""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('employee_info.json')
            t1 = Task('T1', 'Raid Utica', 10, 10, str(date.today()), False)
            m.add_task(t1, jim)
            t2 = Task('T2', 'Raid Utica', 10, 10, str(date.today()), False)
            m.add_task(t2, jim)
            jim_tasks = jim.get_tasks()
            assert t1 in jim_tasks[str(date.today())]
            assert t2 not in jim_tasks[str(date.today())] # no duplicate exists


        def test_remove_task(self):
            """Test a manager removing a task for an employee."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('employee_info.json')
            #pre-removal:
            assert jim.get_specific_task('2026-05-23', 'Contact Leads') is not None
            m.remove_task('Contact Leads', jim, '2026-05-23')
            #post-removal:
            assert jim.get_specific_task('2026-05-23', 'Contact Leads') is None

        def test_change_task(self):
            """Test a manager changing a task for an employee."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            m = Manager('employee_info.json')
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

        def test_complete_task(self):
            """Test an employee completing a task."""
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            jim_tasks = jim.get_tasks()
            assert jim_tasks['2026-05-24'][1].completed is False
            jim.complete_task(jim_tasks['2026-05-24'][1])
            assert jim_tasks['2026-05-24'][1].completed is True


    class TestAnalysisDataRetrieval:
        def test_mood_value_retrieval(self):
            """Test the helper method which retrieves mood values for a specific week.
            Weeks are ISO-based.
            """
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            assert a._get_mood_vals('2026-W21', jim, 'week') == [7, 4]
            assert a._get_mood_vals('2026-W22', jim, 'week') == [6, 3, 8, 4, 9]

        def test_task_weight_value_retrieval(self):
            """Test the helper method which retrieves task weights for a specific week.
            Weeks are ISO-based.
            """
            s = Storage('employee_info.json')
            a = Analysis()
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
            a = Analysis()
            jim = s.get_employee('E1001')
            assert (a._get_task_difficulties('2026-W21', jim, 'week') ==
                    {"2026-05-23": [6, 7], "2026-05-24": [6, 7]})
            assert (a._get_task_difficulties('2026-W22', jim, 'week') ==
                    {'2026-05-25': [6, 7],
                     '2026-05-26': [6, 8],
                     '2026-05-27': [2, 8, 3],
                     '2026-05-28': [3, 10, 2],
                     '2026-05-29': [3, 10, 7]})

        def test_merge_weights(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            assert a.merge_weights(a._get_task_weights('2026-W22', jim, 'week')) == [8, 12, 22, 24, 22]

        def test_merge_diff(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            assert a.merge_diff(a._get_task_difficulties('2026-W22', jim, 'week')) == [7, 8, 8, 10, 10]

        def test_task_comp_ratio(self):
            """Test task completion to task expected ratio."""
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            # assert a._get_task_completed_expected_ratio('2026-W21', jim) == 0.75 #3/4
            # assert a._get_task_completed_expected_ratio('2026-W22', jim) == 0.50 #2/4
            assert a._get_task_completed_expected_ratio('2026-W21', jim, 'week') == [1.0, 0.50]
            assert a._get_task_completed_expected_ratio('2026-W22', jim, 'week') == [1.0, 0.0, 0.6666666666666666, 1.0, 0.3333333333333333]

        def test_tasks_for_specific_week(self):
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            assert jim.get_tasks_for_specific_week('2026-W22') == 3 # works (3 is a placeholder, lots of task objects)

        def test_moods_for_specific_week(self):
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            assert jim.get_moods_for_specific_week('2026-W22') == {'2026-05-25': 6, '2026-05-26': 3, '2026-05-27': 8,
                                                                   '2026-05-28': 4, '2026-05-29': 9, '2026-05-30': 10}

    class TestAnalysisEnvironment:
        def test_mood_environment_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_moods = a._get_mood_vals('2026-W22', jim, 'week')
            assert a.mood_environment(jim_moods) == 'MM'

        def test_task_completion_environment_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_comp = a._get_task_completed_expected_ratio('2026-W22', jim, 'week')
            assert a.completion_environment(jim_comp) == 'HC'

        def test_ask_weight_environment_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_weights = a.merge_weights(a._get_task_weights('2026-W22', jim, 'week'))
            assert a.weight_environment(jim_weights) == 'MW'

        def test_task_difficulty_environment_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_diff = a.merge_diff(a._get_task_difficulties('2026-W22', jim, 'week'))
            assert a.diff_environment(jim_diff) == 'HD'

    class TestAnalysisVolatility:
        def test_mood_volatility_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_moods = a._get_mood_vals('2026-W22', jim, 'week')
            assert a.mood_volatility(jim_moods) == 'HV'

        def test_task_completion_volatility_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_comp = a._get_task_completed_expected_ratio('2026-W22', jim, 'week')
            assert a.comp_volatility(jim_comp) == 'HV'

        def test_ask_weight_volatility_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_weights = a.merge_weights(a._get_task_weights('2026-W22', jim, 'week'))
            assert a.task_weight_volatility(jim_weights) == 'MV'

        def test_task_difficulty_volatility_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_diff = a.merge_diff(a._get_task_difficulties('2026-W22', jim, 'week'))
            assert a.task_diff_volatility(jim_diff) == 'LV'

    class TestAnalysisDirection:
        def test_mood_direction_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_moods = a._get_mood_vals('2026-W22', jim, 'week')
            assert a.mood_diff_direction(jim_moods) == 'UP'

        def test_task_completion_volatility_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_comp = a._get_task_completed_expected_ratio('2026-W22', jim, 'week')
            assert a.comp_direction(jim_comp) == 'UP'

        def test_ask_weight_volatility_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_weights = a.merge_weights(a._get_task_weights('2026-W22', jim, 'week'))
            assert a.weight_direction(jim_weights) == 'UP'

        def test_task_difficulty_volatility_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            jim_diff = a.merge_diff(a._get_task_difficulties('2026-W22', jim, 'week'))
            assert a.mood_diff_direction(jim_diff) == 'UP'

    class TestAnalysisScoring:
        def test_employee_state_weekly(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            assert a.develop_employee_state(jim, '2026-W22', 'week') == (('MM', 'HV', 'UP'), ('HC', 'HV', 'UP'), ('MW', 'MV', 'UP'), ('HD', 'LV', 'UP'))

        def test_mood_score(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            state = a.develop_employee_state(jim, '2026-W22', 'week')
            assert a._calculate_mood_score(state) == 5.95

        def test_comp_score(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            state = a.develop_employee_state(jim, '2026-W22', 'week')
            assert a._calculate_comp_score(state) == 4.15

        def test_weight_score(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            state = a.develop_employee_state(jim, '2026-W22', 'week')
            assert a._calculate_weight_score(state) == 6.00

        def test_diff_score(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            state = a.develop_employee_state(jim, '2026-W22', 'week')
            assert a._calculate_diff_score(state) == 6.30

        def test_sum_score(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            state = a.develop_employee_state(jim, '2026-W22', 'week')
            assert a._sum_burnout_score(state) == 22.400000000000002
            assert a._sum_burnout_score(state) / 4 == 5.6000000000000005

        def test_score_verdict(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            state = a.develop_employee_state(jim, '2026-W22', 'week')
            score = a._sum_burnout_score(state)
            assert a._get_score_category(score) == 'ELEVATED WORKLOAD STRAIN: Burnout Score 22.4/40.0'

    class TestAnalysisCases:
        def test_employee_case(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            state = a.develop_employee_state(jim, '2026-W22', 'week')
            assert a.evaluate_case(state) == 'GENERAL OPERATIONAL LOAD: No acute operational patterns detected.'

    class TestAnalysisResult:
        def test_employee_delivered_report(self):
            s = Storage('employee_info.json')
            a = Analysis()
            jim = s.get_employee('E1001')
            assert a.deliver_report(jim, '2026-W22', 'week') == ('ELEVATED WORKLOAD STRAIN: Burnout Score 21.05/40.0\n'
 'GENERAL OPERATIONAL LOAD: No acute operational patterns detected.')

# Section 2: The Analysis Focused
    class TestEmployeeResults:
        def test_report(self):
            s = Storage('employees_demo_dataset.json')
            a = Analysis()
            carlos_mendez = s.get_employee('E1010')
            assert a.deliver_report(carlos_mendez, '2026-W22', 'week') == ('OPTIMAL BASELINE: Burnout Score 10.8/40.0\n'
                                                                 'GENERAL OPERATIONAL LOAD: No acute operational patterns detected.')

# Section 3: JSON File/IO Testing
    class TestJSON:
        """
        WARNING: JSON Testing will change Analysis results.
        NOTE: JSON Testing only passes at the first attempt since the tests
        change the objects/values (i.e. task objects, mood values) and
        the information for them in the JSON file, rendering later
        tests 'unsuccessful'.
            """

        def test_task_completer(self):

            # Object Checker:
            s = Storage('employee_info.json')
            jim = s.get_employee('E1001')
            jim_tasks = jim.get_tasks()
            # assert jim_tasks['2026-05-24'][1].completed is True
            # ^^ once this complete_task method runs, it will always be as if the task was completed,
            # even before instantiating it since JSON was changed.
            jim.complete_task(jim_tasks['2026-05-24'][1])
            assert jim_tasks['2026-05-24'][1].completed is True

            # JSON Checker:
            with open('employee_info.json') as json_file:
                self.loader = json.load(json_file)

            for employees in self.loader['employees']:
                if employees['name'] == jim.name:
                    for day_date in employees['timeline']:
                        if day_date == jim_tasks['2026-05-24'][1].get_date():
                            for task in employees['timeline'][day_date]['tasks']:
                                if task['name'] == jim_tasks['2026-05-24'][1].name:
                                    assert task['completed'] is True

    def test_mood_rater_in_file(self):
        """Tests mood for an existing day (i.e. changes the mood for a day already rated)"""
        # During this testing, I decided to allow for moods to be altered by employees.
        # This is because analysis naturally adapts to new values so there is no issue.

        # Object Checker:
        s = Storage('employee_info.json')
        jim = s.get_employee('E1001')
        jim_moods_old = jim.get_moods()
        assert jim_moods_old['2026-05-23'] == 7
        jim.rate_mood(5, '2026-05-23')
        assert jim.get_moods()['2026-05-23'] == 5

        # JSON Checker:
        with open('employee_info.json') as json_file:
            self.loader = json.load(json_file)

        for employees in self.loader['employees']:
            if employees['name'] == jim.name:
                for day_date in employees['timeline']:
                    if day_date == '2026-05-23':
                        assert employees['timeline'][day_date]['mood'] == 5

    def test_mood_rater_fresh(self):
        """Adds a new mood to the JSON file for a day that has tasks but no mood yet.

        The loader method build_employees() ensures that employee object creation
        remains successful even if no mood exists yet.
        """
        # Object Checker:
        s = Storage('employee_info.json')
        jim = s.get_employee('E1001')
        jim.rate_mood(10, '2026-05-30')
        assert jim.get_moods()['2026-05-30'] == 10

        # JSON Checker:
        with open('employee_info.json') as json_file:
            self.loader = json.load(json_file)

        for employees in self.loader['employees']:
            if employees['name'] == jim.name:
                for day_date in employees['timeline']:
                    if day_date == '2026-05-30':
                        assert employees['timeline'][day_date]['mood'] == 10

    def test_task_adder_existing_date(self):

        # Object Checker:
        s = Storage('employee_info.json')
        jim = s.get_employee('E1001')
        m = Manager('employee_info.json')
        t = Task('T3', 'Distribute Flyers', 6, 3, '2026-05-23', False)
        m.add_task(t, jim)
        jim_tasks = jim.get_tasks()
        assert t in jim_tasks['2026-05-23']

        # JSON Checker:
        with open('employee_info.json') as json_file:
            self.loader = json.load(json_file)

        for employees in self.loader['employees']:
            if employees['name'] == jim.name:
                for day_date in employees['timeline']:
                    if day_date == t.get_date():
                        for task in employees['timeline'][day_date]['tasks']:
                            if task['name'] == t.name:
                                assert task['completed'] is False # ensure task has been added

    def test_task_adder_new_date(self):
        # Object Checker:
        s = Storage('employee_info.json')
        jim = s.get_employee('E1001')
        m = Manager('employee_info.json')
        t = Task('T1', 'Star in Dunder Mifflin Commercial', 4, 1, '2026-05-31', False)
        m.add_task(t, jim)
        jim_tasks = jim.get_tasks()
        assert t in jim_tasks['2026-05-31']

        # JSON Checker:
        with open('employee_info.json') as json_file:
            self.loader = json.load(json_file)

        for employees in self.loader['employees']:
            if employees['name'] == jim.name:
                for day_date in employees['timeline']:
                    if day_date == t.get_date(): # good sign since date has been added
                        for task in employees['timeline'][day_date]['tasks']:
                            if task['name'] == t.name: # good sign since task has been added
                                assert task['completed'] is False # method completer

    def test_task_remover(self):
        # Object Checker:
        s = Storage('employee_info.json')
        jim = s.get_employee('E1001')
        m = Manager('employee_info.json')
        # pre-removal:
        assert jim.get_specific_task('2026-05-30', 'Speak to Oscar about Accounting') is not None
        m.remove_task('Speak to Oscar about Accounting', jim, '2026-05-30')
        # post-removal:
        assert jim.get_specific_task('2026-05-30', 'Speak to Oscar about accounting') is None

        # JSON Checker:
        with open('employee_info.json') as json_file:
            self.loader = json.load(json_file)

        for employees in self.loader['employees']:
            if employees['name'] == jim.name:
                for day_date in employees['timeline']:
                    if day_date == '2026-05-30':
                        assert employees['timeline'][day_date]['tasks'][0]['name'] != 'Speak to Oscar about Accounting'
                        # this was originally index 0 so after the change, it should no longer be at index 0.


    def test_task_changer(self):
        # Note that tests only are successful once, due to object and JSON mutation,
        # the new info added in "Test 1" would then be the old info for "Test 2".

        # Object Checker:
        s = Storage('employee_info.json')
        jim = s.get_employee('E1001')
        m = Manager('employee_info.json')
        task = jim.get_specific_task('2026-05-23', 'Configure Sales Pitch')
        # pre-change:
        assert task.name == 'Configure Sales Pitch'
        assert task.get_weight() == 10
        assert task.get_difficulty() == 6
        m.change_task('Configure Sales Pitch', jim, '2026-05-23', 'Contact Leads',
                      8, 8)
        # post-change:
        assert task.name == 'Contact Leads'
        assert task.get_weight() == 8
        assert task.get_difficulty() == 8

        # JSON Checker:
        with open('employee_info.json') as json_file:
            self.loader = json.load(json_file)

        for employees in self.loader['employees']:
            if employees['name'] == jim.name:
                for day_date in employees['timeline']:
                    if day_date == '2026-05-23':
                        for task in employees['timeline'][day_date]['tasks']:
                            if task['name'] == 'Contact Leads': # find the updated name
                                assert task['weight'] == 8
                                assert task['difficulty'] == 8

# Section 4: Streamlit Frontend Testing
class TestStreamlit:
    pass
