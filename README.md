# 🕯️ Burnout Beacon

**Burnout Beacon** is a technical, interactive workforce diagnostic dashboard designed to monitor employee sentiment, workload difficulty, and completion metrics to identify burnout risks before they impact teams. 

Built with an **Object-Oriented Programming (OOP)** architecture in Python, the application evaluates time-series employee metrics—tracking trend direction, volatility, and baseline environmental shifts—to deliver actionable diagnostic insights.

---

## 🌟 Key Features

* **📊 Time-Series Metric Evaluation:** Analyzes multi-week employee datasets across three core dimensions:
  * **Environment Baseline:** Categorizes baseline mood (LM/MM/HM), task completion (LC/MC/HC), and workload pressure (HW/HD).
  * **Volatility Tracking:** Measures metric stability (HV/MV/LV) to spot abrupt shifts in employee well-being.
  * **Directional Trends:** Tracks upward, flat, or downward trajectory (UP/FLAT/DOWN) in completion vs. difficulty.
* **🔒 Role-Gated Authentication:** Lightweight per-employee ID verification gated via `st.session_state` to secure sensitive diagnostic reports during multi-user profile switching.
* **📈 Interactive Visualizations:** Dynamic line chart comparisons mapping Mood vs. Completion, Completion vs. Difficulty, and Task Weight over custom week ranges.
* **🎭 Real-Time Mood Logging:** Daily sentiment submission form with instant feedback and historical trend logging.
* **📁 Portable Local Persistence:** Engineered file storage layer reading/writing JSON datasets cleanly without external database overhead.

---

## 🏗️ System Architecture & Tech Stack

### Tech Stack:
* **Language:** Python 3.10+
* **Frontend UI:** Streamlit
* **Data Processing & Analytics:** Custom Python Time-Series Logic, `datetime`
* **Data Persistence:** JSON via `pathlib`
* **Branding & Assets:** SVG Integration

### Object-Oriented Design (OOP)
The codebase enforces strict separation of concerns through an OOP architecture of classes and leverages composition, inheritance & abstraction:

* **Employee**: The employee class represents an employee within the system, storing key information such as name, id, and most importantly, the employee's mood and history over time. This class also covers the task completion feature.

* **Manager**: The manager class represents the abilities of a manager within the system such as adding, removing and editing the tasks of other employees.

* **Task**: The task class represents a task with qualities such as its id, name, weight, difficulty, and completion status.

* **Storage**: The storage class acts as a container which encompasses all employees and their catalogue of information that are stored within the JSON database as proper objects.

* **Loader**: The loader class deals with reading in the JSON database and constructing employee and task objects accordingly, along with manipulating the database when a manager wants to make changes to an employee's tasks.

* **Analysis**: The analysis class is where the bulk of the project happens, as all statistical calculations, score generation and case-matching occur in this class and are constructed together to develop an employee's burnout report.

* **Interface**: The interface class deals with the frontend of the project and is developed in Streamlit. The EmployeeView and ManagerView subclasses revolve around the distinct interfaces of both roles respectively. 
