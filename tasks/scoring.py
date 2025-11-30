from datetime import date


def calculate_task_score(task_data):
    """
    Calculates a priority score.
    Higher score = Higher priority.
    """
    score = 0

    # 1. Urgency Calculation
    today = date.today()
    # Convert string date to object if necessary...
    days_until_due = (task_data['due_date'] - today).days

    if days_until_due < 0:
        score += 100  # OVERDUE! Huge priority boost
    elif days_until_due <= 3:
        score += 50   # Due very soon

    # 2. Importance Weighting
    score += (task_data['importance'] * 5) # Multiply to give it weight

    # 3. Effort (Quick wins logic)
    if task_data['estimated_hours'] < 2:
        score += 10 # Small bonus for quick tasks

    return score
