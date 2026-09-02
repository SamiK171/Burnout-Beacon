import streamlit as st
from Storage import Storage
from Analysis import Analysis
from Employee import Employee, Manager
from Task import Task
from Loader import Loader
from datetime import datetime, timedelta
import pandas as pd

class Interface:
    """The graphical user interface powered by Streamlit.

    This class handles the frontend of the application and covers aspects such
    as event handling, user interaction, and authentication, powered by Streamlit.
    """
    def __init__(self, filename: str):
        self.storage = Storage(filename)
        self.analysis = Analysis()

    def render_top_bar(self, title_text: str):
        """Header with mode switcher on the top right.
        Changes from Manager View to Employee View & vice versa.
        """
        col_title, col_mode = st.columns([3, 1])
        with col_title:
            st.title(title_text)
        with col_mode:
            st.session_state.user_role = st.radio(
                "Mode",
                ["Manager", "Employee"],
                index=0 if st.session_state.get("user_role") == "Manager" else 1,
                horizontal=True
            )
        st.divider()

    def render(self):
        """Abstract method. Child views must implement their own layout."""
        raise NotImplementedError

class EmployeeView(Interface):
    """The employee view."""

    def render(self):
        self.render_top_bar(" 👔 EMPLOYEE PORTAL: ")

        col_left, col_mid, col_right = st.columns([1, 2, 1])
        # Left (Task & Mood History), # Mid: Analysis Report, # Right: Mood Rating, Employee Selection

        # RIGHT COLUMN BUTTONS:
        with col_right:

            # Employee & Week Selection:
            employee_dict = self.storage.get_all_employees()
            st.subheader("👤 Employee Selection")
            selected_employee = st.selectbox("Select Yourself",
                         options=employee_dict.values(),
                         format_func=lambda emp: f"{emp.name} (ID: {emp.employee_id})")

            st.subheader("🕰️ Week Selection")
            selected_week = st.selectbox("Select A Week Number",
                                         options=range(1, 53),
                                         format_func=lambda week: f"Week: {week}"
                                         )
            curr_year = str(datetime.now().year)
            week_id = f'{curr_year}-W{selected_week}'

            st.write(f"Selected Employee: {selected_employee.name}")
            st.write(f"Selected Week: {selected_week}")

            st.divider()

            st.subheader("🎭 Rate Mood")
            mood = st.slider("How are you feeling today?", 1, 10, 5)
            if st.button("Submit Mood Log", width="stretch"):
                # width="stretch" equivalent to use_container_width=True
                mood_rating = selected_employee.rate_mood(mood, str(datetime.now().date()))
                # ^ currently this is designed to be for today's date, might change later
                if type(mood_rating) is str:
                    st.warning("Mood cannot be rated!")
                else:
                    st.success("Mood Logged!")

        # LEFT COLUMN BUTTONS:
        with col_left:
            st.subheader("Quick Navigation")
            if st.button("📋 Tasks for Today", width="stretch"):
                self._show_today_tasks_dialog(selected_employee)

            if st.button("📅 Task History", width="stretch"):
                self._show_task_history_dialog(selected_employee)

            if st.button("🎭 Mood History", width="stretch"):
                self._show_mood_history_dialog(selected_employee)

            if st.button("✅ Complete Task", width="stretch"):
                self._select_task_to_complete(selected_employee)

        # MID COLUMN:
        with col_mid:
            st.subheader("📊 Burnout Analysis Report")
            report = self.analysis.deliver_report(selected_employee, week_id, 'week')

            if report == "Insufficient data for a report.":
                st.warning(report)
            else:

                week_start = datetime.fromisocalendar(int(curr_year), selected_week, 1)
                week_end = week_start + timedelta(days=4)
                st.info(f"Timeframe: Start: {week_start.date()} | End: {week_end.date()}")
                st.info(report)

                mood_vals = self.analysis._get_mood_vals(week_id, selected_employee, 'week')
                task_comp_vals = self.analysis._get_task_completed_expected_ratio(week_id, selected_employee, 'week')
                scaled_completion = [comp * 10 for comp in task_comp_vals] # multiply comp ratios by 10 to match mood scaling
                data = {
                    "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    "Mood": mood_vals,
                    "Task Completion": scaled_completion,
                }

                df = pd.DataFrame(data)
                day_order = ["Mon", "Tue", "Wed", "Thu", "Fri"]

                df["Day"] = pd.Categorical(df["Day"], categories=day_order, ordered=True)

                df = df.sort_values("Day").set_index("Day")

                st.line_chart(df)

                state = self.analysis.develop_employee_state(selected_employee, week_id, 'week')

                STATE_DESCRIPTIONS = {
                    "Environment Conditions": {
                        "LM": "😕 Low Mood Baseline: Overall weekly mood stayed in the lower range (1–4).",
                        "MM": "🙂 Moderate Mood Baseline: Weekly mood remained stable in the mid-range (5–6).",
                        "HM": "😄 High Mood Baseline: Overall weekly mood remained elevated in the top range (7–10).",
                        "LC": "⬇️ Low Completion Rate: Task execution was low, staying below 50% on most days.",
                        "MC": "⬅️➡️ Moderate Completion Rate: Task execution fluctuated around the 50% mark.",
                        "HC": "⬆️ High Completion Rate: Task execution was strong, exceeding 50% on most days.",
                        "HW": "🏋️ High Task Importance: Average workload weight remained elevated this week.",
                        "MW": "⚖️ Moderate Task Importance: Workload weight stayed at a steady, balanced level.",
                        "LW": "🍃 Low Task Importance: Assigned workload weight was minimal this week.",
                        "HD": "🧠 High Task Difficulty: Assigned tasks carried high overall complexity this week.",
                        "MD": "🧩 Moderate Task Difficulty: Task complexity remained at a manageable baseline.",
                        "LD": "🌱 Low Task Difficulty: Assigned tasks carried minimal complexity this week.",
                    },
                    "Volatility Condition": {
                        "HV": "⚡ High Volatility: Metric fluctuated significantly with large day-to-day shifts.",
                        "MV": "〰️ Moderate Volatility: Metric fluctuated within a predictable, consistent range.",
                        "LV": "🧘 Low Volatility: Metric remained highly stable with little to no daily variance.",
                    },
                    "Internal Direction Condition": {  # Mood & Task Completion
                        "UP": "📈 Upward Trend: Metric improved steadily across the week, indicating positive momentum.",
                        "FLAT": "➡️ Steady Baseline: Metric remained flat throughout the week with no major shifts.",
                        "DOWN": "📉 Downward Trend: Metric declined steadily across the week, indicating negative drift.",
                    },
                    "External Direction Condition": {  # Task Weight & Difficulty
                        "UP": "📈 Escalating Workload: Metric increased across the week, indicating rising workload pressure.",
                        "FLAT": "➡️ Steady Workload: Metric remained flat throughout the week with no major shifts.",
                        "DOWN": "📉 Easing Workload: Metric decreased across the week, indicating a release in workload pressure.",
                    },
                }

                st.info("METRIC ANALYSIS: ")
                if st.button("🌎View Metric Environments: "):
                    st.info(f"MOOD: {STATE_DESCRIPTIONS["Environment Conditions"][state[0][0]]}")
                    st.info(f"TASK COMPLETION: {STATE_DESCRIPTIONS["Environment Conditions"][state[1][0]]}")
                    st.info(f"TASK WEIGHT: {STATE_DESCRIPTIONS["Environment Conditions"][state[2][0]]}")
                    st.info(f"TASK DIFFICULTY: {STATE_DESCRIPTIONS["Environment Conditions"][state[3][0]]}")

                if st.button("🔃View Metric Volatility: "):
                    st.info(f"MOOD: {STATE_DESCRIPTIONS["Volatility Condition"][state[0][1]]}")
                    st.info(f"TASK COMPLETION: {STATE_DESCRIPTIONS["Volatility Condition"][state[1][1]]}")
                    st.info(f"TASK WEIGHT: {STATE_DESCRIPTIONS["Volatility Condition"][state[2][1]]}")
                    st.info(f"TASK DIFFICULTY: {STATE_DESCRIPTIONS["Volatility Condition"][state[3][1]]}")

                if st.button("📉📈View Metric Direction: "):
                    st.info(f"MOOD: {STATE_DESCRIPTIONS["Internal Direction Condition"][state[0][2]]}")
                    st.info(f"TASK COMPLETION: {STATE_DESCRIPTIONS["Internal Direction Condition"][state[1][2]]}")
                    st.info(f"TASK WEIGHT: {STATE_DESCRIPTIONS["External Direction Condition"][state[2][2]]}")
                    st.info(f"TASK DIFFICULTY: {STATE_DESCRIPTIONS["External Direction Condition"][state[3][2]]}")


                st.info("📥WEEKLY CONTEXT: ")
                if st.button("💼 Check Week's Tasks", use_container_width=True):
                    self._display_analysis_week_tasks(selected_employee, week_id)
                if st.button("🧠 Check Week's Moods", use_container_width=True):
                    self._display_analysis_week_moods(selected_employee, week_id)

    @st.dialog("📋 Tasks for Today")
    def _show_today_tasks_dialog(self, e: Employee):
        """Show today's tasks of the employee."""
        curr_date = str(datetime.now().date())
        today_tasks = e.get_tasks_for_specific_date(curr_date)

        if today_tasks is None:
            st.write("No available tasks for today.")
        else:
            for task in today_tasks:
                st.write(f"Task: {task.name}"
                         f" | Weight: {task.get_weight()}/10"
                         f" | Difficulty: {task.get_difficulty()}/10"
                         f" | Completed: {'Yes' if task.completed is True else 'No'}")

    @st.dialog("📅 Task History")
    def _show_task_history_dialog(self, e: Employee):
        """Show the task history of the employee."""
        selected_week = st.selectbox("Select A Week Number",
                                     options=range(1, 53),
                                     format_func=lambda week: f"Week: {week}"
                                     )
        curr_year = str(datetime.now().year)
        week_id = f'{curr_year}-W{selected_week}'
        self._display_analysis_week_tasks(e, week_id)

    @st.dialog("🎭 Mood History")
    def _show_mood_history_dialog(self, e: Employee):
        """Show the mood history of the employee."""
        selected_week = st.selectbox("Select A Week Number",
                                     options=range(1, 53),
                                     format_func=lambda week: f"Week: {week}"
                                     )
        curr_year = str(datetime.now().year)
        week_id = f'{curr_year}-W{selected_week}'
        self._display_analysis_week_moods(e, week_id)

    @st.dialog("✅ Complete Task")
    def _select_task_to_complete(self, e: Employee):
        """Select task to complete."""
        curr_date = str(datetime.now().date())
        today_tasks = e.get_tasks_for_specific_date(curr_date)

        if "task_success_msg" in st.session_state:
            st.success(st.session_state.task_success_msg)
            del st.session_state.task_success_msg

        if today_tasks is None:
            st.write("No available tasks for today.")
        else:
            with st.form("task_completion_form"):
                st.subheader(f"📋 Tasks for {curr_date}")

                # Dictionary to track which checkboxes get checked
                task_checks = {}

                for task in today_tasks:
                    label = (
                        f"**{task.name}** — "
                        f"Weight: {task.get_weight()}/10 | "
                        f"Difficulty: {task.get_difficulty()}/10 | "
                        f"Completed: {'Yes' if task.completed is True else 'No'}"
                    )
                    # Render a checkbox for each task
                    task_checks[task] = st.checkbox(label, key=f"chk_{task.name}")

                # 2. Single submit button for the entire form
                submitted = st.form_submit_button("Submit Completed Tasks", use_container_width=True)

            # 3. Process the backend updates ONLY when the form is submitted
            if submitted:
                completed_count = 0
                for task, is_checked in task_checks.items():
                    if is_checked:
                        e.complete_task(task)  # Updates object & backend JSON
                        completed_count += 1

                if completed_count > 0:
                    st.session_state.flash_msg = f"✅ Successfully updated {completed_count} task(s)!"
                else:
                    st.session_state.flash_msg = "ℹ️ No tasks were checked."

                st.rerun()

            # Display persistent banner message after form rerun
        if "flash_msg" in st.session_state:
            st.success(st.session_state.flash_msg)
            del st.session_state.flash_msg

    def _display_analysis_week_tasks(self, e: Employee, w: str):
        """Display the tasks for the week."""
        week_tasks = e.get_tasks_for_specific_week(w)
        if not week_tasks:
            st.warning("No available tasks for this week.")
        else:
            for date in week_tasks:
                st.write(f"Date: {date}")
                for task in week_tasks[date]:
                    st.write(f"Task Name: {task.name} |"
                             f" Weight: {task.get_weight()}/10 |"
                             f" Difficulty: {task.get_difficulty()}/10 |"
                             f" Completed: {"Yes" if task.completed is True else "No"}")
                st.write("-----------------")

    def _display_analysis_week_moods(self, e: Employee, w: str):
        """Display the moods for the week."""
        week_moods = e.get_moods_for_specific_week(w)
        if not week_moods:
            st.warning("No available moods for this week.")
        else:
            for date in week_moods:
                st.write(f"Date: {date} | Mood: {week_moods[date]}")

