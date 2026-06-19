import pytest
from Employee import Employee, Manager
from Task import Task
# from Analytics import Analytics
from Loader import Loader
from Storage import Storage
from datetime import date

class Testing:
    """The testing suite.

     This class focuses on testcases ensuring implementation is meeting expectations.
    Standard cases, edge cases, and property-based testing are all covered.
     """

    def test_employee_builder(self):
        """Test if an employee can be built from a JSON file."""
        storage = Storage()
        assert storage.get_employee('E1001').name == 'Jim Halpert'
        assert storage.get_employee('E1002').name == 'Dwight Schrute'
        assert storage.get_employee('E1001')._moods['2026-05-23'] == 7

    def test_mood_rater_success(self):
        """Test if an employee can properly rate their mood for the current day.

        The current day as of testing is '06-18-26'
        """
        s = Storage()
        jim = s.get_employee('E1001')
        t = Task('Prank Dwight', 10, 10, str(date.today()))
        jim.set_tasks(str(date.today()), t)
        """NOTE: ^^ this is used only for testing! The manager is supposed to 
        add tasks for an employee, not the employee themself!"""
        jim.rate_mood(9)
        assert jim.get_specific_mood(str(date.today())) == 9

    def test_mood_rater_no_task(self):
        """Test the case where an employee tries to rate their mood, despite not
        having task(s) for that day. This implies that the employee was essentially
        absent that day."""
        s = Storage()
        jim = s.get_employee('E1001')
        jim.rate_mood(9)
        assert jim.get_specific_mood(str(date.today())) is None

    def test_mood_rater_day_exists(self):
        """Test the case where an employee tries to rate their mood, yet they have
        already rated their mood for that day. Note that employees rate their mood
        before clocking off for work, so rating after the shift is over cannot work."""
        s = Storage()
        jim = s.get_employee('E1001')
        t = Task('Prank Dwight', 10, 10, str(date.today()))
        jim.set_tasks(str(date.today()), t)
        """NOTE: ^^ this is used only for testing! The manager is supposed to 
        add tasks for an employee, not the employee themself!"""
        jim.rate_mood(9)
        jim.rate_mood(4)
        assert jim.get_specific_mood(str(date.today())) == 9 # no change

    def test_add_task_success(self):
        """Test a manager adding a task for an employee."""
        s = Storage()
        jim = s.get_employee('E1001')
        m = Manager('Michael Scott', 'E0067')
        t = Task('Raid Utica', 10, 10, str(date.today()))
        m.add_task(t, jim, str(date.today()))
        jim_tasks = jim.get_tasks()
        assert t in jim_tasks[str(date.today())]

    def test_add_task_fail(self):
        """Test a manager adding a duplicate task for an employee."""
        s = Storage()
        jim = s.get_employee('E1001')
        m = Manager('Michael Scott', 'E0067')
        t1 = Task('Raid Utica', 10, 10, str(date.today()))
        m.add_task(t1, jim, str(date.today()))
        t2 = Task('Raid Utica', 10, 10, str(date.today()))
        m.add_task(t2, jim, str(date.today()))
        jim_tasks = jim.get_tasks()
        assert t1 in jim_tasks[str(date.today())]
        assert t2 not in jim_tasks[str(date.today())] # no duplicate exists
