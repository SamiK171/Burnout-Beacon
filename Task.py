from datetime import date

class Task:
    """A task.

    === Public Attributes ===
    name: the name of the task.
    completed: the status of the task

    === Private Attributes ===
    _weight: the weight of the task.
    _difficulty: the difficulty of the task.

    === Representation Invariants ===
    - 0 <= _weight <= 10
    - 0 <= _difficulty <= 10
    - _date can only be datetime.today() or a date after datetime.today()
    """
    name: str
    completed: bool
    _weight: int
    _difficulty: int
    _date: str
    def __init__(self, name: str, weight: int, difficulty: int, t_date: str, completed: bool) -> None:
        """Instantiate a task.

        Note: ONLY a Manager can do this
        Note: When tasks are created by the Loader, they may be instantiated as true if that
        is what the JSON file says. Otherwise, when created by the Manager, their "completed"
        value should default to False.
        Precondition: 0 <= weight <= 10, 0 <= difficulty <= 10
        """
        self.name = name
        self.completed = completed
        self._weight = weight
        self._difficulty = difficulty
        self._date = t_date

    def get_name(self) -> str:
        """Get the name of the task."""
        return self.name

    def set_name(self, name: str) -> None:
        """Set the name of the task to <name>."""
        self.name = name

    def get_weight(self) -> int:
        """Get the weight of the task."""
        return self._weight

    def set_weight(self, weight: int):
        """Set the weight of the task to <weight>.

        Precondition: 0 <= weight <= 10
        """
        self._weight = weight

    def get_difficulty(self) -> int:
        """Get the difficulty of the task."""
        return self._difficulty

    def set_difficulty(self, difficulty: int):
        """Set the difficulty of the task to <difficulty>.

        Precondition: 0 <= difficulty <= 10
        """
        self._difficulty = difficulty

    def get_date(self) -> str:
        """Get the date of the task."""
        return self._date

    def set_date(self, d: str) -> None:
        """Set the date of the task to <d>."""
        self._date = d

    def __str__(self) -> str:
        """String representation of the Task."""
        text = (f"Task Name: {self.name}, Weight: {self.get_weight()}, Difficulty: {self.get_difficulty()}, "
                f"Completed?: {self.completed}, Date: {self.get_date()}")
        return text
