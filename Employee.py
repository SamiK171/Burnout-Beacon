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
    def __init__(self, name: str, role: str, employee_id: str, file_name: str) -> None:
        """Instantiate an employee with given <name>, <role> and <employee_id>.
        Note: ONLY the Manager can do this.
        """
        self.name = name
        self.role = role
        self.employee_id = employee_id
        self._moods = {}
        self._tasks = {}
        self._file_name = file_name

    def get_moods(self) -> dict[str, int]:
        """Get the daily moods of an employee."""
        return self._moods

    def get_tasks(self) -> dict[str, list[Task]]:
        """Get the daily tasks of an employee."""
        return self._tasks

    def get_specific_mood(self, d: str) -> int | None:
        """Returns the mood of an employee on a specific date <d>"""
        if d in self._moods:
            return self._moods[d]
        else:
            return None # could be an exception later

    def get_specific_task(self, d: str, name: str) -> Task | None:
        """Returns the task of an employee on a specific date <d>"""
        if d in self._tasks:
            for task in self._tasks[d]:
                if task.name == name:
                    return task
        else:
            return None # could be an exception later

    def get_tasks_for_specific_date(self, d: str) -> list[Task] | None:
        if d in self._tasks:
            return self._tasks[d]
        else:
            return None

    def rate_mood(self, mood_val: int, mood_date: str) -> None:
        """Rate mood for the day which is <mood_val>.

        Precondition: 1 <= <mood_val> <= 10
        """
        from Loader import Loader
        if 1 <= mood_val <= 10:
            if mood_date not in self._tasks: # indicates employee absence
                ... # RAISE Error or handle here. TBD.
            else:
                self._moods[mood_date] = mood_val
                l = Loader(self._file_name)
                l.mood_adder(mood_val, mood_date, self)
        else:
            ... # raise some error/exception perhaps.


    def complete_task(self, t: Task) -> None:
        """Complete a task <t>."""
        from Loader import Loader
        t.completed = True
        l = Loader(self._file_name)
        l.task_completer(self, t)

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
    manager_id: str
    _moods: dict[date, int]
    _tasks: dict[date, dict[str, Task]]

    def __init__(self, name: str, manager_id: str, file_name: str) -> None:
        """Instantiate a manager with given <name> and <manager_id>.

        Note: ONLY the Manager can do this.
        """
        super().__init__(name, 'Manager', manager_id, file_name)
        pass

    def add_task(self, t: Task, e: Employee) -> None:
        """Add a task <t> for the employee <e>. """
        from Loader import Loader # avoids circular imports
        e_tasks = e.get_tasks()
        for dates in e_tasks:
            for task in e_tasks[dates]:
                if task.name == t.name: # if the task already exists
                    return None # raise some error here later & finish method
        e_tasks.setdefault(t.get_date(), []).append(t)
        l = Loader(self._file_name)
        l.task_adder(t, e)

    def remove_task(self, task_name: str, e: Employee, task_date: str) -> None:
        """Remove a task for the employee <e> by its <task_name>."""
        from Loader import Loader
        e_tasks = e.get_tasks()
        for dates in e_tasks:
            if dates == task_date:
                for task in e_tasks[dates]:
                    if task.name == task_name:
                        e_tasks[dates].remove(task)
        l = Loader(self._file_name)
        l.task_remover(task_name, e, task_date)

    def change_task(self, task_name: str, e: Employee,
                    task_date: str, name=None, weight=None, difficulty=None) -> None:
        """Change a task <t> for the employee <e>.
        Managers cannot change if a task is completed or not as only the employee can do that.
        """
        # ROUGH IMPLEMENTATION (the case where date is changed has not been covered yet)
        from Loader import Loader
        e_tasks = e.get_tasks()
        for dates in e_tasks:
            if dates == task_date:
                for task in e_tasks[dates]:
                    if task.name == task_name:
                        if name is not None:
                            task.set_name(name)
                        if weight is not None:
                            task.set_weight(weight)
                        if difficulty is not None:
                            task.set_difficulty(difficulty)
        l = Loader(self._file_name)
        l.task_changer(task_name, e, task_date, name, weight, difficulty)

if __name__ == '__main__':
    x = str(date.today())
    print(x == '2026-06-18')