class ManagerView(EmployeeView):
    """The manager view."""

    def __init__(self, filename: str):
        super().__init__(filename)
        self.manager = Manager(filename)

    def render(self):
        """Render the manager view."""
        self.render_top_bar(" 👨‍💼 MANAGEMENT PORTAL: ")

        col_left, col_mid, col_right = st.columns([1, 2, 1])

        with col_right:
        # Employee & Week Selection (manager can choose any employee they wish):
            employee_dict = self.storage.get_all_employees()
            st.subheader("👤 Employee Selection")
            selected_employee = st.selectbox("Select An Employee",
                                             options=employee_dict.values(),
                                             format_func=lambda emp: f"{emp.name} (ID: {emp.employee_id})")

            st.subheader("🕰️ Week Selection")
            selected_week = st.selectbox("Select A Week Number",
                                         options=range(1, 53),
                                         format_func=lambda week: f"Week: {week}"
                                         )
            curr_year = str(datetime.now().year)
            week_id = f'{curr_year}-W{selected_week}'

            st.write(f"Selected Employee: {selected_employee.name}")
            st.write(f"Selected Week: {selected_week}")

            st.divider()

        with col_left:
            if st.session_state.get("add_flash_msg"):
                st.success(st.session_state.add_flash_msg)
                st.session_state.add_flash_msg = None

            if st.button("✚ Add Task", width="stretch"):
                self._add_task_for_employee(selected_employee)
            if st.button("⊖ Remove Task", width="stretch"):
                self._remove_task_for_employee(selected_employee)
            if st.button("📝 Edit Task", width="stretch"):
                self._edit_task_for_employee(selected_employee)

        with col_mid:
            st.subheader("📊 Burnout Analysis Report")
            report = self.analysis.deliver_report(selected_employee, week_id, 'week')

            if report == "Insufficient data for a report.":
                st.warning(report)
            else:

                week_start = datetime.fromisocalendar(int(curr_year), selected_week, 1)
                week_end = week_start + timedelta(days=4)
                st.info(f"Timeframe: Start: {week_start.date()} | End: {week_end.date()}")
                st.info(report)

                mood_vals = self.analysis._get_mood_vals(week_id, selected_employee, 'week')
                task_comp_vals = self.analysis._get_task_completed_expected_ratio(week_id, selected_employee, 'week')
                scaled_completion = [comp * 10 for comp in task_comp_vals] # multiply comp ratios by 10 to match mood scaling
                data = {
                    "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    "Mood": mood_vals,
                    "Task Completion": scaled_completion,
                }

                df = pd.DataFrame(data)
                day_order = ["Mon", "Tue", "Wed", "Thu", "Fri"]

                df["Day"] = pd.Categorical(df["Day"], categories=day_order, ordered=True)

                df = df.sort_values("Day").set_index("Day")

                st.line_chart(df)

                state = self.analysis.develop_employee_state(selected_employee, week_id, 'week')

                STATE_DESCRIPTIONS = {
                    "Environment Conditions": {
                        "LM": "😕 Low Mood Baseline: Overall weekly mood stayed in the lower range (1–4).",
                        "MM": "🙂 Moderate Mood Baseline: Weekly mood remained stable in the mid-range (5–6).",
                        "HM": "😄 High Mood Baseline: Overall weekly mood remained elevated in the top range (7–10).",
                        "LC": "⬇️ Low Completion Rate: Task execution was low, staying below 50% on most days.",
                        "MC": "⬅️➡️ Moderate Completion Rate: Task execution fluctuated around the 50% mark.",
                        "HC": "⬆️ High Completion Rate: Task execution was strong, exceeding 50% on most days.",
                        "HW": "🏋️ High Task Importance: Average workload weight remained elevated this week.",
                        "MW": "⚖️ Moderate Task Importance: Workload weight stayed at a steady, balanced level.",
                        "LW": "🍃 Low Task Importance: Assigned workload weight was minimal this week.",
                        "HD": "🧠 High Task Difficulty: Assigned tasks carried high overall complexity this week.",
                        "MD": "🧩 Moderate Task Difficulty: Task complexity remained at a manageable baseline.",
                        "LD": "🌱 Low Task Difficulty: Assigned tasks carried minimal complexity this week.",
                    },
                    "Volatility Condition": {
                        "HV": "⚡ High Volatility: Metric fluctuated significantly with large day-to-day shifts.",
                        "MV": "〰️ Moderate Volatility: Metric fluctuated within a predictable, consistent range.",
                        "LV": "🧘 Low Volatility: Metric remained highly stable with little to no daily variance.",
                    },
                    "Internal Direction Condition": {  # Mood & Task Completion
                        "UP": "📈 Upward Trend: Metric improved steadily across the week, indicating positive momentum.",
                        "FLAT": "➡️ Steady Baseline: Metric remained flat throughout the week with no major shifts.",
                        "DOWN": "📉 Downward Trend: Metric declined steadily across the week, indicating negative drift.",
                    },
                    "External Direction Condition": {  # Task Weight & Difficulty
                        "UP": "📈 Escalating Workload: Metric increased across the week, indicating rising workload pressure.",
                        "FLAT": "➡️ Steady Workload: Metric remained flat throughout the week with no major shifts.",
                        "DOWN": "📉 Easing Workload: Metric decreased across the week, indicating a release in workload pressure.",
                    },
                }

                st.info("METRIC ANALYSIS: ")
                if st.button("🌎View Metric Environments: "):
                    st.info(f"MOOD: {STATE_DESCRIPTIONS["Environment Conditions"][state[0][0]]}")
                    st.info(f"TASK COMPLETION: {STATE_DESCRIPTIONS["Environment Conditions"][state[1][0]]}")
                    st.info(f"TASK WEIGHT: {STATE_DESCRIPTIONS["Environment Conditions"][state[2][0]]}")
                    st.info(f"TASK DIFFICULTY: {STATE_DESCRIPTIONS["Environment Conditions"][state[3][0]]}")

                if st.button("🔃View Metric Volatility: "):
                    st.info(f"MOOD: {STATE_DESCRIPTIONS["Volatility Condition"][state[0][1]]}")
                    st.info(f"TASK COMPLETION: {STATE_DESCRIPTIONS["Volatility Condition"][state[1][1]]}")
                    st.info(f"TASK WEIGHT: {STATE_DESCRIPTIONS["Volatility Condition"][state[2][1]]}")
                    st.info(f"TASK DIFFICULTY: {STATE_DESCRIPTIONS["Volatility Condition"][state[3][1]]}")

                if st.button("📉📈View Metric Direction: "):
                    st.info(f"MOOD: {STATE_DESCRIPTIONS["Internal Direction Condition"][state[0][2]]}")
                    st.info(f"TASK COMPLETION: {STATE_DESCRIPTIONS["Internal Direction Condition"][state[1][2]]}")
                    st.info(f"TASK WEIGHT: {STATE_DESCRIPTIONS["External Direction Condition"][state[2][2]]}")
                    st.info(f"TASK DIFFICULTY: {STATE_DESCRIPTIONS["External Direction Condition"][state[3][2]]}")


                st.info("📥WEEKLY CONTEXT: ")
                if st.button("💼 Check Week's Tasks", use_container_width=True):
                    self._display_analysis_week_tasks(selected_employee, week_id)
                if st.button("🧠 Check Week's Moods", use_container_width=True):
                    self._display_analysis_week_moods(selected_employee, week_id)

    @st.dialog("✚ Add Task")
    def _add_task_for_employee(self, e: Employee):

        with st.form("add_task_form", clear_on_submit=True):
            chosen_name = st.text_input("Task Name: ")
            chosen_weight = st.slider("Task Weight (1 - 10): ", 1, 10, 5)
            chosen_difficulty = st.slider("Task Difficulty (1 - 10): ", 1, 10, 5)
            chosen_id = st.text_input("Task ID: ", placeholder="T1") # starting from most important being 1, manager's can designate tasks by importance via numbers
            chosen_date = str(datetime.now().date()) # tasks can only be added for current day
            submitted = st.form_submit_button("Submit Task", use_container_width=True)

            if submitted:
                if not chosen_name.strip():
                    st.error("🚨 Task name cannot be empty.")
                else:
                    new_task = Task(chosen_id, chosen_name, chosen_weight, chosen_difficulty, chosen_date, False)
                    # ^ status is defaulted to False
                    self.manager.add_task(new_task, e)
                    st.session_state.add_flash_msg = f"Task: {new_task.get_name()} added successfully!"
                    st.rerun()

    @st.dialog("⊖ Remove Task")
    def _remove_task_for_employee(self, e: Employee):
        curr_date = str(datetime.now().date())
        today_tasks = e.get_tasks_for_specific_date(curr_date)

        if "task_success_msg" in st.session_state:
            st.success(st.session_state.task_success_msg)
            del st.session_state.task_success_msg

        if today_tasks is None:
            st.write("No available tasks to remove for today.")
        else:
            with st.form("task_completion_form"):
                st.subheader(f"📋 Tasks for {curr_date}")

                # Dictionary to track which checkboxes get checked
                task_checks = {}

                for task in today_tasks:
                    label = (
                        f"**{task.name}** — "
                        f"Weight: {task.get_weight()}/10 | "
                        f"Difficulty: {task.get_difficulty()}/10 | "
                        f"Completed: {'Yes' if task.completed is True else 'No'}"
                    )
                    # Render a checkbox for each task
                    task_checks[task] = st.checkbox(label, key=f"chk_{task.name}")

                # 2. Single submit button for the entire form
                submitted = st.form_submit_button("Remove Tasks", use_container_width=True)

            # 3. Process the backend updates ONLY when the form is submitted
            if submitted:
                removed_count = 0
                for task, is_checked in task_checks.items():
                    if is_checked:
                        self.manager.remove_task(task.get_name(), e, task.get_date())  # Updates object & backend JSON
                        removed_count += 1

                if removed_count > 0:
                    st.session_state.flash_msg = f"✅ Successfully removed {removed_count} task(s)!"
                else:
                    st.session_state.flash_msg = "ℹ️ No tasks were removed."

                st.rerun()

            # Display persistent banner message after form rerun
        if "flash_msg" in st.session_state:
            st.success(st.session_state.flash_msg)
            del st.session_state.flash_msg

    @st.dialog("📝 Edit Task")
    def _edit_task_for_employee(self, e: Employee):
        curr_date = str(datetime.now().date())
        today_tasks = e.get_tasks_for_specific_date(curr_date)

        if "task_success_msg" in st.session_state:
            st.success(st.session_state.task_success_msg)
            del st.session_state.task_success_msg

        if today_tasks is None:
            st.write("No available tasks to change for today.")
        else:
            ...

# SOFTWARE EXECUTION:

st.set_page_config(layout="wide", page_title="Burnout Beacon")
#active_view1 = EmployeeView('10_employee_dataset.json')
active_view2 = ManagerView('10_employee_dataset.json')
#active_view1.render()
active_view2.render()
