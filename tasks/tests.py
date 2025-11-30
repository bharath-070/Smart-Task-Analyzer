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
