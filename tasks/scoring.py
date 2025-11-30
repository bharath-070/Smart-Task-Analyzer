from datetime import date

class DependencyCycleError(Exception):
    pass

#Detecting circular dependancy
def detect_cycle(graph):
    visited = set()
    stack = set()

    def dfs(node):
        if node in stack:
            raise DependencyCycleError("Circular dependency detected")
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nxt in graph.get(node, []):
            dfs(nxt)
        stack.remove(node)

    for task in graph:
        dfs(task)


def calculate_score(task, all_tasks):
    # --- URGENCY ---
    if not task.get("due_date"):
        urgency = 0
    else:
        due = date.fromisoformat(task["due_date"])
        days_left = (due - date.today()).days
        if days_left < 0:
            urgency = 15  # high penalty for overdue
        elif days_left == 0:
            urgency = 12
        else:
            urgency = max(0, 10 - days_left)

    # --- IMPORTANCE ---
    importance = task.get("importance", 5)

    # --- EFFORT ---
    effort = task.get("estimated_hours", 1)
    effort_score = 10 / (effort + 1)  # lower effort → higher score

    # --- DEPENDENCY WEIGHT ---
    dependency_count = len(task.get("dependencies", []))
    dependency_score = dependency_count * 3

    # FINAL SCORE (Smart Balanced)
    final_score = (urgency * 0.4) + (importance * 0.4) + (effort_score * 0.1) + (dependency_score * 0.1)
    return round(final_score, 2)
