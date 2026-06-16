from Employee import Employee
from Loader import Loader
import json

class Storage:
    """
    The storage system.

    This is the location where important data lives in real-time, and allows access
    to the current state of the system live.
    """
    def __init__(self):
        """Initialize the storage system."""
        l = Loader('employee_info.json')
        self._employee_storage = {}
        l.build_employees(self._employee_storage)

    def get_employee(self, employee_id: str) -> Employee | None:
        """Return an employee from the employee storage."""
        if employee_id not in self._employee_storage:
            return None # TEMPORARY: exceptions will be implemented later on
        else:
            return self._employee_storage[employee_id]

    def get_all_employees(self) -> dict[str, Employee]:
        """Return all employees from the employee storage."""
        return self._employee_storage

    def contains_employee(self, _id: str) -> bool:
        """Return True if the employee ID is in the storage.
        Otherwise, return False."""
        for employee_id in self._employee_storage:
            if employee_id == _id:
                return True
        return False

    def add_employee(self, e: Employee) -> None:
        """Add an employee to the storage."""
        if not self.contains_employee(e.employee_id):
            # only add if employee does not exist already
            self._employee_storage[e.employee_id] = e
        # NOTE: raise exceptions later if employee id already exists!

    def remove_employee(self, e: Employee) -> None:
        """Remove an employee from the storage."""
        if self.contains_employee(e.employee_id):
            # remove if the employee exists in storage
            self._employee_storage.pop(e.employee_id)
        # NOTE: raise exceptions later if employee id does not exist!

    def save(self) -> None:
        """Save new information to the JSON file."""
        pass

if __name__ == "__main__":
    loader = Loader('employee_info.json')
    s = Storage()
    jim = s.get_employee('E1001')
    print("Jim's Profile:", jim)
    print("Jim's Moods: ", jim.get_moods())
    print("Jim's Tasks: ", jim.get_tasks())
    jim_tasks = jim.get_tasks()
    jim_list = jim_tasks['2026-05-23']
    print("Before Completion, May 23, 2026's Task 1:", jim_list[0])
    jim.complete_task(jim_list[0])
    print("After Completion, May 23, 2026's Task 1:", jim_list[0])
