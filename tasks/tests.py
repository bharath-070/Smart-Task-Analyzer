import json
from django.test import TestCase
from datetime import date, timedelta
from .scoring import calculate_score, detect_cycle, DependencyCycleError


class ScoringTests(TestCase):

    def test_no_due_date_gives_zero_urgency(self):
        """Tasks without a due date should have urgency = 0."""
        task = {
            "title": "Task",
            "due_date": None,
            "importance": 5,
            "estimated_hours": 2,
            "dependencies": []
        }
        score = calculate_score(task, [task])
        self.assertTrue(score < 5)

    def test_overdue_task_has_high_urgency(self):
        """Past-due tasks should have urgency = 15."""
        past_date = (date.today() - timedelta(days=3)).isoformat()
        task = {
            "title": "Late Task",
            "due_date": past_date,
            "importance": 5,
            "estimated_hours": 2,
            "dependencies": []
        }
        score = calculate_score(task, [task])
        self.assertTrue(score > 6)

    def test_deadline_today(self):
        """Due today should give urgency = 12."""
        today = date.today().isoformat()
        task = {
            "title": "Today Deadline",
            "due_date": today,
            "importance": 5,
            "estimated_hours": 2,
            "dependencies": []
        }
        score = calculate_score(task, [task])
        self.assertTrue(score > 4.8)

    def test_low_effort_quick_win(self):
        """Lower estimated hours should increase score."""
        fast = {
            "title": "Quick Task",
            "due_date": None,
            "importance": 5,
            "estimated_hours": 0,
            "dependencies": []
        }
        slow = {
            "title": "Slow Task",
            "due_date": None,
            "importance": 5,
            "estimated_hours": 10,
            "dependencies": []
        }
        fast_score = calculate_score(fast, [fast])
        slow_score = calculate_score(slow, [slow])
        self.assertTrue(fast_score > slow_score)

    def test_dependency_weight(self):
        """More dependencies should increase final score."""
        t1 = {
            "title": "T1",
            "due_date": None,
            "importance": 5,
            "estimated_hours": 2,
            "dependencies": ["x", "y"]
        }
        t2 = {
            "title": "T2",
            "due_date": None,
            "importance": 5,
            "estimated_hours": 2,
            "dependencies": []
        }
        self.assertTrue(calculate_score(t1, [t1, t2]) > calculate_score(t2, [t1, t2]))

    def test_circular_dependency_detection(self):
        """Detect cycles correctly."""
        graph = {"a": ["b"], "b": ["a"]}
        with self.assertRaises(DependencyCycleError):
            detect_cycle(graph)

    def test_no_cycle_valid_graph(self):
        """Valid graph should NOT raise cycle error."""
        graph = {"a": ["b"], "b": ["c"], "c": []}
        try:
            detect_cycle(graph)
        except DependencyCycleError:
            self.fail("Unexpected cycle error")




#Unit tests for API
class APITests(TestCase):

    def test_analyze_tasks_post(self):
        """POST /api/tasks/analyze/ → should return sorted tasks with scores."""
        url = "/api/tasks/analyze/"

        tasks = [
            {
                "id": "t1",
                "title": "Low Importance",
                "due_date": None,
                "estimated_hours": 5,
                "importance": 2,
                "dependencies": []
            },
            {
                "id": "t2",
                "title": "High Importance",
                "due_date": None,
                "estimated_hours": 3,
                "importance": 9,
                "dependencies": []
            }
        ]

        response = self.client.post(
            url,
            data=json.dumps(tasks),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        # The higher importance task should come first
        self.assertEqual(data[0]["title"], "High Importance")
        self.assertIn("score", data[0])

    def test_analyze_rejects_non_post(self):
        """GET on analyze should return 405."""
        response = self.client.get("/api/tasks/analyze/")
        self.assertEqual(response.status_code, 405)

    def test_analyze_detects_cycle(self):
        """Should detect circular dependencies."""
        url = "/api/tasks/analyze/"

        circular_tasks = [
            {"id": "a", "title": "A", "due_date": None, "estimated_hours": 1, "importance": 5, "dependencies": ["b"]},
            {"id": "b", "title": "B", "due_date": None, "estimated_hours": 1, "importance": 5, "dependencies": ["a"]}
        ]

        response = self.client.post(
            url,
            data=json.dumps(circular_tasks),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Circular", response.json()["error"])

    def test_suggest_tasks_top3(self):
        """GET /api/tasks/suggest/ should return top 3 tasks with explanations."""
        url = "/api/tasks/suggest/"

        future = (date.today() + timedelta(days=1)).isoformat()

        tasks = [
            {"id": "t1", "title": "High Importance", "importance": 10, "due_date": future, "estimated_hours": 2, "dependencies": []},
            {"id": "t2", "title": "Medium Importance", "importance": 6, "due_date": None, "estimated_hours": 1, "dependencies": []},
            {"id": "t3", "title": "Low Importance", "importance": 3, "due_date": None, "estimated_hours": 8, "dependencies": []},
            {"id": "t4", "title": "Another High", "importance": 9, "due_date": None, "estimated_hours": 2, "dependencies": []}
        ]

        response = self.client.get(
            url + "?tasks=" + json.dumps(tasks)
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Should return only top 3
        self.assertEqual(len(data), 3)
        # Each task must have an explanation list
        self.assertTrue("explanation" in data[0])

    def test_suggest_rejects_non_get(self):
        """POST on suggest should return 405."""
        response = self.client.post("/api/tasks/suggest/")
        self.assertEqual(response.status_code, 405)

    def test_suggest_requires_tasks_param(self):
        """Should return error when ?tasks= parameter is missing."""
        response = self.client.get("/api/tasks/suggest/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing", response.json()["error"])
