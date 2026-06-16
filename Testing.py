import pytest
from Employee import Employee, Manager
from Task import Task
# from Analytics import Analytics
from Loader import Loader
from Storage import Storage

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
