import json
from Employee import Employee
from Task import Task
from datetime import date

class Loader:
    """The loader class.

    This class ensures a safe loading/saving process for the JSON file
    known as "employee_info.json" storing core employee info.
    """

    def __init__(self, json_file: str) -> None:
        """Initialize the loader class."""
        with open(json_file) as json_file:
            self.loader = json.load(json_file)

    def build_employees(self, storage: dict) -> None:
        """Builds employee objects from all employees in the JSON file."""
        for employees in self.loader['employees']:
            # Construct Attributes & Object:
            name = employees['name']
            role = employees['role']
            emp_id = employees['employee_id']
            employee_obj = Employee(name, role, emp_id)
            #self.employee_list[emp_id] = employee_obj
            #s.add_employee(employee_obj)

            # Set Up Mood and Tasks Attributes:
            if "timeline" in employees:
                for mood_task_date in employees['timeline']:
                    #employee_obj.set_moods(mood_task_date, employees['timeline'][mood_task_date]['mood'])
                    self.set_moods(mood_task_date, employees['timeline'][mood_task_date]['mood'], employee_obj)
                    for task in employees['timeline'][mood_task_date]['tasks']:
                        task_obj = Task(task['name'], task['weight'], task['difficulty'],
                                        mood_task_date, task['completed'])
                        #employee_obj.set_tasks(mood_task_date, task_obj)
                        self.set_tasks(mood_task_date, task_obj, employee_obj)

            #s.add_employee(employee_obj)
            storage[emp_id] = employee_obj

    def set_moods(self, str_date: str, mood_val: int, e: Employee) -> None:
        """Build the _moods attribute for an employee based on pre-existing
        JSON file info."""
        moods = e.get_moods()
        moods[str_date] = mood_val

    def set_tasks(self, str_date: str, task: Task, e: Employee) -> None:
        """ Build the _tasks attribute for an employee based on pre-existing
        JSON file info."""
        tasks = e.get_tasks()
        tasks.setdefault(str_date, []).append(task)

    def build_task(self) -> Task:
        """Builds a task object from the JSON file."""
        pass

    def date_parser(self, date_string: str) -> date:
        """Parse the date from the JSON file."""
        return date.fromisoformat(date_string)
