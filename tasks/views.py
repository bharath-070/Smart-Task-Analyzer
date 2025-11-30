import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .scoring import calculate_score, detect_cycle, DependencyCycleError


@csrf_exempt
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    Accepts a JSON list of tasks.
    Returns the same list sorted by calculated score.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        tasks = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    # Detect circular dependencies
    graph = {}
    for t in tasks:
        graph[t.get("id")] = t.get("dependencies", [])

    try:
        detect_cycle(graph)
    except DependencyCycleError as e:
        return JsonResponse({"error": str(e)}, status=400)

    # Calculate scoring
    for t in tasks:
        t["score"] = calculate_score(t, tasks)

    # Sort by score (highest first)
    tasks = sorted(tasks, key=lambda x: x["score"], reverse=True)

    return JsonResponse(tasks, safe=False, status=200)


@csrf_exempt
def suggest_tasks(request):
    """
    GET /api/tasks/suggest/?tasks=[...]
    Returns top 3 tasks with explanations.
    """

    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    tasks_json = request.GET.get("tasks")
    if not tasks_json:
        return JsonResponse({"error": "Missing 'tasks' parameter"}, status=400)

    try:
        tasks = json.loads(tasks_json)
    except:
        return JsonResponse({"error": "Invalid tasks JSON"}, status=400)

    # Score each task
    for t in tasks:
        t["score"] = calculate_score(t, tasks)

    # Sort top 3
    top3 = sorted(tasks, key=lambda x: x["score"], reverse=True)[:3]

    # Add explanations
    for t in top3:
        explanation = []

        if t.get("importance", 0) >= 8:
            explanation.append("High importance task")

        if t.get("due_date"):
            explanation.append("Approaching or urgent deadline")

        if t.get("estimated_hours", 10) <= 2:
            explanation.append("Quick win (low effort)")

        if len(t.get("dependencies", [])) > 0:
            explanation.append("Task unlocks other work")

        t["explanation"] = explanation

    return JsonResponse(top3, safe=False, status=200)
