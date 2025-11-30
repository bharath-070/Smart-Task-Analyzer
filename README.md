# **`Smart Task Analyzer`** 

## 📌  **Overview** 

Smart Task Analyzer is a mini-application that accepts a list of tasks and automatically calculates their priority based on urgency, importance, effort, and dependencies.
It helps users understand what they should work on first.

### This project includes:

Python + Django backend <br>
HTML + CSS + Vanilla JS frontend <br>
Custom scoring algorithm <br>
Task suggestions <br>
Multiple sorting strategies <br>
Unit tests for scoring + API <br>

## 🛠️ Installation & Setup

### 1️⃣ Clone the repository

create a folder in the workspace
```
git clone https://github.com/bharath-070/Smart-Task-Analyzer.git
cd Smart-Task-Analyzer
```

### 2️⃣ Create & activate virtual environment

Windows:
```
python -m venv myenv
myenv\Scripts\activate
```

macOS/Linux:
```
python3 -m venv myenv
source myenv/bin/activate
```

### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```
### 4️⃣ Run Django server
```
python manage.py migrate
python manage.py runserver
```
Backend is now running on:

http://localhost:8000

### 5️⃣ Run the frontend

Open the frontend HTML file:<br>
> frontend/index.html <br>

If using VS Code Live Server → it runs at:

http://127.0.0.1:5500

## 🧪 Running Unit Tests

All tests are located in:

> tasks/tests.py

Run all tests using:
```
python manage.py test
```
## 🧠 Priority Scoring Algorithm 

The Smart Task Analyzer uses a weighted scoring model designed to mirror how real humans prioritize work. The algorithm focuses on four key factors—urgency, importance, effort, and dependencies—each contributing a different weight to the final score.

- **Urgency**

Urgency is derived from the due date. Tasks that are overdue automatically receive a very high urgency value (15), tasks due today receive 12, and tasks with future deadlines receive a decaying urgency score based on how many days remain. Tasks without any due date default to 0 urgency. This ensures time-critical items naturally rise to the top.

- **Importance**

Importance is a direct user-provided value from 1 to 10. It is treated as a major factor in the final score because high-impact work should not be overshadowed by trivial urgent tasks. This matches the behavior seen in real productivity frameworks like Eisenhower Matrix.

- **Effort (Quick Win Logic)**

Effort influences how easy a task is to complete. The logic favors “quick wins” by giving higher scores to tasks that require fewer hours. The formula 10 / (effort + 1) provides diminishing returns: very small tasks get a big boost, while large tasks barely affect score.

- **Dependencies**

Tasks that are blocking other tasks are more important. The algorithm assigns +3 points for each dependency, making upstream tasks more valuable.

- **Weighted Final Score**

The final formula combines these values using balanced weights:

score = (urgency * 0.4) 
      + (importance * 0.4)
      + (effort_score * 0.1)
      + (dependency_score * 0.1)


This creates the Smart Balance strategy used by default in the backend.

Other strategies (Fastest Wins, High Impact, Deadline Driven) are implemented in the frontend by re-sorting the list based on the selected preference.

## 🧩 Design Decisions

- **Kept the backend scoring algorithm simple**  
  Instead of making a highly complex configurable engine, I implemented a clean and understandable scoring function. This allowed me to focus on correctness and readability rather than tuning dozens of parameters.

- **Did not build models or database storage for tasks**  
  Since the assignment mainly required evaluating task priority, I used JSON-based interactions. This reduced setup complexity and made the API easier to test quickly. If this were a full product, storing tasks in SQLite or PostgreSQL would be essential.

- **Implemented alternative strategies (Fastest Wins, High Impact, Deadline Driven) in the frontend**  
  The backend already had “Smart Balance,” so I handled the other sorting strategies in JavaScript. This avoided duplicating logic on the server and kept backend code minimal.

- **Minimal UI, focused on clarity**  
  I avoided heavy styling libraries to keep things simple, readable, and easy to modify under time constraints.

## ⏱️  Time Breakdown

- **Backend Scoring Algorithm:** ~1 hour  
  Designing urgency logic, effort formula, dependency handling, and implementing final weighted score.

- **API Endpoints (analyze & suggest):** ~45 minutes  
  Handling JSON input, returning calculated results, formatting responses.

- **Frontend UI + Interactions:** ~2 hours
  Building task forms, task lists, sorting strategies, score explanations, color indicators.

- **Testing (Unit Tests):** ~30 minutes  
  Writing tests for scoring and cycle detection, verifying edge cases.

- **Debugging + CORS + UI adjustments:** ~30 minutes  
  Fixing CORS issues, updating layout, ensuring sorting strategies work.

- **README.md + Documentation:** ~20 minutes  
  Setup instructions, algorithm explanation, assumptions, design choices.

- **Total Time:** ~5 hours 5 minutes

## 🎁 Bonus Challenges Completed

I did not implement any optional bonus challenges due to time constraints.  
My focus was on meeting the core requirements with clean code and proper testing.

## 🎯 Future Improvements

- **Store tasks in a database**  
  Instead of sending JSON arrays every time, tasks could be persisted using SQLite/PostgreSQL.

- **Add authentication**  
  Each user could save their tasks and get personalized suggestions.

- **Improve the scoring algorithm**  
  Could introduce machine learning or reinforcement learning where the system learns user behavior.

- **Add task categories or tags**  
  Priority could be influenced by task type (e.g., work, study, urgent personal tasks).

- **UI enhancements**  
  Better dashboard layout, drag-drop sorting, charts, timeline view.

- **Dependency visualization**  
  A graph-based UI view of task dependencies.

- **Recurring tasks & reminders**  
  Extend functionality to support scheduling and reminders.
