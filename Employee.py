from datetime import date
from Task import Task

class Employee:
    """An employee.

    === Public Attributes ===
    name: the name of the Employee
    employee_id: the workplace ID of the Employees
    role: the role of the Employee

    === Private Attributes ===
    _moods: the daily rated moods of an employee
    _tasks: the daily tasks of an employee

    === Representation Invariants ===
    - the mood value of an employee must be between 1 and 10.
    - the name key of an employee's task must be defined as "TaskX" where X is an integer.
    """
    name: str
    employee_id: str
    role: str
    _moods: dict[str, int]
    _tasks: dict[str, list[Task]]
    def __init__(self, name: str, role: str, employee_id: str) -> None:
        """Instantiate an employee with given <name>, <role> and <employee_id>.
        Note: ONLY the Manager can do this.
        """
        self.name = name
        self.role = role
        self.employee_id = employee_id
        self._moods = {}
        self._tasks = {}

    def get_moods(self) -> dict[str, int]:
        """Get the daily moods of an employee."""
        return self._moods

    def get_tasks(self) -> dict[str, list[Task]]:
        """Get the daily tasks of an employee."""
        return self._tasks

    def rate_mood(self, mood_val: int) -> None:
        """Rate mood for the day which is <mood_val>.

        Precondition: 1 <= <mood_val> <= 10
        """
        pass

    def complete_task(self, t: Task) -> None:
        """Complete a task <t>."""
        t.completed = True

    def set_moods(self, str_date: str, mood_val: int) -> None:
        """Used by the Loader, this safely allows for access to
        _moods while maintaining proper information hiding.
        This is for building the _moods attribute based on
        pre-existing JSON file info.
        """
        self._moods[str_date] = mood_val

    def set_tasks(self, str_date: str, task: Task) -> None:
        """Used by the Loader, this safely allows for access to
        _tasks while maintaining proper information hiding.
        This is for building the _tasks attribute based on
        pre-existing JSON file info.
        """
        self._tasks.setdefault(str_date, []).append(task)

    def __str__(self):
        """String representation of the Employee."""
        return f"Employee: {self.name}, {self.role}, {self.employee_id} "

class Manager(Employee):
    """A manager.

    === Public Attributes ===
    name: the name of the Manager
    manager_id: the workplace ID of the Manager
    role: the role of the Manager

    === Private Attributes ===
    _moods: the daily rated moods of a manager
    _tasks: the daily tasks of a manager

    === Representation Invariants ===
    - the mood value of a manager must be between 0 and 10.
    - the name key of a manager's task must be defined as "TaskX" where X is an integer.
    - role = 'Manager'
    """
    name: str
    manager_id: int
    _moods: dict[date, int]
    _tasks: dict[date, dict[str, Task]]

    def __init__(self, name: str, manager_id: int) -> None:
        """Instantiate a manager with given <name> and <manager_id>.

        Note: ONLY the Manager can do this.
        """
        super().__init__(name, 'Manager', manager_id)
        pass

    def add_task(self, t: Task, e: Employee) -> None:
        """Add a task <t> for the employee <e>. """
        pass

    def remove_task(self, t: Task, e: Employee) -> None:
        """Remove a task <t> for the employee <e>."""
        pass

    def change_task(self, t: Task, e: Employee) -> None:
        """Change a task <t> for the employee <e>."""
        pass
